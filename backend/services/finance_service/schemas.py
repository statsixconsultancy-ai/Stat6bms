from typing import Optional, List
from pydantic import BaseModel

# --- Invoice Schemas ---
class InvoiceItemCreate(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float

class InvoiceItemResponse(BaseModel):
    id: str
    description: str
    quantity: int
    unit_price: float
    total_price: float

class InvoiceCreate(BaseModel):
    invoice_number: Optional[str] = None
    client_name: str
    deal_id: Optional[str] = None
    issue_date: Optional[str] = "2026-09-24"
    due_date: Optional[str] = "2026-10-24"
    items: List[InvoiceItemCreate]

class PaymentCreate(BaseModel):
    amount: float
    payment_method: Optional[str] = "Wire Transfer"
    reference_number: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    invoice_id: str
    amount: float
    payment_date: str
    payment_method: str
    reference_number: Optional[str] = None

class InvoiceResponse(BaseModel):
    id: str
    org_id: str
    invoice_number: str
    client_name: str
    deal_id: Optional[str] = None
    issue_date: str
    due_date: str
    status: str
    subtotal: float
    tax_amount: float
    total_amount: float
    balance_due: float

class InvoiceDetailResponse(InvoiceResponse):
    items: List[InvoiceItemResponse] = []
    payments: List[PaymentResponse] = []

# --- Expense Schemas ---
class ExpenseCreate(BaseModel):
    category: str
    vendor: str
    amount: float
    date: Optional[str] = "2026-09-24"
    approved_by: Optional[str] = "CFO"

class ExpenseResponse(BaseModel):
    id: str
    org_id: str
    category: str
    vendor: str
    amount: float
    date: str
    status: str
    approved_by: str

# --- Double-Entry Ledger Schemas ---
class JournalLineResponse(BaseModel):
    id: str
    account_code: str
    account_name: str
    debit: float
    credit: float

class JournalEntryResponse(BaseModel):
    id: str
    org_id: str
    entry_number: str
    date: str
    description: str
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    total_debit: float
    total_credit: float
    is_balanced: bool
    lines: List[JournalLineResponse] = []

# --- Financial Reports ---
class ProfitAndLossResponse(BaseModel):
    period: str
    operating_revenue: float
    cost_of_goods_sold: float
    gross_profit: float
    operating_expenses: float
    ebitda: float
    net_operating_margin_percent: float

class CashFlowResponse(BaseModel):
    cash_at_start: float
    cash_inflows_customer_receipts: float
    cash_outflows_expenses: float
    cash_outflows_payroll: float
    net_operating_cash_flow: float
    cash_at_close: float

# --- Subscriptions & Recurring Billing ---
class SubscriptionCreate(BaseModel):
    customer_name: str
    customer_email: str
    plan_name: Optional[str] = "Enterprise Tier"
    billing_interval: Optional[str] = "monthly"
    unit_price: float
    quantity: Optional[int] = 1
    next_billing_date: Optional[str] = None
    payment_method: Optional[str] = "Credit Card"

class SubscriptionResponse(BaseModel):
    id: str
    org_id: str
    customer_name: str
    customer_email: str
    plan_name: str
    billing_interval: str
    unit_price: float
    quantity: int
    total_recurring_amount: float
    next_billing_date: str
    status: str
    payment_method: str
    auto_renew: bool

# --- Tax Calculation Engine (GST / VAT) ---
class TaxCalculationRequest(BaseModel):
    subtotal: float
    place_of_supply: str  # e.g., "Inter-State", "Intra-State", "California", "Karnataka"
    tax_rate: Optional[float] = 0.18

class TaxCalculationResponse(BaseModel):
    subtotal: float
    tax_rate: float
    cgst_amount: float
    sgst_amount: float
    igst_amount: float
    total_tax: float
    gross_amount: float

# --- Expense OCR Scanner ---
class ExpenseOCRRequest(BaseModel):
    receipt_text: Optional[str] = None
    image_url: Optional[str] = None

class ExpenseOCRResponse(BaseModel):
    vendor: str
    amount: float
    date: str
    category: str
    tax_amount: float
    confidence_score: float
    status: str = "EXTRACTED"

