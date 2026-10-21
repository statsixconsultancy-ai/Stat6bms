import uuid
from sqlalchemy.orm import Session
from services.collaboration_service.models import ChatChannel

def seed_collaboration_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds default enterprise team communication channels. Zero preloaded chat messages."""
    if not session.query(ChatChannel).filter_by(org_id=org_id).first():
        c1 = ChatChannel(id=str(uuid.uuid4()), org_id=org_id, name="general", description="Company-wide announcements and operational syncs.")
        c2 = ChatChannel(id=str(uuid.uuid4()), org_id=org_id, name="engineering", description="Microservices architecture, code reviews, and infrastructure.")
        c3 = ChatChannel(id=str(uuid.uuid4()), org_id=org_id, name="deals", description="Commercial closed-won alerts and enterprise celebrations.")
        c4 = ChatChannel(id=str(uuid.uuid4()), org_id=org_id, name="incident-response", description="P1 critical escalations and autonomous system alerts.")
        session.add_all([c1, c2, c3, c4])
        session.commit()
