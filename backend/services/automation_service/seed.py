import uuid
from sqlalchemy.orm import Session
from services.automation_service.models import AutomationRule

def seed_automation_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds WHEN-IF-DO event-driven business workflow automation rules."""
    if session.query(AutomationRule).filter_by(org_id=org_id).first():
        return

    r1 = AutomationRule(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Enterprise High-Value Deal Slack Broadcast",
        trigger_event="deal.won",
        condition_code="amount >= 100000",
        action_type="DISPATCH_NOTIFICATION",
        action_config='{"target": "#deals", "channel": "Slack", "priority": "High"}',
        is_active=True,
        execution_count=3
    )
    r2 = AutomationRule(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Auto-Trigger Restock Order on Low Inventory",
        trigger_event="stock.low",
        condition_code="True",
        action_type="CREATE_PURCHASE_ORDER",
        action_config='{"auto_approve": True}',
        is_active=True,
        execution_count=2
    )
    r3 = AutomationRule(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="P1 Incident Immediate Team Escalation",
        trigger_event="ticket.urgent",
        condition_code="True",
        action_type="NOTIFY_INCIDENT_SWARM",
        action_config='{"target": "#incident-response", "alert_level": "Emergency"}',
        is_active=True,
        execution_count=1
    )
    session.add_all([r1, r2, r3])
    session.commit()
