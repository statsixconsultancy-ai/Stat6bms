import os
import sys
import uuid
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.config import get_service_config
from common.database import create_db_manager
from common.models import Base
from common.security import get_user_context, UserContext
from common.middleware import setup_microservice_middleware
from common.event_bus import event_bus

from services.procurement_service.models import Vendor, PurchaseOrder, POLineItem, GoodsReceiptNote, VendorBill, PurchaseRequisition, RFQ
from services.procurement_service.schemas import (
    VendorCreate, VendorResponse,
    POLineItemCreate, POLineItemResponse,
    PurchaseOrderCreate, PurchaseOrderResponse, PurchaseOrderDetailResponse,
    GRNCreate, GRNResponse,
    VendorBillCreate, VendorBillResponse,
    ThreeWayMatchResponse,
    RequisitionCreate, RequisitionResponse,
    RFQCreate, RFQBidSubmitRequest, RFQResponse, RFQAwardRequest,
    VendorScorecardResponse
)
from services.procurement_service.seed import seed_procurement_data

config = get_service_config("procurement-service", default_port=8008, db_filename="procurement.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="BMS Procurement & Vendor Operations Microservice",
    description="Strategic Vendor Sourcing, Automated Low-Stock Purchase Orders & 3-Way Matching Verification",
    version="2.0.0"
)

setup_microservice_middleware(app, "procurement-service", config.cors_origins)

@app.on_event("startup")
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_procurement_data(session)
    finally:
        session.close()

def get_db():
    yield from db_mgr.get_session()

# ----------------------------------------------------
# 1. Health & Event Broker Webhook Endpoints
# ----------------------------------------------------
@app.get("/health")
def health():
    return {"service": "procurement-service", "status": "UP", "port": config.service_port}

@app.post("/webhooks/events")
async def handle_events(event: dict, db: Session = Depends(get_db)):
    """
    Subscribes to 'stock.low' events emitted by inventory-service.
    Automatically drafts a Purchase Order for replenishment.
    """
    event_name = event.get("event_name")
    payload = event.get("payload", {})
    org_id = event.get("org_id", "org-acroflow-main")

    if event_name == "stock.low":
        sku = payload.get("sku")
        name = payload.get("name", "Low Stock Item")
        reorder_qty = payload.get("reorder_quantity", 50)

        # Match vendor
        vendor = db.query(Vendor).filter_by(org_id=org_id).first()
        if not vendor:
            return {"status": "error", "detail": "No vendor found for replenishment"}

        po_seq = db.query(PurchaseOrder).filter_by(org_id=org_id).count() + 1
        po_number = f"PO-AUTO-{po_seq:04d}"

        # Standard estimated unit price
        unit_price = 1000.0
        total_val = reorder_qty * unit_price

        po = PurchaseOrder(
            id=str(uuid.uuid4()),
            org_id=org_id,
            po_number=po_number,
            vendor_id=vendor.id,
            status="Draft",
            total_amount=total_val,
            order_date="2026-09-24",
            expected_delivery="2026-10-10"
        )
        db.add(po)
        db.flush()

        item = POLineItem(
            id=str(uuid.uuid4()),
            org_id=org_id,
            po_id=po.id,
            product_sku=sku,
            description=f"Auto-Replenish: {name}",
            quantity_ordered=reorder_qty,
            unit_price=unit_price,
            total_price=total_val
        )
        db.add(item)
        db.commit()

        return {"status": "po_auto_drafted", "po_number": po_number, "sku": sku, "quantity": reorder_qty}

    return {"status": "ignored", "event_name": event_name}

# ----------------------------------------------------
# 2. Vendors Endpoints
# ----------------------------------------------------
@app.get("/procurement/vendors", response_model=List[VendorResponse])
def list_vendors(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    vendors = db.query(Vendor).filter_by(org_id=user_ctx.org_id).all()
    return [VendorResponse(**v.to_dict()) for v in vendors]

@app.post("/procurement/vendors", response_model=VendorResponse)
def create_vendor(req: VendorCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    v = Vendor(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        name=req.name,
        contact_email=req.contact_email,
        phone=req.phone,
        address=req.address,
        rating=req.rating or 4.5,
        payment_terms=req.payment_terms or "Net30"
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return VendorResponse(**v.to_dict())

# ----------------------------------------------------
# 3. Purchase Orders Endpoints
# ----------------------------------------------------
@app.get("/procurement/orders", response_model=List[PurchaseOrderResponse])
def list_purchase_orders(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    orders = db.query(PurchaseOrder).filter_by(org_id=user_ctx.org_id).order_by(PurchaseOrder.created_at.desc()).all()
    results = []
    for po in orders:
        po_dict = po.to_dict()
        po_dict["vendor_name"] = po.vendor.name if po.vendor else "Direct Supplier"
        results.append(PurchaseOrderResponse(**po_dict))
    return results

@app.post("/procurement/orders", response_model=PurchaseOrderResponse)
def create_purchase_order(req: PurchaseOrderCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    po_seq = db.query(PurchaseOrder).filter_by(org_id=user_ctx.org_id).count() + 1
    po_number = f"PO-2026-{po_seq:03d}"

    total_amount = sum(it.quantity_ordered * it.unit_price for it in req.items)

    po = PurchaseOrder(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        po_number=po_number,
        vendor_id=req.vendor_id,
        status="Approved",
        total_amount=total_amount,
        order_date=req.order_date or "2026-09-24",
        expected_delivery=req.expected_delivery
    )
    db.add(po)
    db.flush()

    for it in req.items:
        line = POLineItem(
            id=str(uuid.uuid4()),
            org_id=user_ctx.org_id,
            po_id=po.id,
            product_sku=it.product_sku,
            description=it.description,
            quantity_ordered=it.quantity_ordered,
            unit_price=it.unit_price,
            total_price=it.quantity_ordered * it.unit_price
        )
        db.add(line)

    db.commit()
    db.refresh(po)

    po_dict = po.to_dict()
    po_dict["vendor_name"] = po.vendor.name if po.vendor else "Direct Supplier"
    return PurchaseOrderResponse(**po_dict)

@app.get("/procurement/orders/{id}", response_model=PurchaseOrderDetailResponse)
def get_purchase_order(id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    items = [POLineItemResponse(**it.to_dict()) for it in po.items]
    grns = [GRNResponse(**g.to_dict()) for g in po.grns]
    bills = [VendorBillResponse(**b.to_dict()) for b in po.bills]

    po_dict = po.to_dict()
    po_dict["vendor_name"] = po.vendor.name if po.vendor else "Direct Supplier"
    po_dict["items"] = items
    po_dict["grns"] = grns
    po_dict["bills"] = bills
    return PurchaseOrderDetailResponse(**po_dict)

# ----------------------------------------------------
# 4. Goods Receipt Notes & Vendor Bills
# ----------------------------------------------------
@app.post("/procurement/orders/{id}/grn", response_model=GRNResponse)
async def record_goods_receipt(
    id: str,
    req: GRNCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    po = db.query(PurchaseOrder).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    grn_number = f"GRN-2026-{uuid.uuid4().hex[:6].upper()}"

    grn = GoodsReceiptNote(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        po_id=po.id,
        grn_number=grn_number,
        received_date="2026-09-24",
        received_by=req.received_by or "Warehouse Receiver",
        quantity_received=req.quantity_received,
        status=req.status or "Full"
    )
    db.add(grn)
    db.commit()
    db.refresh(grn)

    # Inform inventory microservice to increment physical stock
    first_item = po.items[0] if po.items else None
    if first_item:
        await event_bus.publish("grn.received", {
            "po_id": po.id,
            "product_sku": first_item.product_sku,
            "quantity_received": req.quantity_received
        }, org_id=user_ctx.org_id)

    return GRNResponse(**grn.to_dict())

@app.post("/procurement/orders/{id}/bill", response_model=VendorBillResponse)
def record_vendor_bill(
    id: str,
    req: VendorBillCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    po = db.query(PurchaseOrder).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    bill = VendorBill(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        po_id=po.id,
        bill_number=req.bill_number,
        billed_amount=req.billed_amount,
        status="Pending_Match"
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return VendorBillResponse(**bill.to_dict())

# ----------------------------------------------------
# 5. 3-Way Matching Engine
# ----------------------------------------------------
@app.post("/procurement/orders/{id}/three-way-match", response_model=ThreeWayMatchResponse)
def execute_three_way_match(id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    """
    Executes strict Enterprise 3-Way Matching verification:
    Condition 1: Total Ordered Quantity (PO) == Total Received Quantity (GRN)
    Condition 2: PO Total Amount == Billed Amount (Vendor Bill)
    If both hold with zero variance, approves match and unlocks payment disbursement.
    """
    po = db.query(PurchaseOrder).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    ordered_qty = sum(it.quantity_ordered for it in po.items)
    received_qty = sum(g.quantity_received for g in po.grns)
    billed_amt = sum(b.billed_amount for b in po.bills)

    if not po.grns or not po.bills:
        return ThreeWayMatchResponse(
            po_id=po.id,
            po_number=po.po_number,
            match_status="INCOMPLETE_DOCUMENTATION",
            ordered_quantity=ordered_qty,
            received_quantity=received_qty,
            po_amount=po.total_amount,
            billed_amount=billed_amt,
            is_verified=False,
            audit_notes="Missing Goods Receipt Note or Vendor Invoice Bill"
        )

    qty_matched = ordered_qty == received_qty
    amt_matched = abs(po.total_amount - billed_amt) < 0.01

    if qty_matched and amt_matched:
        po.status = "Matched_Approved"
        for b in po.bills:
            b.status = "Matched_Approved"
        db.commit()

        return ThreeWayMatchResponse(
            po_id=po.id,
            po_number=po.po_number,
            match_status="MATCHED_APPROVED",
            ordered_quantity=ordered_qty,
            received_quantity=received_qty,
            po_amount=po.total_amount,
            billed_amount=billed_amt,
            is_verified=True,
            audit_notes="Three-way verification confirmed. PO, GRN, and Vendor Bill match with zero discrepancy."
        )
    else:
        return ThreeWayMatchResponse(
            po_id=po.id,
            po_number=po.po_number,
            match_status="MISMATCH_DETECTED",
            ordered_quantity=ordered_qty,
            received_quantity=received_qty,
            po_amount=po.total_amount,
            billed_amount=billed_amt,
            is_verified=False,
            audit_notes=f"Variance detected: Qty ordered ({ordered_qty}) vs received ({received_qty}), Amount PO (${po.total_amount}) vs billed (${billed_amt})"
        )

# ----------------------------------------------------
# 6. Purchase Requisitions (PR) Engine
# ----------------------------------------------------
@app.get("/procurement/requisitions", response_model=List[RequisitionResponse])
def list_requisitions(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    prs = db.query(PurchaseRequisition).filter_by(org_id=user_ctx.org_id).all()
    return [RequisitionResponse(**r.to_dict()) for r in prs]

@app.post("/procurement/requisitions", response_model=RequisitionResponse)
def create_requisition(
    req: RequisitionCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    seq = db.query(PurchaseRequisition).count() + 1
    pr_num = f"PR-2026-{seq:04d}-{uuid.uuid4().hex[:4].upper()}"

    pr = PurchaseRequisition(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        pr_number=pr_num,
        department=req.department,
        requested_by=req.requested_by,
        estimated_budget=req.estimated_budget,
        status="Pending_Approval",
        notes=req.notes
    )
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return RequisitionResponse(**pr.to_dict())

@app.post("/procurement/requisitions/{id}/approve", response_model=RequisitionResponse)
def approve_requisition(
    id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    pr = db.query(PurchaseRequisition).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Purchase requisition not found")
    pr.status = "Approved"
    db.commit()
    db.refresh(pr)
    return RequisitionResponse(**pr.to_dict())

@app.post("/procurement/requisitions/{id}/convert-to-po", response_model=PurchaseOrderResponse)
async def convert_requisition_to_po(
    id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    pr = db.query(PurchaseRequisition).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail="Purchase requisition not found")

    vendor = db.query(Vendor).filter_by(org_id=user_ctx.org_id).first()
    if not vendor:
        raise HTTPException(status_code=400, detail="No vendor available to fulfill PO")

    po_seq = db.query(PurchaseOrder).count() + 1
    po_num = f"PO-PR-{po_seq:04d}-{uuid.uuid4().hex[:4].upper()}"

    po = PurchaseOrder(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        po_number=po_num,
        vendor_id=vendor.id,
        status="Approved",
        total_amount=pr.estimated_budget,
        order_date="2026-10-16",
        expected_delivery="2026-11-01"
    )
    db.add(po)

    # Add default line item based on requisition
    item = POLineItem(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        po_id=po.id,
        product_sku=f"SKU-PR-{pr.department[:3].upper()}",
        description=f"Procurement request from {pr.department}: {pr.notes or 'Standard Supply'}",
        quantity_ordered=1,
        unit_price=pr.estimated_budget,
        total_price=pr.estimated_budget
    )
    db.add(item)

    pr.status = "Converted_To_PO"
    db.commit()
    db.refresh(po)

    p_dict = po.to_dict()
    p_dict["vendor_name"] = vendor.name
    return PurchaseOrderResponse(**p_dict)

# ----------------------------------------------------
# 7. RFQ & Multi-Vendor Bid Evaluation Engine
# ----------------------------------------------------
@app.get("/procurement/rfqs", response_model=List[RFQResponse])
def list_rfqs(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    rfqs = db.query(RFQ).filter_by(org_id=user_ctx.org_id).all()
    return [RFQResponse(**r.to_dict()) for r in rfqs]

@app.post("/procurement/rfqs", response_model=RFQResponse)
def create_rfq(
    req: RFQCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    seq = db.query(RFQ).count() + 1
    rfq_num = f"RFQ-2026-{seq:04d}"

    rfq = RFQ(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        rfq_number=rfq_num,
        title=req.title,
        deadline=req.deadline,
        status="Open",
        vendor_bids="[]"
    )
    db.add(rfq)
    db.commit()
    db.refresh(rfq)
    return RFQResponse(**rfq.to_dict())

@app.post("/procurement/rfqs/{id}/bids", response_model=RFQResponse)
def submit_rfq_bid(
    id: str,
    req: RFQBidSubmitRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    import json
    rfq = db.query(RFQ).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    try:
        bids = json.loads(rfq.vendor_bids or "[]")
    except Exception:
        bids = []

    bids.append({
        "bid_id": str(uuid.uuid4()),
        "vendor_id": req.vendor_id,
        "vendor_name": req.vendor_name,
        "bid_amount": req.bid_amount,
        "delivery_lead_days": req.delivery_lead_days,
        "notes": req.notes,
        "status": "Submitted"
    })
    rfq.vendor_bids = json.dumps(bids)
    db.commit()
    db.refresh(rfq)
    return RFQResponse(**rfq.to_dict())

@app.post("/procurement/rfqs/{id}/award", response_model=RFQResponse)
def award_rfq(
    id: str,
    req: RFQAwardRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    import json
    rfq = db.query(RFQ).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not rfq:
        raise HTTPException(status_code=404, detail="RFQ not found")

    try:
        bids = json.loads(rfq.vendor_bids or "[]")
    except Exception:
        bids = []

    for b in bids:
        if b.get("vendor_id") == req.winning_vendor_id:
            b["status"] = "Awarded"
        else:
            b["status"] = "Rejected"

    rfq.vendor_bids = json.dumps(bids)
    rfq.status = "Awarded"
    db.commit()
    db.refresh(rfq)
    return RFQResponse(**rfq.to_dict())

# ----------------------------------------------------
# 8. Vendor Portal & Scorecard
# ----------------------------------------------------
@app.get("/procurement/vendors/{id}/scorecard", response_model=VendorScorecardResponse)
def get_vendor_scorecard(
    id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    vendor = db.query(Vendor).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    pos = db.query(PurchaseOrder).filter_by(vendor_id=vendor.id, org_id=user_ctx.org_id).all()
    total_pos = len(pos)
    matched_pos = sum(1 for p in pos if p.status == "Matched_Approved")
    compliance_rate = (matched_pos / total_pos * 100.0) if total_pos > 0 else 100.0
    tier = "Tier 1 Strategic Partner" if vendor.rating >= 4.5 else "Tier 2 Approved Supplier"

    return VendorScorecardResponse(
        vendor_id=vendor.id,
        vendor_name=vendor.name,
        rating=vendor.rating,
        total_pos_issued=total_pos,
        matched_pos_count=matched_pos,
        fulfillment_compliance_rate_percent=round(compliance_rate, 1),
        average_lead_time_days=12,
        tier_classification=tier
    )

