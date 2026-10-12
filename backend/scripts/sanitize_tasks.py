import os
import sys
import uuid
import json
from datetime import datetime, timedelta

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.config import get_service_config
from common.database import create_db_manager
from common.models import Base
from services.automation_service.models import ScheduledTask, HITLApprovalRequest

config = get_service_config("automation-service", default_port=8012, db_filename="automation.db")
db_mgr = create_db_manager(config.database_url)
session = next(db_mgr.get_session())

try:
    session.query(HITLApprovalRequest).delete()
    session.query(ScheduledTask).delete()
    session.commit()

    now = datetime.utcnow()

    # 1. PENDING task requiring HITL approval
    t1_id = str(uuid.uuid4())
    h1_id = str(uuid.uuid4())
    t1 = ScheduledTask(
        id=t1_id,
        org_id="org-acroflow-main",
        task_name="Send Net30 Overdue Invoice Reminder to Acme Corp",
        target_service="finance-service",
        action_type="SEND_PAYMENT_REMINDER",
        payload=json.dumps({"invoice_id": "INV-2024-002", "client": "Acme Corp", "amount": 27500.0}),
        scheduled_for=(now + timedelta(days=1)).isoformat(),
        precondition_check=json.dumps({"field": "status", "expected": "OVERDUE"}),
        status="PENDING",
        requires_hitl=True,
        hitl_approval_id=h1_id
    )
    h1 = HITLApprovalRequest(
        id=h1_id,
        org_id="org-acroflow-main",
        task_id=t1_id,
        requested_by="AI Copilot Scheduler",
        assigned_approver_role="FINANCE_MANAGER",
        risk_level="HIGH",
        title="High-Value Net30 Payment Reminder",
        summary="Automated collection dispatch for Acme Corp invoice INV-2024-002 ($27,500.00). Requires manager approval before delivery.",
        action_diff=json.dumps({"invoice_id": "INV-2024-002", "amount": 27500.0}),
        status="PENDING"
    )

    # 2. EXECUTED task
    t2 = ScheduledTask(
        id=str(uuid.uuid4()),
        org_id="org-acroflow-main",
        task_name="Synchronize Central Warehouse SKU Thresholds",
        target_service="inventory-service",
        action_type="SYNC_STOCK",
        payload=json.dumps({"warehouse": "Central Hub", "categories": ["Electronics", "Hardware"]}),
        scheduled_for=(now - timedelta(hours=2)).isoformat(),
        precondition_check=None,
        status="EXECUTED",
        requires_hitl=False,
        executed_at=(now - timedelta(hours=2)).isoformat(),
        execution_result=json.dumps({"outcome": "SUCCESS", "updated_skus": 42, "sync_duration_ms": 120})
    )

    # 3. CANCELLED task (guard condition prevented unwanted execution)
    t3 = ScheduledTask(
        id=str(uuid.uuid4()),
        org_id="org-acroflow-main",
        task_name="Dunning Notice on Disputed Account",
        target_service="finance-service",
        action_type="SEND_DUNNING",
        payload=json.dumps({"invoice_id": "INV-2024-001", "dispute_flag": False}),
        scheduled_for=(now - timedelta(hours=5)).isoformat(),
        precondition_check=json.dumps({"field": "status", "expected": "OVERDUE", "actual": "PAID"}),
        status="CANCELLED",
        requires_hitl=False,
        execution_result=json.dumps({"outcome": "CANCELLED", "reason": "Precondition guard failed: status was 'PAID', expected 'OVERDUE'"})
    )

    # 4. PENDING automated background task
    t4 = ScheduledTask(
        id=str(uuid.uuid4()),
        org_id="org-acroflow-main",
        task_name="Execute Weekly GDPR/SOC2 Audit Trail Rotation",
        target_service="compliance-service",
        action_type="GENERATE_REPORT",
        payload=json.dumps({"report_type": "SOC2_TYPE_II", "scope": "All Services"}),
        scheduled_for=(now + timedelta(hours=8)).isoformat(),
        status="PENDING",
        requires_hitl=False
    )

    session.add_all([t1, h1, t2, t3, t4])
    session.commit()
    print("Successfully sanitized tasks database via SQLAlchemy!")
finally:
    session.close()
