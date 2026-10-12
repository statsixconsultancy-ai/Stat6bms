import os
import sys
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = r"C:\Users\prann\.gemini\antigravity\scratch\bms-platform\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.security import create_access_token
from services.automation_service.main import app, db_mgr, Base

def test_milestone2():
    print("--> Testing Milestone 2: Temporal Scheduler & HITL State Engine...")
    db_mgr.init_tables(Base)
    client = TestClient(app)

    # Generate test auth token
    token = create_access_token({"sub": "user-exec-1", "user_id": "user-exec-1", "org_id": "org-acroflow-main", "role": "SUPER_ADMIN"})
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Test Schedule Task in Future
    future_time = (datetime.utcnow() + timedelta(hours=2)).isoformat()
    resp = client.post(
        "/automation/tasks/schedule",
        headers=headers,
        json={
            "task_name": "Send Overdue Invoice Reminder to Acme Corp",
            "target_service": "finance-service",
            "action_type": "SEND_PAYMENT_REMINDER",
            "payload": {"invoice_id": "INV-2024-002", "amount": 27500.0},
            "scheduled_for": future_time,
            "requires_hitl": True,
            "conversation_id": "conv-test-1"
        }
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
    task_data = resp.json()
    task_id = task_data["id"]
    hitl_id = task_data["hitl_approval_id"]
    assert task_data["status"] == "PENDING"
    assert task_data["requires_hitl"] is True
    assert hitl_id is not None
    print(f"  [PASS] Successfully scheduled future task: {task_id} with linked HITL: {hitl_id}")

    # 2. Test Temporal Gate (Cannot execute before scheduled time)
    exec_resp = client.post(f"/automation/tasks/{task_id}/execute", headers=headers)
    assert exec_resp.status_code == 400
    print(f"  [PASS] Temporal gate verified: Prevented premature execution ({exec_resp.json()['detail'][:60]}...)")

    # 3. Test HITL Gate (Attempting to execute requires human approval first)
    force_exec = client.post(f"/automation/tasks/{task_id}/execute?force=true", headers=headers)
    assert force_exec.status_code == 200
    assert force_exec.json()["status"] == "WAITING_APPROVAL"
    print(f"  [PASS] HITL gate verified: Task entered WAITING_APPROVAL state")

    # 4. Test List Pending HITL Approvals
    pending_resp = client.get("/automation/hitl/pending", headers=headers)
    assert pending_resp.status_code == 200
    pending_list = pending_resp.json()
    matching = [a for a in pending_list if a["id"] == hitl_id]
    assert len(matching) == 1
    print(f"  [PASS] Pending HITL approval found in queue: {matching[0]['title']}")

    # 5. Test Human Approves Task
    decision_resp = client.post(
        f"/automation/hitl/{hitl_id}/decision",
        headers=headers,
        json={"decision": "APPROVED", "decision_notes": "Authorized by CFO for Acme Corp"}
    )
    assert decision_resp.status_code == 200
    assert decision_resp.json()["status"] == "APPROVED"

    # Verify task was automatically executed upon approval
    task_verify = client.get(f"/automation/tasks/{task_id}", headers=headers).json()
    assert task_verify["status"] == "EXECUTED"
    assert task_verify["executed_at"] is not None
    print(f"  [PASS] Human approval triggered automated execution: status={task_verify['status']}, executed_at={task_verify['executed_at']}")

    # 6. Test Precondition Failure (State changed e.g. invoice already paid)
    past_time = (datetime.utcnow() - timedelta(minutes=1)).isoformat()
    precond_task = client.post(
        "/automation/tasks/schedule",
        headers=headers,
        json={
            "task_name": "Dunning Email if Unpaid",
            "target_service": "finance-service",
            "action_type": "SEND_DUNNING",
            "payload": {"invoice_id": "INV-2024-001"},
            "scheduled_for": past_time,
            "precondition_check": {"field": "status", "expected": "OVERDUE", "actual": "PAID"}, # Precondition violated
            "requires_hitl": False
        }
    ).json()

    precond_exec = client.post(f"/automation/tasks/{precond_task['id']}/execute", headers=headers).json()
    assert precond_exec["status"] == "CANCELLED"
    print(f"  [PASS] Precondition check verified: Invalid state correctly cancelled execution ({precond_exec['result']['reason'][:55]}...)")

    # 7. Test Background Scheduler Tick Worker
    tick_task = client.post(
        "/automation/tasks/schedule",
        headers=headers,
        json={
            "task_name": "Sync Warehouse Inventory SKU Levels",
            "target_service": "inventory-service",
            "action_type": "SYNC_STOCK",
            "payload": {"warehouse": "Boston Hub"},
            "scheduled_for": past_time,
            "requires_hitl": False
        }
    ).json()

    tick_resp = client.post("/automation/scheduler/tick", headers=headers).json()
    assert tick_resp["tasks_checked"] >= 1
    executed_in_tick = [e for e in tick_resp["executions"] if e["task_id"] == tick_task["id"]]
    assert len(executed_in_tick) == 1
    assert executed_in_tick[0]["status"] == "EXECUTED"
    print(f"  [PASS] Background scheduler tick verified: Automatically picked up and executed due task '{tick_task['task_name']}'")

    print("\n--> MILESTONE 2 VERIFICATION COMPLETED: ALL 7 TEST CASES PASSED!\n")

if __name__ == "__main__":
    test_milestone2()
