from sqlalchemy.orm import Session

def seed_procurement_data(session: Session, org_id: str = "org-acroflow-main"):
    """Zero-data clean state: Vendors, purchase orders, GRNs, and 3-way match bills are created by users."""
    pass
