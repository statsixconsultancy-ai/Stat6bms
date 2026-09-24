from sqlalchemy.orm import Session
from services.auth_service.models import Organization, User, Role
from common.security import hash_password

def seed_auth_data(session: Session):
    """Seed initial AcroFlow enterprise organization and core users if absent."""
    org = session.query(Organization).filter_by(id="org-acroflow-main").first()
    if not org:
        org = Organization(
            id="org-acroflow-main",
            name="AcroFlow Global Enterprises",
            slug="acroflow",
            industry="FinTech & Autonomous Systems",
            currency="USD",
            timezone="America/New_York",
            plan="Enterprise Multi-Tenant"
        )
        session.add(org)
        session.commit()

    admin = session.query(User).filter_by(email="admin@acroflow.enterprise").first()
    if not admin:
        admin = User(
            id="usr-dev-001",
            org_id="org-acroflow-main",
            email="admin@acroflow.enterprise",
            full_name="Prann (Enterprise Admin)",
            password_hash=hash_password("AcroFlow2026!"),
            role="superadmin",
            avatar_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=120",
            is_active=True
        )
        session.add(admin)

        # Team members
        marcus = User(
            id="usr-dev-002",
            org_id="org-acroflow-main",
            email="marcus.chen@acroflow.enterprise",
            full_name="Marcus Chen",
            password_hash=hash_password("MarcusPass2026!"),
            role="lead_architect",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120",
            is_active=True
        )
        elena = User(
            id="usr-dev-003",
            org_id="org-acroflow-main",
            email="elena.rostova@acroflow.enterprise",
            full_name="Elena Rostova",
            password_hash=hash_password("ElenaPass2026!"),
            role="platform_lead",
            avatar_url="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=120",
            is_active=True
        )
        session.add_all([marcus, elena])
        session.commit()
