"""
Script to test Confidence Calculation, Escalation, Resolution, and Multi-tenant Security.

TEST A — HIGH CONFIDENCE (Patagonia doc question)
TEST B — VERIFIED EXPERIENCE ("which company is being talked about in the doc")
TEST C — UNKNOWN QUESTION ("What is the population of Mars?")
         + Escalation listing, details, assignment, resolution & PENDING experience creation
TEST D — MULTI-TENANT SECURITY (Cross-company access blocked)
"""

import asyncio
import uuid
import httpx

from sqlalchemy import select
from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.company import Company
from app.models.conversation import Conversation, ConversationStatus
from app.models.escalation import Escalation, EscalationStatus
from app.models.experience import Experience, ExperienceVerificationStatus
from app.models.message import Message
from app.models.user import User, UserRole


async def run_confidence_and_escalation_tests():
    print("=" * 70)
    print("STARTING CONFIDENCE & ESCALATION INTEGRATION TESTS")
    print("=" * 70)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
        # Step 0: Ensure demo company & second company exist for multi-tenant testing
        async with AsyncSessionLocal() as db:
            comp_res = await db.execute(select(Company).where(Company.name == "AdaptiveAI Demo Company"))
            demo_comp = comp_res.scalar_one_or_none()
            assert demo_comp is not None, "Demo company not found"

            # Check/create customer user for demo company
            res = await db.execute(select(User).where(User.email == "customer@adaptiveai-demo.com"))
            customer_user = res.scalar_one_or_none()
            if not customer_user:
                customer_user = User(
                    company_id=demo_comp.id,
                    email="customer@adaptiveai-demo.com",
                    hashed_password=hash_password("Customer123!"),
                    full_name="Demo Customer",
                    role=UserRole.CUSTOMER,
                    is_active=True,
                    is_verified=True,
                )
                db.add(customer_user)

            # Check/create Company B for multi-tenant isolation testing
            res_b = await db.execute(select(Company).where(Company.name == "Tenant B Corp"))
            tenant_b = res_b.scalar_one_or_none()
            if not tenant_b:
                tenant_b = Company(name="Tenant B Corp", slug="tenant-b-corp", website="https://tenantb.com")
                db.add(tenant_b)
                await db.flush()

            # Check/create Company B Admin
            res_admin_b = await db.execute(select(User).where(User.email == "admin@tenantb.com"))
            admin_b = res_admin_b.scalar_one_or_none()
            if not admin_b:
                admin_b = User(
                    company_id=tenant_b.id,
                    email="admin@tenantb.com",
                    hashed_password=hash_password("TenantBAdmin123!"),
                    full_name="Tenant B Admin",
                    role=UserRole.COMPANY_ADMIN,
                    is_active=True,
                    is_verified=True,
                )
                db.add(admin_b)

            await db.commit()

        # Step 1: Login as Demo Admin
        admin_login = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@adaptiveai-demo.com", "password": "DemoAdmin123!"}
        )
        assert admin_login.status_code == 200, f"Demo Admin login failed: {admin_login.text}"
        demo_admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        # Step 2: Login as Demo Customer
        cust_login = await client.post(
            "/api/v1/auth/login",
            data={"username": "customer@adaptiveai-demo.com", "password": "Customer123!"}
        )
        assert cust_login.status_code == 200, f"Demo Customer login failed: {cust_login.text}"
        demo_cust_headers = {"Authorization": f"Bearer {cust_login.json()['access_token']}"}

        # Step 3: Login as Tenant B Admin
        b_login = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@tenantb.com", "password": "TenantBAdmin123!"}
        )
        assert b_login.status_code == 200, f"Tenant B Admin login failed: {b_login.text}"
        tenant_b_headers = {"Authorization": f"Bearer {b_login.json()['access_token']}"}
        print("Logins successful for Demo Admin, Demo Customer, and Tenant B Admin.")

        # =========================================================================
        # TEST A — HIGH CONFIDENCE (Patagonia doc question)
        # =========================================================================
        print("\n" + "=" * 60)
        print("TEST A: High-Confidence Question from Patagonia Doc")
        print("=" * 60)
        q_high = "What primary materials does Patagonia use in its clothing?"
        resp_a = await client.post(
            "/api/v1/chat/",
            headers=demo_cust_headers,
            json={"message": q_high}
        )
        assert resp_a.status_code == 200, f"Chat failed: {resp_a.text}"
        data_a = resp_a.json()
        print(f"Question: {q_high}")
        print(f"Answer: {data_a['answer'][:120]}...")
        print(f"Confidence score: {data_a.get('confidence_score')}")
        print(f"Is escalated: {data_a.get('is_escalated')}")
        print(f"Retrieved chunks: {data_a.get('retrieved_chunks')}")
        print(f"Sources count: {len(data_a.get('sources', []))}")

        assert data_a["is_escalated"] is False, "Expected is_escalated to be False"
        assert data_a["confidence_score"] is not None and data_a["confidence_score"] >= 0.70, (
            f"Expected confidence_score >= 0.70, got {data_a.get('confidence_score')}"
        )
        assert len(data_a["sources"]) > 0, "Expected sources to be present"
        conv_id_a = data_a["conversation_id"]

        # Verify conversation state in DB
        async with AsyncSessionLocal() as db:
            conv = await db.get(Conversation, uuid.UUID(conv_id_a))
            assert conv is not None
            assert conv.status == ConversationStatus.ACTIVE, f"Expected ACTIVE status, got {conv.status}"
            # Check message
            msg = await db.get(Message, uuid.UUID(data_a["assistant_message_id"]))
            assert msg is not None
            assert msg.confidence_score == data_a["confidence_score"]
            assert msg.is_escalated is False
        print("PASSED TEST A: High confidence answer generated, conversation remains ACTIVE, confidence_score stored.")

        # =========================================================================
        # TEST B — VERIFIED EXPERIENCE ("which company is being talked about in the doc")
        # =========================================================================
        print("\n" + "=" * 60)
        print("TEST B: Verified Experience Retrieval")
        print("=" * 60)
        q_exp = "which company is being talked about in the doc"
        resp_b = await client.post(
            "/api/v1/chat/",
            headers=demo_cust_headers,
            json={"message": q_exp}
        )
        assert resp_b.status_code == 200, f"Chat failed: {resp_b.text}"
        data_b = resp_b.json()
        print(f"Question: {q_exp}")
        print(f"Answer: {data_b['answer']}")
        print(f"Confidence score: {data_b.get('confidence_score')}")
        print(f"Retrieved experiences: {data_b.get('retrieved_experiences')}")
        print(f"Sources: {data_b.get('sources')}")

        assert data_b["is_escalated"] is False
        assert data_b.get("retrieved_experiences", 0) >= 1, "Expected at least 1 retrieved experience"
        assert any(s.get("type") == "verified_experience" for s in data_b.get("sources", [])), (
            "Expected verified_experience in sources"
        )
        assert data_b["confidence_score"] >= 0.80, (
            f"Expected high confidence for verified experience, got {data_b.get('confidence_score')}"
        )
        print("PASSED TEST B: Verified Experience retrieved, high confidence, correction prioritized.")

        # =========================================================================
        # TEST C — UNKNOWN QUESTION ("What is the population of Mars?")
        # =========================================================================
        print("\n" + "=" * 60)
        print("TEST C: Unknown Question -> Low Confidence -> Escalation")
        print("=" * 60)
        q_unknown = "What is the population of Mars?"
        resp_c = await client.post(
            "/api/v1/chat/",
            headers=demo_cust_headers,
            json={"message": q_unknown}
        )
        assert resp_c.status_code == 200, f"Chat failed: {resp_c.text}"
        data_c = resp_c.json()
        print(f"Question: {q_unknown}")
        print(f"Answer: {data_c['answer']}")
        print(f"Confidence score: {data_c.get('confidence_score')}")
        print(f"Is escalated: {data_c.get('is_escalated')}")
        print(f"Escalation ID: {data_c.get('escalation_id')}")

        assert data_c["is_escalated"] is True, "Expected is_escalated to be True"
        assert data_c["confidence_score"] < 0.50, f"Expected confidence < 0.50, got {data_c.get('confidence_score')}"
        assert "escalated" in data_c["answer"].lower(), "Expected escalation notice in answer"
        assert data_c.get("escalation_id") is not None, "Expected escalation_id in response"
        escalation_id = data_c["escalation_id"]
        conv_id_c = data_c["conversation_id"]

        # Check DB conversation status & escalation record
        async with AsyncSessionLocal() as db:
            conv = await db.get(Conversation, uuid.UUID(conv_id_c))
            assert conv is not None
            assert conv.status == ConversationStatus.ESCALATED, f"Expected ESCALATED status, got {conv.status}"
            assert conv.escalated_at is not None

            esc = await db.get(Escalation, uuid.UUID(escalation_id))
            assert esc is not None
            assert esc.status == EscalationStatus.OPEN
            assert esc.reason.value == "LOW_CONFIDENCE"
            assert esc.triggering_message_id == uuid.UUID(data_c["assistant_message_id"])

        print("PASSED TEST C1: Low confidence detected, conversation marked ESCALATED, Escalation record created.")

        # TEST C2: Admin lists escalations
        print("\n--- TEST C2: Admin lists escalations ---")
        list_esc_resp = await client.get("/api/v1/escalations/", headers=demo_admin_headers)
        assert list_esc_resp.status_code == 200
        esc_list = list_esc_resp.json()
        matching_esc = next((e for e in esc_list if e["id"] == escalation_id), None)
        assert matching_esc is not None, "Created escalation not found in admin list"
        print(f"Found escalation in list: id={matching_esc['id']}, status={matching_esc['status']}, reason={matching_esc['reason']}")
        print(f"Customer Question in escalation: {matching_esc['customer_question']}")
        assert matching_esc["customer_question"] == q_unknown

        # TEST C3: Customer cannot list escalations (403)
        cust_esc_resp = await client.get("/api/v1/escalations/", headers=demo_cust_headers)
        assert cust_esc_resp.status_code == 403, f"Expected 403 for customer, got {cust_esc_resp.status_code}"
        print("Verified customer gets 403 on escalation list.")

        # TEST C4: Get escalation details
        print("\n--- TEST C4: Get escalation details with conversation history ---")
        detail_resp = await client.get(f"/api/v1/escalations/{escalation_id}", headers=demo_admin_headers)
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()
        assert detail_data["id"] == escalation_id
        assert detail_data["status"] == "OPEN"
        assert len(detail_data.get("conversation_history", [])) >= 2
        print(f"Detail history length: {len(detail_data['conversation_history'])}")

        # TEST C5: Assign escalation
        print("\n--- TEST C5: Assign escalation to Admin ---")
        assign_resp = await client.put(f"/api/v1/escalations/{escalation_id}/assign", headers=demo_admin_headers)
        assert assign_resp.status_code == 200
        assign_data = assign_resp.json()
        print(f"Assigned status: {assign_data['status']}")
        print(f"Assigned agent ID: {assign_data['assigned_agent_id']}")
        assert assign_data["status"] == "IN_PROGRESS"
        assert assign_data["assigned_agent_id"] is not None

        # TEST C6: Resolve escalation with human resolution -> Creates PENDING Experience
        print("\n--- TEST C6: Resolve escalation and verify PENDING Experience ---")
        resolution_text = "Mars currently has an active population of 0 permanent human residents, though robotic rovers are operational."
        resolve_resp = await client.put(
            f"/api/v1/escalations/{escalation_id}/resolve",
            headers=demo_admin_headers,
            json={
                "resolution_notes": resolution_text,
                "create_experience": True
            }
        )
        assert resolve_resp.status_code == 200
        resolve_data = resolve_resp.json()
        print(f"Resolved status: {resolve_data['status']}")
        print(f"Resolution notes: {resolve_data['resolution_notes']}")
        print(f"Experience created: {resolve_data['experience_created']}")
        print(f"Experience ID: {resolve_data['experience_id']}")
        assert resolve_data["status"] == "RESOLVED"
        assert resolve_data["experience_created"] is True
        created_exp_id = resolve_data["experience_id"]

        # Verify the created Experience is in PENDING state
        exp_check_resp = await client.get(f"/api/v1/experiences/{created_exp_id}", headers=demo_admin_headers)
        assert exp_check_resp.status_code == 200
        exp_data = exp_check_resp.json()
        print(f"Experience Verification Status: {exp_data['verification_status']}")
        print(f"Experience Question: {exp_data['question']}")
        print(f"Experience Corrected Answer: {exp_data['corrected_answer']}")
        assert exp_data["verification_status"] == "PENDING"
        assert exp_data["has_embedding"] is False
        assert exp_data["corrected_answer"] == resolution_text

        print("PASSED TEST C: Full escalation lifecycle tested successfully (Open -> In Progress -> Resolved -> PENDING Experience).")

        # =========================================================================
        # TEST D — MULTI-TENANT SECURITY
        # =========================================================================
        print("\n" + "=" * 60)
        print("TEST D: Multi-Tenant Security Isolation")
        print("=" * 60)
        # Tenant B Admin attempts to view Demo Company's escalation
        cross_get = await client.get(f"/api/v1/escalations/{escalation_id}", headers=tenant_b_headers)
        assert cross_get.status_code == 404, f"Expected 404 for cross-tenant escalation, got {cross_get.status_code}"
        print("Tenant B cannot GET Demo Company's escalation (404 Not Found).")

        # Tenant B Admin attempts to resolve Demo Company's escalation
        cross_resolve = await client.put(
            f"/api/v1/escalations/{escalation_id}/resolve",
            headers=tenant_b_headers,
            json={"resolution_notes": "Hacked resolution"}
        )
        assert cross_resolve.status_code == 404, f"Expected 404 for cross-tenant resolve, got {cross_resolve.status_code}"
        print("Tenant B cannot RESOLVE Demo Company's escalation (404 Not Found).")

        # Tenant B list escalations does not include Demo Company's escalation
        b_list_resp = await client.get("/api/v1/escalations/", headers=tenant_b_headers)
        assert b_list_resp.status_code == 200
        b_list = b_list_resp.json()
        assert not any(e["id"] == escalation_id for e in b_list), "Tenant B list leaked Demo Company escalation!"
        print("Tenant B escalation list is completely isolated (0 leaked escalations).")

        print("PASSED TEST D: Multi-tenant security isolation verified across all escalation endpoints.")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_confidence_and_escalation_tests())
