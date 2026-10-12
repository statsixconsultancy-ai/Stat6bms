"""
Milestone 5 & Full End-to-End System Verification:
Validates the complete Agentic AI Architecture:
1. Dual-track Chatbot: Immediate Telemetry Synthesis + Temporal Background Task Scheduling.
2. Temporal Scheduler: State verification, Precondition check, Time gating.
3. Human-In-The-Loop (HITL) Gatekeeper: High-risk action halting, Approval card lifecycle, Post-approval execution.
4. Precondition auto-cancellation if conditions are no longer met (avoiding duplicate/stale actions).
5. Background Tick Worker: Automatic execution of due autonomous tasks.
"""
import sys
import os
from datetime import datetime, timedelta

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from common.security import create_access_token
from services.ai_copilot_service.main import app as ai_app, db_mgr as ai_db_mgr, Base as ai_Base
from services.automation_service.main import app as auto_app, db_mgr as auto_db_mgr, Base as auto_Base

def test_full_agentic_flow():
    print("=" * 65)
    print("STARTING FULL END-TO-END AGENTIC AI & TEMPORAL HITL VERIFICATION")
    print("=" * 65)

    # Initialize tables
    ai_db_mgr.init_tables(ai_Base)
    auto_db_mgr.init_tables(auto_Base)

    ai_client = TestClient(ai_app)
    auto_client = TestClient(auto_app)

    token = create_access_token({
        "sub": "user-exec-1",
        "user_id": "user-exec-1",
        "org_id": "org-acroflow-main",
        "role": "SUPER_ADMIN"
    })
    headers = {"Authorization": f"Bearer {token}"}

    # -------------------------------------------------------------
    # 1. Chatbot Dual-Track: Immediate Synthesis + Background Task
    # -------------------------------------------------------------
    print("\n[Step 1] Conversational Query with Background HITL Scheduling...")
    chat_prompt = "What's our cash position today? Also schedule a follow-up payment reminder to Acme Corp tomorrow at 10 AM, but ask me for approval before sending."
    
    chat_resp = ai_client.post("/ai/chat", json={"message": chat_prompt}, headers=headers)
    assert chat_resp.status_code == 200, f"AI chat failed: {chat_resp.text}"
    chat_data = chat_resp.json()

    # Track A: Immediate Synthesis
    assert "580,000.00" in chat_data["reply"], "Missing cash/revenue telemetry in reply"
    assert "1,540,950.00" in chat_data["reply"], "Missing operating reserve in reply"
    print("  [PASS] Track A: Instant financial telemetry synthesized without blocking:")
    print(f"         \"{chat_data['reply'][:110]}...\"")

    # Track B: Background Task
    task_info = chat_data["scheduled_task"]
    assert task_info is not None, "Expected scheduled task to be created"
    task_id = task_info["task_id"]
    hitl_id = task_info["hitl_approval_id"]
    assert task_info["target_service"] == "finance-service"
    assert task_info["requires_hitl"] is True
    print(f"  [PASS] Track B: Temporal task scheduled:")
    print(f"         ID: {task_id} | Name: {task_info['task_name']} | Requires HITL: {task_info['requires_hitl']}")

    # Track C: HITL Linkage
    assert hitl_id is not None, "Expected HITL approval ID to be linked"
    print(f"  [PASS] Track C: Human-in-the-Loop approval card generated with ID: {hitl_id}")

    # -------------------------------------------------------------
    # 2. Temporal Gating: Prevent Premature Execution
    # -------------------------------------------------------------
    print("\n[Step 2] Testing Temporal Gatekeeper (Premature Execution Prevention)...")
    premature_resp = auto_client.post(f"/automation/tasks/{task_id}/execute", headers=headers)
    assert premature_resp.status_code == 400
    assert "not arrived yet" in premature_resp.json()["detail"]
    print(f"  [PASS] Temporal gate prevented premature run: {premature_resp.json()['detail'][:65]}...")

    # -------------------------------------------------------------
    # 3. HITL Gatekeeper: Halts Task in WAITING_APPROVAL
    # -------------------------------------------------------------
    print("\n[Step 3] Testing HITL Gatekeeper at Due Time...")
    # Force execution simulation (as if time has arrived)
    due_resp = auto_client.post(f"/automation/tasks/{task_id}/execute?force=true", headers=headers)
    assert due_resp.status_code == 200
    due_data = due_resp.json()
    assert due_data["status"] == "WAITING_APPROVAL"
    print(f"  [PASS] Task halted in safety state: status={due_data['status']}")
    print(f"         Message: {due_data['result']['message']}")

    # -------------------------------------------------------------
    # 4. Human Decision: Review Pending Queue and Approve
    # -------------------------------------------------------------
    print("\n[Step 4] Human Reviewer Decision on Interactive Card...")
    pending_resp = auto_client.get("/automation/hitl/pending", headers=headers)
    assert pending_resp.status_code == 200
    matching = [a for a in pending_resp.json() if a["id"] == hitl_id]
    assert len(matching) == 1, "Approval request not visible in pending queue"
    print(f"  [PASS] Found card in pending queue: {matching[0]['title']}")

    # Approve
    decision_resp = auto_client.post(
        f"/automation/hitl/{hitl_id}/decision",
        json={"decision": "APPROVED", "decision_notes": "Authorized by CFO for Acme Corp follow-up"},
        headers=headers
    )
    assert decision_resp.status_code == 200
    assert decision_resp.json()["status"] == "APPROVED"
    print("  [PASS] Approval recorded with audit trail.")

    # Verify task auto-executed upon approval
    task_verify = auto_client.get(f"/automation/tasks/{task_id}", headers=headers).json()
    assert task_verify["status"] == "EXECUTED"
    assert task_verify["executed_at"] is not None
    print(f"  [PASS] Task auto-executed upon human approval: status={task_verify['status']}")

    # -------------------------------------------------------------
    # 5. Precondition Validation (Auto-cancel Stale Actions)
    # -------------------------------------------------------------
    print("\n[Step 5] Testing State Precondition Engine (Cancelling Stale Actions)...")
    past_time = (datetime.utcnow() - timedelta(minutes=1)).isoformat()
    stale_task = auto_client.post(
        "/automation/tasks/schedule",
        headers=headers,
        json={
            "task_name": "Dunning Email If Overdue",
            "target_service": "finance-service",
            "action_type": "SEND_DUNNING",
            "payload": {"invoice_id": "INV-2024-001"},
            "scheduled_for": past_time,
            "precondition_check": {"field": "status", "expected": "OVERDUE", "actual": "PAID"},
            "requires_hitl": False
        }
    ).json()

    precond_exec = auto_client.post(f"/automation/tasks/{stale_task['id']}/execute", headers=headers).json()
    assert precond_exec["status"] == "CANCELLED"
    print(f"  [PASS] Stale action auto-cancelled by precondition check: {precond_exec['result']['reason']}")

    # -------------------------------------------------------------
    # 6. Background Tick Worker (Autonomous Due Tasks)
    # -------------------------------------------------------------
    print("\n[Step 6] Testing Background Scheduler Tick Worker...")
    auto_task = auto_client.post(
        "/automation/tasks/schedule",
        headers=headers,
        json={
            "task_name": "Synchronize Warehouse Inventory SKU Levels",
            "target_service": "inventory-service",
            "action_type": "SYNC_STOCK",
            "payload": {"warehouse": "Central Hub"},
            "scheduled_for": past_time,
            "requires_hitl": False
        }
    ).json()

    tick_resp = auto_client.post("/automation/scheduler/tick", headers=headers).json()
    assert tick_resp["tasks_checked"] >= 1
    executed = [e for e in tick_resp["executions"] if e["task_id"] == auto_task["id"]]
    assert len(executed) == 1
    assert executed[0]["status"] == "EXECUTED"
    print(f"  [PASS] Background worker tick processed due task: status={executed[0]['status']}")

    # -------------------------------------------------------------
    # 7. Pure Read-Only Chat Query (No Unwanted Tasks)
    # -------------------------------------------------------------
    print("\n[Step 7] Testing Pure Read-Only Chatbot Query...")
    sprint_resp = ai_client.post(
        "/ai/chat",
        headers=headers,
        json={"message": "What is blocked on Sprint 44 right now?"}
    ).json()
    assert "FIN-50" in sprint_resp["reply"]
    assert sprint_resp["scheduled_task"] is None
    print("  [PASS] Pure conversational query answered with zero scheduled tasks:")
    print(f"         \"{sprint_resp['reply'][:110]}...\"")

    print("\n" + "=" * 65)
    print("ALL 7 END-TO-END VALIDATION STAGES COMPLETED SUCCESSFULLY (100% PASS)")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    test_full_agentic_flow()
