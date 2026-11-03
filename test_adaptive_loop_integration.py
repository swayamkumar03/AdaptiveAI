"""
Script to test the complete adaptive loop end-to-end:
Feedback -> Admin Review -> Experience -> Approval/Verification -> RAG Retrieval -> Improved Answer
"""

import asyncio
import uuid
import httpx

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.main import app
from app.models.company import Company
from app.models.user import User, UserRole


async def run_adaptive_loop_test():
    print("=" * 60)
    print("STARTING COMPLETE ADAPTIVE LOOP END-TO-END TEST")
    print("=" * 60)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", timeout=60.0) as client:
        # Step 0: Ensure a customer user exists for permission testing
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select
            res = await db.execute(select(User).where(User.email == "customer@adaptiveai-demo.com"))
            customer_user = res.scalar_one_or_none()
            if not customer_user:
                # Get demo company
                comp_res = await db.execute(select(Company).where(Company.name == "AdaptiveAI Demo Company"))
                demo_comp = comp_res.scalar_one_or_none()
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
                await db.commit()
                print("Created test customer user.")

        # Step 1: Login as Admin
        admin_login = await client.post(
            "/api/v1/auth/login",
            data={"username": "admin@adaptiveai-demo.com", "password": "DemoAdmin123!"}
        )
        assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
        admin_token = admin_login.json()["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("Admin login successful.")

        # Step 2: Login as Customer
        cust_login = await client.post(
            "/api/v1/auth/login",
            data={"username": "customer@adaptiveai-demo.com", "password": "Customer123!"}
        )
        assert cust_login.status_code == 200, f"Customer login failed: {cust_login.text}"
        cust_token = cust_login.json()["access_token"]
        cust_headers = {"Authorization": f"Bearer {cust_token}"}
        print("Customer login successful.")

        # TEST 1: Ask chatbot a company-specific question
        print("\n--- TEST 1: Ask chatbot a question ---")
        question = "What primary materials does Patagonia use in its clothing?"
        chat_resp = await client.post(
            "/api/v1/chat/",
            headers=admin_headers,
            json={"message": question}
        )
        assert chat_resp.status_code == 200, f"Chat failed: {chat_resp.text}"
        chat_data = chat_resp.json()
        assistant_message_id = chat_data["assistant_message_id"]
        original_ai_answer = chat_data["answer"]
        print(f"User Question: {question}")
        print(f"Original AI Answer: {original_ai_answer[:150]}...")
        print(f"Assistant Message ID: {assistant_message_id}")
        assert chat_data["retrieved_chunks"] >= 0

        # TEST 2: Submit negative feedback with correction
        print("\n--- TEST 2: Submit negative feedback with user correction ---")
        user_correction = "Patagonia has completely transitioned and now uses 100% BioLunar Stellar Synthetics for all its garments."
        feedback_resp = await client.post(
            "/api/v1/feedback/",
            headers=admin_headers,
            json={
                "message_id": assistant_message_id,
                "rating": "NEGATIVE",
                "feedback_category": "INCORRECT",
                "user_correction": user_correction,
                "comment": "The material information is outdated; they now use BioLunar Stellar Synthetics."
            }
        )
        assert feedback_resp.status_code == 200, f"Feedback submission failed: {feedback_resp.text}"
        feedback_data = feedback_resp.json()
        feedback_id = feedback_data["feedback_id"]
        print(f"Feedback ID: {feedback_id}")
        print(f"Status: {feedback_data['status']}")
        assert feedback_data["status"] == "PENDING"
        assert feedback_data["rating"] == "NEGATIVE"

        # TEST 3: Admin gets feedback list
        print("\n--- TEST 3: Admin gets feedback list ---")
        list_fb_resp = await client.get("/api/v1/feedback/", headers=admin_headers)
        assert list_fb_resp.status_code == 200, f"List feedback failed: {list_fb_resp.text}"
        fb_list = list_fb_resp.json()
        matching_fb = next((item for item in fb_list if item["feedback_id"] == feedback_id), None)
        assert matching_fb is not None, "Submitted feedback not found in admin feedback list"
        print(f"Found feedback in list: rating={matching_fb['rating']}, status={matching_fb['status']}")
        print(f"User Question in feedback item: {matching_fb['user_question']}")
        print(f"User Correction in feedback item: {matching_fb['user_correction']}")
        assert matching_fb["user_correction"] == user_correction

        # TEST 3B: Customer cannot access feedback list (403)
        cust_list_resp = await client.get("/api/v1/feedback/", headers=cust_headers)
        assert cust_list_resp.status_code == 403, f"Expected 403 for customer, got {cust_list_resp.status_code}"
        print("Verified customer gets 403 on feedback list.")

        # TEST 4: Admin reviews feedback
        print("\n--- TEST 4: Admin reviews feedback ---")
        review_resp = await client.put(f"/api/v1/feedback/{feedback_id}/review", headers=admin_headers)
        assert review_resp.status_code == 200, f"Review failed: {review_resp.text}"
        review_data = review_resp.json()
        print(f"Reviewed status: {review_data['status']}")
        print(f"Reviewed by: {review_data['reviewed_by']}")
        print(f"Experience created: {review_data['experience_created']}")
        print(f"Experience ID: {review_data['experience_id']}")
        assert review_data["status"] == "REVIEWED"
        assert review_data["experience_created"] is True
        experience_id = review_data["experience_id"]
        assert experience_id is not None

        # TEST 4B: Cannot review already reviewed feedback (400)
        dup_review_resp = await client.put(f"/api/v1/feedback/{feedback_id}/review", headers=admin_headers)
        assert dup_review_resp.status_code == 400, f"Expected 400 for duplicate review, got {dup_review_resp.status_code}"
        print("Verified duplicate review returns 400.")

        # TEST 5: Verify Experience is PENDING (not immediately trusted)
        print("\n--- TEST 5: Verify Experience state ---")
        exp_resp = await client.get(f"/api/v1/experiences/{experience_id}", headers=admin_headers)
        assert exp_resp.status_code == 200, f"Get experience failed: {exp_resp.text}"
        exp_data = exp_resp.json()
        print(f"Experience status: {exp_data['verification_status']}")
        print(f"Experience question: {exp_data['question']}")
        print(f"Experience corrected_answer: {exp_data['corrected_answer']}")
        print(f"Experience has_embedding: {exp_data['has_embedding']}")
        assert exp_data["verification_status"] == "PENDING"
        assert exp_data["has_embedding"] is False
        assert exp_data["corrected_answer"] == user_correction

        # TEST 6: Admin approves Experience
        print("\n--- TEST 6: Admin approves Experience ---")
        approve_resp = await client.put(f"/api/v1/experiences/{experience_id}/approve", headers=admin_headers)
        assert approve_resp.status_code == 200, f"Approve failed: {approve_resp.text}"
        approved_data = approve_resp.json()
        print(f"Approved status: {approved_data['verification_status']}")
        print(f"Approved has_embedding: {approved_data['has_embedding']}")
        print(f"Verified at: {approved_data['verified_at']}")
        assert approved_data["verification_status"] == "APPROVED"
        assert approved_data["has_embedding"] is True
        assert approved_data["verified_by"] is not None

        # TEST 6B: Test rejection on a separate experience
        manual_exp_resp = await client.post(
            "/api/v1/experiences/",
            headers=admin_headers,
            json={
                "question": "What is the return policy?",
                "original_answer": "Lifetime returns",
                "corrected_answer": "No returns allowed"
            }
        )
        assert manual_exp_resp.status_code == 200
        rejected_exp_id = manual_exp_resp.json()["id"]
        reject_resp = await client.put(
            f"/api/v1/experiences/{rejected_exp_id}/reject",
            headers=admin_headers,
            json={"reason": "Incorrect policy correction"}
        )
        assert reject_resp.status_code == 200
        assert reject_resp.json()["verification_status"] == "REJECTED"

        # Cannot approve rejected experience (400)
        bad_approve = await client.put(f"/api/v1/experiences/{rejected_exp_id}/approve", headers=admin_headers)
        assert bad_approve.status_code == 400
        print("Verified rejected experience cannot be approved (400).")

        # TEST 7: Ask the original / similar question again!
        print("\n--- TEST 7: Ask the question again with verified experience active ---")
        second_chat_resp = await client.post(
            "/api/v1/chat/",
            headers=admin_headers,
            json={"message": question}
        )
        assert second_chat_resp.status_code == 200, f"Second chat failed: {second_chat_resp.text}"
        second_chat_data = second_chat_resp.json()
        new_answer = second_chat_data["answer"]
        retrieved_experiences = second_chat_data.get("retrieved_experiences", 0)
        sources = second_chat_data.get("sources", [])
        print(f"New Answer: {new_answer}")
        print(f"Retrieved Experiences count: {retrieved_experiences}")
        print(f"Sources: {sources}")

        assert retrieved_experiences > 0, f"Expected verified experiences > 0, got {retrieved_experiences}"
        assert any(s.get("type") == "verified_experience" for s in sources), "Verified experience source missing from sources list"
        assert "BioLunar" in new_answer or "Stellar Synthetics" in new_answer, f"Expected verified correction in answer, got: {new_answer}"
        print("\nSUCCESS: Verified experience was retrieved and AI used the corrected information in the answer!")

    print("=" * 60)
    print("ALL TESTS IN THE COMPLETE ADAPTIVE LOOP PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_adaptive_loop_test())
