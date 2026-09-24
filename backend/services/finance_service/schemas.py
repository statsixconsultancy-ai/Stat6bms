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
