import uuid
from sqlalchemy.orm import Session
from services.inventory_service.models import Warehouse

def seed_inventory_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds canonical primary enterprise warehouse facility. Zero preloaded products, batches, or assets."""
    if not session.query(Warehouse).filter_by(org_id=org_id).first():
        wh = Warehouse(
            id=str(uuid.uuid4()),
            org_id=org_id,
            code="WH-HQ-01",
            name="Primary Distribution Center - HQ",
            location="Enterprise Headquarters",
            capacity=25000
        )
        session.add(wh)
        session.commit()
