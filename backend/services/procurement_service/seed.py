import uuid
from sqlalchemy.orm import Session
from services.procurement_service.models import Vendor, PurchaseOrder, POLineItem, GoodsReceiptNote, VendorBill

def seed_procurement_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds strategic hardware suppliers, purchase orders, goods receipts, and 3-way matching bills."""
    if session.query(Vendor).filter_by(org_id=org_id).first():
        return

    # 1. Vendors
    v1 = Vendor(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Velodyne LiDAR Manufacturing Corp",
        contact_email="orders@velodynelidar.internal",
        phone="+1 (555) 881-2200",
        address="5521 Hellyer Ave, San Jose, CA",
        rating=4.9,
        payment_terms="Net30"
    )
    v2 = Vendor(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="NVIDIA Accelerated Compute OEM",
        contact_email="enterprise-oem@nvidia.internal",
        phone="+1 (555) 881-3300",
        address="2788 San Tomas Expressway, Santa Clara, CA",
        rating=4.95,
        payment_terms="Net30"
    )
    v3 = Vendor(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Maxon Precision Motor AG",
        contact_email="supply@maxonmotors.internal",
        phone="+1 (555) 881-4400",
        address="Brünigstrasse 220, Sachseln, Switzerland",
        rating=4.8,
        payment_terms="Net60"
    )
    session.add_all([v1, v2, v3])
    session.flush()

    # 2. Purchase Order
    po1 = PurchaseOrder(
        id=str(uuid.uuid4()),
        org_id=org_id,
        po_number="PO-2026-001",
        vendor_id=v1.id,
        status="Matched_Approved",
        total_amount=36000.0,
        order_date="2026-08-20",
        expected_delivery="2026-09-05"
    )
    session.add(po1)
    session.flush()

    po_item = POLineItem(
        id=str(uuid.uuid4()),
        org_id=org_id,
        po_id=po1.id,
        product_sku="HW-204",
        description="LiDAR Spatial Scanning Array",
        quantity_ordered=30,
        unit_price=1200.0,
        total_price=36000.0
    )
    session.add(po_item)
    session.flush()

    # 3. Goods Receipt Note (GRN)
    grn1 = GoodsReceiptNote(
        id=str(uuid.uuid4()),
        org_id=org_id,
        po_id=po1.id,
        grn_number="GRN-2026-001",
        received_date="2026-09-04",
        received_by="David Kim (Boston Hub Lead)",
        quantity_received=30,
        status="Full"
    )
    session.add(grn1)
    session.flush()

    # 4. Vendor Bill (3-way match verified)
    bill1 = VendorBill(
        id=str(uuid.uuid4()),
        org_id=org_id,
        po_id=po1.id,
        grn_id=grn1.id,
        bill_number="BILL-VEL-9901",
        billed_amount=36000.0,
        status="Matched_Approved"
    )
    session.add(bill1)
    session.commit()
