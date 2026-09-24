import uuid
from sqlalchemy.orm import Session
from services.ai_copilot_service.models import AnomalyInsight

def seed_ai_copilot_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds proactive intelligence anomalies and executive operational recommendations."""
    if session.query(AnomalyInsight).filter_by(org_id=org_id).first():
        return

    a1 = AnomalyInsight(
        id=str(uuid.uuid4()),
        org_id=org_id,
        category="Supply Chain",
        severity="Critical",
        title="Hardware Inventory Depletion: Jetson Tensor Cores (HW-501)",
        description="Physical stock at Boston Hub has fallen to 8 units, below the 15-unit safe operating floor.",
        recommended_action="Execute automated replenishment PO with NVIDIA OEM to secure delivery by Oct 10.",
        is_resolved=False
    )
    a2 = AnomalyInsight(
        id=str(uuid.uuid4()),
        org_id=org_id,
        category="Customer Support",
        severity="Warning",
        title="P1 SLA Buffer Warning: Nexus Robotics Mission Control",
        description="Ticket TKT-2026-001 has 1.2 hours remaining before strict contract breach threshold.",
        recommended_action="Notify Marcus Chen to deploy ROS2 ring buffer patch before 03:00 PM.",
        is_resolved=False
    )
    a3 = AnomalyInsight(
        id=str(uuid.uuid4()),
        org_id=org_id,
        category="Financial Operations",
        severity="Info",
        title="Double-Entry General Ledger Perfect Balance Confirmed",
        description="All accounts receivable, payments, and talent disbursements reconciled with 0.00 discrepancy.",
        recommended_action="Maintain automated weekly P&L export to board audit archive.",
        is_resolved=False
    )
    session.add_all([a1, a2, a3])
    session.commit()
