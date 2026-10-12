import os
import sys
import json
from datetime import datetime, timedelta

# Add backend directory to sys.path
backend_dir = r"C:\Users\prann\.gemini\antigravity\scratch\bms-platform\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.models import Base
from common.database import create_db_manager
from services.automation_service.models import ScheduledTask, HITLApprovalRequest, AutomationRule

def test_milestone1():
    print("--> Testing Milestone 1: Data Models & Persistence...")
    test_db_url = "sqlite:///C:/Users/prann/.gemini/antigravity/scratch/bms-platform/backend/data/test_m1_automation.db"
    db_mgr = create_db_manager(test_db_url)
    db_mgr.init_tables(Base)

    session = next(db_mgr.get_session())
    try:
        org_id = "org-test-milestone1"
        target_time = (datetime.utcnow() + timedelta(hours=24)).isoformat()

        # 1. Create a ScheduledTask
        task = ScheduledTask(
            org_id=org_id,
            created_by_user_id="user-exec-1",
            conversation_id="conv-12345",
            task_name="Send Dunning Reminder Sequence #2 to Acme Corp",
            target_service="finance-service",
            action_type="SEND_PAYMENT_REMINDER",
            payload=json.dumps({"invoice_id": "INV-2024-002", "client": "Acme Corp", "amount": 27500.0}),
            scheduled_for=target_time,
            precondition_check=json.dumps({"field": "status", "expected": "OVERDUE"}),
            status="PENDING",
            requires_hitl=True
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        assert task.id is not None
        assert task.requires_hitl is True
        print(f"  [PASS] Created ScheduledTask: id={task.id}, status={task.status}, scheduled_for={task.scheduled_for}")

        # 2. Create a linked HITLApprovalRequest
        hitl = HITLApprovalRequest(
            org_id=org_id,
            task_id=task.id,
            requested_by="AI_AGENT_COPILOT",
            assigned_approver_role="FINANCE_MANAGER",
            risk_level="HIGH",
            title="Approve Outbound Dunning Notice to Acme Corp",
            summary="Invoice INV-2024-002 ($27,500.00) is 4 days overdue. Propose sending Net30 Reminder.",
            action_diff=json.dumps({"to": "billing@acme.com", "template": "dunning_seq_2", "invoice": "INV-2024-002"}),
            status="PENDING",
            expires_at=(datetime.utcnow() + timedelta(days=2)).isoformat()
        )
        session.add(hitl)
        session.commit()
        session.refresh(hitl)

        assert hitl.id is not None
        assert hitl.task_id == task.id
        print(f"  [PASS] Created HITLApprovalRequest: id={hitl.id}, risk={hitl.risk_level}, status={hitl.status}")

        # 3. Test Relationship & Querying
        queried_task = session.query(ScheduledTask).filter_by(id=task.id).first()
        assert len(queried_task.hitl_requests) == 1
        assert queried_task.hitl_requests[0].id == hitl.id
        print(f"  [PASS] Relationship verified: Task has {len(queried_task.hitl_requests)} linked HITL request(s)")

        # 4. Test Model Serialization
        d = queried_task.to_dict()
        assert d["task_name"] == "Send Dunning Reminder Sequence #2 to Acme Corp"
        print(f"  [PASS] to_dict() serialization verified successfully")

        print("--> MILESTONE 1 VERIFICATION COMPLETED: ALL ASSERTIONS PASSED!\n")
    finally:
        session.close()

if __name__ == "__main__":
    test_milestone1()
