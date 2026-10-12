import os
import sys
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = r"C:\Users\prann\.gemini\antigravity\scratch\bms-platform\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.security import create_access_token
from services.ai_copilot_service.main import app, db_mgr, Base

def test_milestone3():
    print("--> Testing Milestone 3: Agentic Supervisor & Multi-Tool Chatbot...")
    db_mgr.init_tables(Base)
    client = TestClient(app)

    token = create_access_token({"sub": "user-exec-1", "user_id": "user-exec-1", "org_id": "org-acroflow-main", "role": "SUPER_ADMIN"})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test Pure Immediate Q&A Query (Track A Only)
    q1_resp = client.post(
        "/ai/chat",
        headers=headers,
        json={"message": "What is our current cash position and revenue?"}
    )
    assert q1_resp.status_code == 200, f"Expected 200, got {q1_resp.status_code}: {q1_resp.text}"
    data1 = q1_resp.json()
    assert data1["intent"] == "FINANCIAL_SYNTHESIS"
    assert "580,000.00" in data1["reply"]
    assert "1,540,950.00" in data1["reply"]
    assert data1["scheduled_task"] is None
    print("  [PASS] Track A Immediate Q&A verified: Instant financial synthesis without scheduled task")

    # 2. Test Dual-Track Query (Immediate Q&A + Background Temporal Scheduling with HITL)
    q2_resp = client.post(
        "/ai/chat",
        headers=headers,
        json={
            "message": "What's our cash flow? Also schedule a follow-up payment reminder to Acme Corp tomorrow at 10 AM, but ask me for approval before sending."
        }
    )
    assert q2_resp.status_code == 200
    data2 = q2_resp.json()
    assert data2["intent"] == "FINANCIAL_SYNTHESIS"
    assert "580,000.00" in data2["reply"]
    # Verify scheduled task is populated
    task_info = data2["scheduled_task"]
    assert task_info is not None
    assert task_info["target_service"] == "finance-service"
    assert task_info["requires_hitl"] is True
    assert "Human-in-the-Loop policy is active" in data2["reply"]
    print(f"  [PASS] Dual-Track verified: Immediate financial response + Background Task scheduled ({task_info['task_name']}) with HITL={task_info['requires_hitl']}")

    # 3. Test Sprint & Operations Chat Query
    q3_resp = client.post(
        "/ai/chat",
        headers=headers,
        json={"message": "What is blocked on Sprint 44 right now?"}
    )
    assert q3_resp.status_code == 200
    data3 = q3_resp.json()
    assert data3["intent"] == "PROJECTS_SYNTHESIS"
    assert "Sprint 44" in data3["reply"]
    assert "FIN-50" in data3["reply"]
    print("  [PASS] Domain Routing verified: Successfully answered cross-domain Jira Sprint query")

    print("\n--> MILESTONE 3 VERIFICATION COMPLETED: ALL AGENTIC CHATBOT TESTS PASSED!\n")

if __name__ == "__main__":
    test_milestone3()
