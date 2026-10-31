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
    reference: Optional[str] = None
    date: str
    entry_date: Optional[str] = None
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
    total_revenue: float = 0.0
    cost_of_goods_sold: float
    gross_profit: float
    operating_expenses: float
    total_expenses: float = 0.0
    ebitda: float
    net_profit: float = 0.0
    net_operating_margin_percent: float
    profit_margin_percent: float = 0.0

class CashFlowResponse(BaseModel):
    cash_at_start: float
    cash_inflows_customer_receipts: float
    cash_inflows: float = 0.0
    cash_outflows_expenses: float
    cash_outflows_payroll: float
    cash_outflows: float = 0.0
    net_operating_cash_flow: float
    net_cash_flow: float = 0.0
    cash_at_close: float

# --- Subscriptions & Recurring Billing ---
class SubscriptionCreate(BaseModel):
    customer_name: Optional[str] = None
    client_name: Optional[str] = None
    customer_email: Optional[str] = "billing@enterprise.corp"
    plan_name: Optional[str] = "Enterprise Tier"
    billing_interval: Optional[str] = "monthly"
    billing_cycle: Optional[str] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    quantity: Optional[int] = 1
    next_billing_date: Optional[str] = None
    payment_method: Optional[str] = "Credit Card"

class SubscriptionResponse(BaseModel):
    id: str
    org_id: str
    customer_name: str
    client_name: str = ""
    customer_email: str
    plan_name: str
    billing_interval: str
    billing_cycle: str = "MONTHLY"
    unit_price: float
    amount: float = 0.0
    quantity: int
    total_recurring_amount: float
    next_billing_date: str
    status: str
    payment_method: str
    auto_renew: bool

# --- Tax Calculation Engine (GST / VAT) ---
class TaxCalculationRequest(BaseModel):
    subtotal: Optional[float] = None
    amount: Optional[float] = None
    place_of_supply: Optional[str] = "Intra-State"
    tax_rate: Optional[float] = None
    gst_rate: Optional[float] = None
    tax_regime: Optional[str] = "GST_IN"
    is_interstate: Optional[bool] = None
    hsn_sac_code: Optional[str] = "998314"

class TaxCalculationResponse(BaseModel):
    subtotal: float
    taxable_amount: float = 0.0
    tax_rate: float
    cgst_amount: float
    cgst: float = 0.0
    sgst_amount: float
    sgst: float = 0.0
    igst_amount: float
    igst: float = 0.0
    total_tax: float
    gross_amount: float
    total_with_tax: float = 0.0

# --- Expense OCR Scanner ---
class ExpenseOCRRequest(BaseModel):
    receipt_text: Optional[str] = None
    image_url: Optional[str] = None

class ExpenseOCRResponse(BaseModel):
    vendor: str
    merchant: str = ""
    amount: float
    date: str
    category: str
    tax_amount: float
    confidence_score: float
    policy_violation: bool = False
    status: str = "EXTRACTED"

