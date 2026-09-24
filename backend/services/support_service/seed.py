import uuid
from sqlalchemy.orm import Session
from services.support_service.models import Ticket, TicketMessage

def seed_support_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds mission-critical client support tickets, SLAs, and message threads."""
    if session.query(Ticket).filter_by(org_id=org_id).first():
        return

    # 1. Tickets
    t1 = Ticket(
        id=str(uuid.uuid4()),
        org_id=org_id,
        ticket_number="TKT-2026-001",
        customer_name="David Zhang",
        customer_email="dzhang@nexusrobotics.internal",
        subject="LiDAR Point Cloud Buffer Jitter in Rover Unit 12",
        description="High packet loss observed during sharp 90-degree indoor turns.",
        priority="Urgent",
        status="In Progress",
        assigned_to="Marcus Chen",
        sla_target_hours=2.0,
        elapsed_hours=0.8,
        is_breached=False
    )
    t2 = Ticket(
        id=str(uuid.uuid4()),
        org_id=org_id,
        ticket_number="TKT-2026-002",
        customer_name="Dr. Eleanor Vance",
        customer_email="eleanor@quantumdynamics.internal",
        subject="SSO SAML Identity Provider Certificate Rotation",
        description="Requesting automated rollover for corporate Okta IdP metadata.",
        priority="High",
        status="Resolved",
        assigned_to="Elena Rostova",
        sla_target_hours=4.0,
        elapsed_hours=2.1,
        is_breached=False
    )
    t3 = Ticket(
        id=str(uuid.uuid4()),
        org_id=org_id,
        ticket_number="TKT-2026-003",
        customer_name="Liam O'Connor",
        customer_email="liam@apexbiometrics.internal",
        subject="API Webhook Rate Limiting Threshold Inquiry",
        description="Seeking confirmation on default burst capacity for biometric batch ingest.",
        priority="Low",
        status="Open",
        assigned_to="Tier 1 Specialist",
        sla_target_hours=8.0,
        elapsed_hours=1.2,
        is_breached=False
    )
    session.add_all([t1, t2, t3])
    session.flush()

    # 2. Messages
    m1 = TicketMessage(
        id=str(uuid.uuid4()),
        org_id=org_id,
        ticket_id=t1.id,
        sender_name="David Zhang",
        sender_type="Customer",
        message="Seeing 2% frame drops on ROS2 bridge when sensor captures > 50k points/sec."
    )
    m2 = TicketMessage(
        id=str(uuid.uuid4()),
        org_id=org_id,
        ticket_id=t1.id,
        sender_name="Marcus Chen",
        sender_type="Agent",
        message="Engineering identified the issue in the ring buffer mutex. Patch scheduled for push in 30 mins."
    )
    session.add_all([m1, m2])
    session.commit()
