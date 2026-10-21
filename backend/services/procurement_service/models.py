import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class Vendor(TenantModel):
    __tablename__ = "proc_vendors"

    name = Column(String(255), nullable=False, unique=True, index=True)
    contact_email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    rating = Column(Float, default=4.5)  # 1.0 to 5.0
    payment_terms = Column(String(50), default="Net30")  # Net30, Net60, Immediate

    purchase_orders = relationship("PurchaseOrder", back_populates="vendor")

class PurchaseOrder(TenantModel):
    __tablename__ = "proc_purchase_orders"

    po_number = Column(String(50), nullable=False, unique=True, index=True)
    vendor_id = Column(String(36), ForeignKey("proc_vendors.id"), nullable=False, index=True)
    status = Column(String(50), default="Draft", index=True)  # Draft, Approved, Received, Matched_Approved, Cancelled
    total_amount = Column(Float, default=0.0)
    order_date = Column(String(50), nullable=False)
    expected_delivery = Column(String(50), nullable=True)

    vendor = relationship("Vendor", back_populates="purchase_orders")
    items = relationship("POLineItem", back_populates="purchase_order", cascade="all, delete-orphan")
    grns = relationship("GoodsReceiptNote", back_populates="purchase_order", cascade="all, delete-orphan")
    bills = relationship("VendorBill", back_populates="purchase_order", cascade="all, delete-orphan")

class POLineItem(TenantModel):
    __tablename__ = "proc_po_line_items"

    po_id = Column(String(36), ForeignKey("proc_purchase_orders.id"), nullable=False, index=True)
    product_sku = Column(String(100), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    quantity_ordered = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    purchase_order = relationship("PurchaseOrder", back_populates="items")

class GoodsReceiptNote(TenantModel):
    __tablename__ = "proc_goods_receipt_notes"

    po_id = Column(String(36), ForeignKey("proc_purchase_orders.id"), nullable=False, index=True)
    grn_number = Column(String(50), nullable=False, unique=True, index=True)
    received_date = Column(String(50), nullable=False)
    received_by = Column(String(255), default="Warehouse Lead")
    quantity_received = Column(Integer, nullable=False)
    status = Column(String(50), default="Full")  # Full, Partial

    purchase_order = relationship("PurchaseOrder", back_populates="grns")

class VendorBill(TenantModel):
    __tablename__ = "proc_vendor_bills"

    po_id = Column(String(36), ForeignKey("proc_purchase_orders.id"), nullable=False, index=True)
    grn_id = Column(String(36), nullable=True)
    bill_number = Column(String(50), nullable=False, unique=True, index=True)
    billed_amount = Column(Float, nullable=False)
    status = Column(String(50), default="Pending_Match", index=True)  # Pending_Match, Matched_Approved, Mismatch

    purchase_order = relationship("PurchaseOrder", back_populates="bills")

class PurchaseRequisition(TenantModel):
    __tablename__ = "proc_purchase_requisitions"

    pr_number = Column(String(50), nullable=False, unique=True, index=True)
    department = Column(String(100), nullable=False, index=True)
    requested_by = Column(String(255), nullable=False)
    estimated_budget = Column(Float, nullable=False)
    status = Column(String(50), default="Pending_Approval", index=True)  # Pending_Approval, Approved, Converted_To_PO
    notes = Column(Text, nullable=True)

class RFQ(TenantModel):
    __tablename__ = "proc_rfqs"

    rfq_number = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    deadline = Column(String(50), nullable=False)
    status = Column(String(50), default="Open", index=True)  # Open, Closed, Awarded
    vendor_bids = Column(Text, default="[]")  # JSON string of bids

