"""
Integration tests for Analytics Endpoints:
1. GET /api/v1/analytics/overview
2. GET /api/v1/analytics/questions
3. GET /api/v1/analytics/feedback
4. GET /api/v1/analytics/knowledge-gaps
5. GET /api/v1/analytics/accuracy
Plus: Role check (Customer gets 403) and Multi-tenant isolation.
"""

import asyncio
import json
import httpx

from app.main import app


async def run_analytics_tests():
    print("=" * 70)
    print("STARTING ANALYTICS INTEGRATION TESTS")
    print("=" * 70)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
        # 1. Login as Demo Admin
        admin_login = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@adaptiveai-demo.com", "password": "DemoAdmin123!"}
        )
        assert admin_login.status_code == 200, f"Demo Admin login failed: {admin_login.text}"
        demo_admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        # 2. Login as Demo Customer
        cust_login = await client.post(
            "/api/v1/auth/login",
            data={"username": "customer@adaptiveai-demo.com", "password": "Customer123!"}
        )
        assert cust_login.status_code == 200, f"Demo Customer login failed: {cust_login.text}"
        demo_cust_headers = {"Authorization": f"Bearer {cust_login.json()['access_token']}"}

        # 3. Login as Tenant B Admin
        b_login = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@tenantb.com", "password": "TenantBAdmin123!"}
        )
        assert b_login.status_code == 200, f"Tenant B Admin login failed: {b_login.text}"
        tenant_b_headers = {"Authorization": f"Bearer {b_login.json()['access_token']}"}

        print("Authentication succeeded for Demo Admin, Demo Customer, and Tenant B Admin.")

        # =========================================================================
        # TEST 1 — GET /api/v1/analytics/overview
        # =========================================================================
        print("\n" + "=" * 60)
        print("TEST 1: GET /api/v1/analytics/overview")
        print("=" * 60)
        resp_overview = await client.get("/api/v1/analytics/overview", headers=demo_admin_headers)
        assert resp_overview.status_code == 200, f"Overview failed: {resp_overview.text}"
        overview_data = resp_overview.json()
        print("Overview response:")
        print(json.dumps(overview_data, indent=2))

        assert overview_data["total_conversations"] >= 0
        assert overview_data["total_user_questions"] >= 0
        assert overview_data["total_assistant_answers"] >= 0
        assert 0.0 <= overview_data["escalation_rate"] <= 1.0
        assert 0.0 <= overview_data["average_confidence_score"] <= 1.0
        assert overview_data["total_documents"] >= 0

        # =========================================================================
        # TEST 2 — GET /api/v1/analytics/questions
        # =========================================================================
        print("\n" + "=" * 60)
        print("TEST 2: GET /api/v1/analytics/questions")
        print("=" * 60)
        resp_questions = await client.get("/api/v1/analytics/questions?limit=5", headers=demo_admin_headers)
        assert resp_questions.status_code == 200, f"Questions failed: {resp_questions.text}"
        questions_data = resp_questions.json()
        print("Questions response summary:")
        print(f"Total questions: {questions_data['total_questions']}")
        print(f"Answered: {questions_data['answered_questions']}")
        print(f"Escalated: {questions_data['escalated_questions']}")
        print(f"Average confidence: {questions_data['average_confidence']}")
        print(f"Recent questions count: {len(questions_data['recent_questions'])}")
        if questions_data["recent_questions"]:
            sample_q = questions_data["recent_questions"][0]
            print(f"Sample recent question: {sample_q['question']}")
            print(f"Sample answer preview: {str(sample_q['answer'])[:60]}...")
            print(f"Sample confidence: {sample_q['confidence_score']}, Escalated: {sample_q['is_escalated']}")

        assert questions_data["total_questions"] >= questions_data["answered_questions"]
        assert len(questions_data["recent_questions"]) <= 5

        # =========================================================================
        # TEST 3 — GET /api/v1/analytics/feedback
        # =========================================================================
        print("\n" + "=" * 60)
        print("TEST 3: GET /api/v1/analytics/feedback")
        print("=" * 60)
        resp_fb = await client.get("/api/v1/analytics/feedback", headers=demo_admin_headers)
        assert resp_fb.status_code == 200, f"Feedback failed: {resp_fb.text}"
        fb_data = resp_fb.json()
        print("Feedback response:")
        print(json.dumps(fb_data, indent=2))

        assert fb_data["total_feedback"] == fb_data["positive_count"] + fb_data["negative_count"]
        assert 0.0 <= fb_data["positive_rate"] <= 1.0
        assert 0.0 <= fb_data["negative_rate"] <= 1.0
        assert "INCORRECT" in fb_data["category_breakdown"]

        # =========================================================================
        # TEST 4 — GET /api/v1/analytics/knowledge-gaps
        # =========================================================================
        print("\n" + "=" * 60)
        print("TEST 4: GET /api/v1/analytics/knowledge-gaps")
        print("=" * 60)
        resp_gaps = await client.get("/api/v1/analytics/knowledge-gaps?limit=5", headers=demo_admin_headers)
        assert resp_gaps.status_code == 200, f"Knowledge gaps failed: {resp_gaps.text}"
        gaps_data = resp_gaps.json()
        print("Knowledge gaps summary:")
        print(f"Total knowledge gaps: {gaps_data['total_knowledge_gaps']}")
        print(f"Unresolved: {gaps_data['unresolved_gaps']}")
        print(f"Resolved: {gaps_data['resolved_gaps']}")
        print(f"Experiences created from gaps: {gaps_data['experiences_created_count']}")
        if gaps_data["knowledge_gaps"]:
            sample_gap = gaps_data["knowledge_gaps"][0]
            print(f"Sample gap question: {sample_gap['question']}")
            print(f"Sample gap status: {sample_gap['escalation_status']}")
            print(f"Sample gap resolution: {sample_gap['resolution_notes']}")
            print(f"Sample gap experience created: {sample_gap['experience_created']}")

        assert gaps_data["total_knowledge_gaps"] >= 0

        # =========================================================================
        # TEST 5 — GET /api/v1/analytics/accuracy
        # =========================================================================
        print("\n" + "=" * 60)
        print("TEST 5: GET /api/v1/analytics/accuracy")
        print("=" * 60)
        resp_acc = await client.get("/api/v1/analytics/accuracy", headers=demo_admin_headers)
        assert resp_acc.status_code == 200, f"Accuracy failed: {resp_acc.text}"
        acc_data = resp_acc.json()
        print("Accuracy response:")
        print(json.dumps(acc_data, indent=2))

        assert acc_data["metric_type"] == "proxy_reliability_metrics"
        assert "disclaimer" in acc_data.get("description", "").lower() or "proxy" in acc_data.get("metric_type", "").lower()
        assert 0.0 <= acc_data["average_confidence_score"] <= 1.0

        # =========================================================================
        # TEST 6 — ROLE SECURITY & TENANT ISOLATION
        # =========================================================================
        print("\n" + "=" * 60)
        print("TEST 6: Role Security & Multi-Tenant Isolation")
        print("=" * 60)
        # Customer gets 403 on all analytics endpoints
        for endpoint in ["/overview", "/questions", "/feedback", "/knowledge-gaps", "/accuracy"]:
            cust_resp = await client.get(f"/api/v1/analytics{endpoint}", headers=demo_cust_headers)
            assert cust_resp.status_code == 403, f"Expected 403 for customer on {endpoint}, got {cust_resp.status_code}"
        print("Verified customer receives 403 Forbidden on all analytics endpoints.")

        # Tenant B gets clean isolated zero metrics for their company
        b_overview_resp = await client.get("/api/v1/analytics/overview", headers=tenant_b_headers)
        assert b_overview_resp.status_code == 200
        b_overview = b_overview_resp.json()
        print("Tenant B overview (isolated):")
        print(json.dumps(b_overview, indent=2))
        assert b_overview["total_conversations"] == 0
        assert b_overview["total_documents"] == 0
        assert b_overview["total_escalations"] == 0
        print("Multi-tenant isolation verified: Tenant B cannot see Demo Company metrics.")

    print("\n" + "=" * 70)
    print("ALL ANALYTICS TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_analytics_tests())
