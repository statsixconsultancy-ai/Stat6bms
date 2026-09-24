import uuid
from sqlalchemy.orm import Session
from services.collaboration_service.models import ChatChannel, ChatMessage

def seed_collaboration_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds default team channels and communication history."""
    if session.query(ChatChannel).filter_by(org_id=org_id).first():
        return

    # Channels
    c1 = ChatChannel(id=str(uuid.uuid4()), org_id=org_id, name="general", description="Company-wide announcements and operational syncs.")
    c2 = ChatChannel(id=str(uuid.uuid4()), org_id=org_id, name="engineering", description="Microservices architecture, code reviews, and infrastructure.")
    c3 = ChatChannel(id=str(uuid.uuid4()), org_id=org_id, name="deals", description="Commercial closed-won alerts and enterprise celebrations.")
    c4 = ChatChannel(id=str(uuid.uuid4()), org_id=org_id, name="incident-response", description="P1 critical escalations and autonomous system alerts.")
    session.add_all([c1, c2, c3, c4])
    session.flush()

    # Initial Messages
    m1 = ChatMessage(
        id=str(uuid.uuid4()),
        org_id=org_id,
        channel_id=c2.id,
        user_id="usr-dev-002",
        user_name="Marcus Chen",
        message="Sprint 14 ROS2 UDP telemetry daemon benchmarked under 2ms. Ready for QA.",
        message_type="text"
    )
    m2 = ChatMessage(
        id=str(uuid.uuid4()),
        org_id=org_id,
        channel_id=c3.id,
        user_id="usr-dev-001",
        user_name="Sarah Connor",
        message="Nexus Robotics $450,000 enterprise fleet contract signed and confirmed!",
        message_type="event_alert"
    )
    session.add_all([m1, m2])
    session.commit()
