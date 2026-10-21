from sqlalchemy.orm import Session
from services.auth_service.models import Organization, User
from common.security import hash_password

def seed_auth_data(session: Session):
    """Seed initial enterprise organization and master admin account if absent."""
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
            password_hash=hash_password("Password123!"),
            role="superadmin",
            persona="ADMIN",
            avatar_url="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=120",
            is_active=True
        )
        session.add(admin)
        session.commit()
