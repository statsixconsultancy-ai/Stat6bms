import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class Invoice(TenantModel):
    __tablename__ = "fin_invoices"

    invoice_number = Column(String(50), nullable=False, unique=True, index=True)
    client_name = Column(String(255), nullable=False, index=True)
    client_id = Column(String(36), nullable=True)
    deal_id = Column(String(36), nullable=True, index=True)
    issue_date = Column(String(50), nullable=False)
    due_date = Column(String(50), nullable=False)
    status = Column(String(50), default="Sent", index=True)  # Draft, Sent, Paid, Overdue
    subtotal = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    balance_due = Column(Float, default=0.0)

    items = relationship("InvoiceItem", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

class InvoiceItem(TenantModel):
    __tablename__ = "fin_invoice_items"

    invoice_id = Column(String(36), ForeignKey("fin_invoices.id"), nullable=False, index=True)
    description = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)

    invoice = relationship("Invoice", back_populates="items")

class Payment(TenantModel):
    __tablename__ = "fin_payments"

    invoice_id = Column(String(36), ForeignKey("fin_invoices.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_date = Column(String(50), nullable=False)
    payment_method = Column(String(50), default="Wire Transfer")  # Wire Transfer, Stripe ACH, Credit Card
    reference_number = Column(String(100), nullable=True)

    invoice = relationship("Invoice", back_populates="payments")

class Expense(TenantModel):
    __tablename__ = "fin_expenses"

    category = Column(String(100), nullable=False, index=True)  # Cloud Hosting, Software, Travel, Office, Payroll
    vendor = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(String(50), nullable=False)
    status = Column(String(50), default="Approved", index=True)  # Pending, Approved, Paid
    approved_by = Column(String(255), default="CFO")

class JournalEntry(TenantModel):
    __tablename__ = "fin_journal_entries"

    entry_number = Column(String(50), nullable=False, unique=True, index=True)
    date = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)
    reference_type = Column(String(50), nullable=True)  # INVOICE_PAYMENT, EXPENSE, PAYROLL
    reference_id = Column(String(100), nullable=True)
    total_debit = Column(Float, default=0.0)
    total_credit = Column(Float, default=0.0)
    is_balanced = Column(Boolean, default=True)

    lines = relationship("JournalLine", back_populates="journal_entry", cascade="all, delete-orphan")

class JournalLine(TenantModel):
    __tablename__ = "fin_journal_lines"

    journal_entry_id = Column(String(36), ForeignKey("fin_journal_entries.id"), nullable=False, index=True)
    account_code = Column(String(50), nullable=False, index=True)  # 1010 Cash, 1200 AR, 4000 Revenue, etc.
    account_name = Column(String(100), nullable=False)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)

    journal_entry = relationship("JournalEntry", back_populates="lines")
