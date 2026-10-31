from typing import Optional, List
from pydantic import BaseModel

# --- Vendor Schemas ---
class VendorCreate(BaseModel):
    name: str
    contact_email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    rating: Optional[float] = 4.5
    payment_terms: Optional[str] = "Net30"

class VendorResponse(BaseModel):
    id: str
    org_id: str
    name: str
    contact_email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    rating: float
    payment_terms: str

# --- PO Line Items & PO Schemas ---
class POLineItemCreate(BaseModel):
    product_sku: str
    description: str
    quantity_ordered: int
    unit_price: float

class POLineItemResponse(BaseModel):
    id: str
    product_sku: str
    description: str
    quantity_ordered: int
    unit_price: float
    total_price: float

class PurchaseOrderCreate(BaseModel):
    vendor_id: str
    order_date: Optional[str] = "2026-09-24"
    expected_delivery: Optional[str] = "2026-10-15"
    items: List[POLineItemCreate]

class PurchaseOrderResponse(BaseModel):
    id: str
    org_id: str
    po_number: str
    vendor_id: str
    vendor_name: Optional[str] = None
    status: str
    three_way_match_status: Optional[str] = None
    total_amount: float
    order_date: str
    expected_delivery: Optional[str] = None
    expected_delivery_date: Optional[str] = None

# --- Goods Receipt Note (GRN) ---
class GRNCreate(BaseModel):
    received_by: Optional[str] = "Warehouse Receiver"
    quantity_received: int
    status: Optional[str] = "Full"

class GRNResponse(BaseModel):
    id: str
    org_id: str
    po_id: str
    grn_number: str
    received_date: str
    received_by: str
    quantity_received: int
    status: str

# --- Vendor Bill & 3-Way Match ---
class VendorBillCreate(BaseModel):
    bill_number: str
    billed_amount: float

class VendorBillResponse(BaseModel):
    id: str
    org_id: str
    po_id: str
    grn_id: Optional[str] = None
    bill_number: str
    billed_amount: float
    status: str

class PurchaseOrderDetailResponse(PurchaseOrderResponse):
    items: List[POLineItemResponse] = []
    grns: List[GRNResponse] = []
    bills: List[VendorBillResponse] = []

class ThreeWayMatchResponse(BaseModel):
    po_id: str
    po_number: str
    match_status: str  # MATCHED_APPROVED, QUANTITY_MISMATCH, AMOUNT_MISMATCH, INCOMPLETE_DOCUMENTATION
    ordered_quantity: int
    received_quantity: int
    grn_accepted_qty: int = 0
    po_amount: float
    billed_amount: float
    is_verified: bool
    audit_notes: str

# --- Purchase Requisition Schemas ---
class RequisitionCreate(BaseModel):
    department: str
    requested_by: Optional[str] = "Department Lead"
    estimated_budget: Optional[float] = None
    estimated_cost: Optional[float] = None
    item_description: Optional[str] = None
    notes: Optional[str] = None

class RequisitionResponse(BaseModel):
    id: str
    org_id: str
    pr_number: str
    department: str
    requested_by: str
    estimated_budget: float
    estimated_cost: float = 0.0
    item_description: str = ""
    status: str
    notes: Optional[str] = None

# --- RFQ (Request for Quotation) Schemas ---
class RFQCreate(BaseModel):
    title: str
    deadline: Optional[str] = "2026-11-25"
    item_specification: Optional[str] = None
    target_quantity: Optional[int] = 100
    estimated_budget: Optional[float] = 50000.0

class RFQBidSubmitRequest(BaseModel):
    vendor_id: str
    vendor_name: str
    bid_amount: float
    delivery_lead_days: int
    notes: Optional[str] = None

class RFQResponse(BaseModel):
    id: str
    org_id: str
    rfq_number: str
    title: str
    deadline: str
    item_specification: str = "Enterprise Grade Spec"
    target_quantity: int = 100
    estimated_budget: float = 50000.0
    status: str
    vendor_bids: str

class RFQAwardRequest(BaseModel):
    winning_vendor_id: str

# --- Vendor Scorecard Schemas ---
class VendorScorecardResponse(BaseModel):
    vendor_id: str
    vendor_name: str
    rating: float
    overall_score: float = 95.0
    total_pos_issued: int
    total_pos: int = 0
    matched_pos_count: int
    fulfillment_compliance_rate_percent: float
    on_time_delivery_rate: float = 98.0
    quality_acceptance_rate: float = 99.2
    average_lead_time_days: int
    tier_classification: str
    tier_recommendation: str = "Tier 1 Strategic Partner"

