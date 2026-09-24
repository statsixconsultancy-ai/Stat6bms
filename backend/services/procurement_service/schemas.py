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
    total_amount: float
    order_date: str
    expected_delivery: Optional[str] = None

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
    po_amount: float
    billed_amount: float
    is_verified: bool
    audit_notes: str
