from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

# --- Lead Schemas ---
class LeadCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    company_name: str
    source: Optional[str] = "Website"
    score: Optional[int] = 50
    assigned_to: Optional[str] = "Sales Rep"
    notes: Optional[str] = None

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    company_name: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    score: Optional[int] = None
    assigned_to: Optional[str] = None
    notes: Optional[str] = None

class LeadResponse(BaseModel):
    id: str
    org_id: str
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    company_name: str
    status: str
    source: str
    score: int
    assigned_to: str
    notes: Optional[str] = None
    converted_contact_id: Optional[str] = None
    converted_company_id: Optional[str] = None
    converted_deal_id: Optional[str] = None

class LeadConvertRequest(BaseModel):
    deal_title: Optional[str] = None
    deal_amount: Optional[float] = 50000.0
    close_date: Optional[str] = None

class LeadConvertResponse(BaseModel):
    message: str
    lead_id: str
    company_id: str
    company_name: str
    contact_id: str
    deal_id: str
    deal_title: str
    deal_amount: float

# --- Contact & Company Schemas ---
class ContactCreate(BaseModel):
    company_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    job_title: Optional[str] = "Executive"
    is_primary: Optional[bool] = False
    role_type: Optional[str] = "Decision Maker"

class ContactResponse(BaseModel):
    id: str
    org_id: str
    company_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    job_title: str
    is_primary: bool
    role_type: str = "Decision Maker"

class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = "Technology"
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    annual_revenue: Optional[float] = 0.0
    tier: Optional[str] = "Tier 2"
    account_owner: Optional[str] = "Sales Lead"
    parent_company_id: Optional[str] = None

class CompanyResponse(BaseModel):
    id: str
    org_id: str
    name: str
    industry: str
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    annual_revenue: float
    tier: str
    account_owner: str
    parent_company_id: Optional[str] = None

class CompanyDetailResponse(CompanyResponse):
    contacts: List[ContactResponse] = []
    deals_count: int = 0
    total_deal_value: float = 0.0

# --- Deal Schemas ---
class DealCreate(BaseModel):
    title: Optional[str] = None
    name: Optional[str] = None
    company_id: Optional[str] = None
    contact_id: Optional[str] = None
    amount: Optional[float] = None
    value: Optional[float] = None
    stage: Optional[str] = "Prospecting"
    probability: Optional[int] = 20
    close_date: Optional[str] = None
    owner: Optional[str] = "Account Executive"
    pipeline_name: Optional[str] = "Standard Enterprise"
    currency: Optional[str] = "USD"
    stage_gate_checklist: Optional[Dict[str, Any]] = None

class DealUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    stage: Optional[str] = None
    probability: Optional[int] = None
    close_date: Optional[str] = None
    owner: Optional[str] = None
    stage_gate_checklist: Optional[Dict[str, Any]] = None

class StageUpdateRequest(BaseModel):
    stage: str
    probability: Optional[int] = None
    checklist_verification: Optional[Dict[str, bool]] = None

class DealResponse(BaseModel):
    id: str
    org_id: str
    title: str
    company_id: Optional[str] = None
    contact_id: Optional[str] = None
    company_name: Optional[str] = None
    amount: float
    stage: str
    probability: int
    close_date: Optional[str] = None
    owner: str
    pipeline_name: str = "Standard Enterprise"
    currency: str = "USD"
    stage_gate_checklist: Dict[str, Any] = {}
    converted_invoice_id: Optional[str] = None
    converted_project_id: Optional[str] = None

class DealConversionResponse(BaseModel):
    deal_id: str
    invoice_id: Optional[str] = None
    project_id: Optional[str] = None
    status: str
    message: str

# --- CPQ & E-Signature Schemas ---
class QuoteItemCreate(BaseModel):
    description: Optional[str] = None
    item: Optional[str] = None
    quantity: int = 1
    unit_price: float = 0.0
    total: Optional[float] = None

class QuoteItemResponse(BaseModel):
    id: str
    description: str
    quantity: int
    unit_price: float
    total_price: float

class QuoteCreate(BaseModel):
    deal_id: Optional[str] = None
    company_id: Optional[str] = None
    company_name: Optional[str] = None
    quote_number: Optional[str] = None
    valid_until: Optional[str] = None
    total_amount: Optional[float] = None
    status: Optional[str] = "Draft"
    tiered_discount_percent: Optional[float] = 0.0
    items: Optional[List[QuoteItemCreate]] = None
    line_items: Optional[List[QuoteItemCreate]] = None

class QuoteResponse(BaseModel):
    id: str
    quote_number: str
    deal_id: Optional[str] = None
    company_id: Optional[str] = None
    status: str
    subtotal: float
    tax_rate: float
    tax_amount: float
    discount_amount: float
    tiered_discount_percent: float = 0.0
    margin_floor_approved: bool = True
    total_amount: float
    valid_until: Optional[str] = None
    e_signature_status: str = "draft"
    e_signature_audit: Dict[str, Any] = {}
    items: List[QuoteItemResponse] = []

class QuoteESignRequest(BaseModel):
    signer_name: Optional[str] = "Authorized Signatory"
    signer_email: Optional[str] = "client@acroflow.enterprise"
    signer_role: Optional[str] = "Executive"
    ip_address: Optional[str] = "127.0.0.1"
    otp_code: Optional[str] = "123456"
    signature_data: Optional[str] = "Signed electronically"

class QuoteESignResponse(BaseModel):
    quote_id: str
    quote_number: str
    status: Optional[str] = "Signed"
    e_signature_status: str
    signed_at: str
    audit_hash: str
    signer_email: Optional[str] = None
    e_signature_audit_hash: Optional[str] = None
    message: str

# --- Pipeline & Appointments Schemas ---
class PipelineCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_default: bool = False
    stages: List[Dict[str, Any]]

class PipelineResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str] = None
    is_default: bool
    stages: List[Dict[str, Any]]

class AppointmentCreate(BaseModel):
    contact_id: Optional[str] = None
    deal_id: Optional[str] = None
    title: str
    host_email: Optional[str] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None
    scheduled_at: Optional[Any] = None
    scheduled_time: Optional[Any] = None
    duration_minutes: int = 30
    meeting_link: Optional[str] = None

class AppointmentResponse(BaseModel):
    id: str
    org_id: str
    contact_id: Optional[str] = None
    deal_id: Optional[str] = None
    host_user_id: Optional[str] = None
    title: str
    scheduled_at: Optional[str] = None
    duration_minutes: int = 30
    status: str = "Scheduled"
    meeting_link: Optional[str] = None
    guest_name: Optional[str] = None
    guest_email: Optional[str] = None


# --- Summary ---
class CRMSummaryResponse(BaseModel):
    total_pipeline_value: float
    total_deals_count: int
    won_revenue: float
    win_rate_percent: float
    leads_count: int
    qualified_leads_count: int
