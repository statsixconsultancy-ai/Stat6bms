from app.database import SessionLocal, init_db
from app.models import Organization, User

def seed_database():
    """Clean zero-data state for legacy app."""
    init_db()
    db = SessionLocal()
    existing_org = db.query(Organization).first()
    if existing_org:
        db.close()
        return existing_org.id

    org = Organization(
        name="AcroFlow Global Systems",
        slug="acroflow",
        industry="Enterprise AI & Cloud Infrastructure",
        currency="USD",
        timezone="America/New_York"
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    admin_user = User(
        org_id=org.id,
        email="admin@acroflow.enterprise",
        full_name="Prann (Enterprise Admin)",
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    db.close()
    return org.id
