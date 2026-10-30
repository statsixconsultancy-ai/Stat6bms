from sqlalchemy.orm import Session
from services.auth_service.models import Organization, User
from common.security import hash_password

def seed_auth_data(session: Session):
    """Seed initial enterprise organization and master 7-persona credentials if absent."""
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

    personas_seed = [
        {
            "id": "usr-dev-001",
            "email": "admin@acroflow.enterprise",
            "full_name": "Prann (Enterprise Admin)",
            "role": "superadmin",
            "persona": "ADMIN",
            "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=120"
        },
        {
            "id": "usr-dev-002",
            "email": "manager@acroflow.enterprise",
            "full_name": "Department Manager",
            "role": "manager",
            "persona": "MANAGER",
            "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120"
        },
        {
            "id": "usr-dev-003",
            "email": "staff@acroflow.enterprise",
            "full_name": "Staff Member",
            "role": "employee",
            "persona": "EMPLOYEE",
            "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120"
        },
        {
            "id": "usr-dev-004",
            "email": "client@portal.enterprise",
            "full_name": "Client Contact",
            "role": "customer",
            "persona": "CUSTOMER",
            "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=120"
        },
        {
            "id": "usr-dev-005",
            "email": "supplier@portal.enterprise",
            "full_name": "Supplier Representative",
            "role": "vendor",
            "persona": "VENDOR",
            "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=120"
        },
        {
            "id": "usr-dev-006",
            "email": "partner@portal.enterprise",
            "full_name": "Channel Partner",
            "role": "partner",
            "persona": "PARTNER",
            "avatar_url": "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?w=120"
        },
        {
            "id": "usr-dev-007",
            "email": "auditor@portal.enterprise",
            "full_name": "External Auditor",
            "role": "auditor",
            "persona": "EXTERNAL_USER",
            "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=120"
        }
    ]

    for p in personas_seed:
        existing = session.query(User).filter_by(email=p["email"]).first()
        if not existing:
            u = User(
                id=p["id"],
                org_id="org-acroflow-main",
                email=p["email"],
                full_name=p["full_name"],
                password_hash=hash_password("Password123!"),
                role=p["role"],
                persona=p["persona"],
                avatar_url=p["avatar_url"],
                is_active=True
            )
            session.add(u)
    session.commit()
