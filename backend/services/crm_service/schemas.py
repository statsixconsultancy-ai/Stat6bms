from typing import Optional, List
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

class CompanyCreate(BaseModel):
    name: str
    industry: Optional[str] = "Technology"
    website: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    annual_revenue: Optional[float] = 0.0
    tier: Optional[str] = "Tier 2"
    account_owner: Optional[str] = "Sales Lead"

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

class CompanyDetailResponse(CompanyResponse):
    contacts: List[ContactResponse] = []
    deals_count: int = 0
    total_deal_value: float = 0.0

# --- Deal Schemas ---
class DealCreate(BaseModel):
    title: str
    company_id: Optional[str] = None
    contact_id: Optional[str] = None
    amount: float
    stage: Optional[str] = "Prospecting"
    probability: Optional[int] = 20
    close_date: Optional[str] = None
    owner: Optional[str] = "Account Executive"

class DealUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[float] = None
    stage: Optional[str] = None
    probability: Optional[int] = None
    close_date: Optional[str] = None
    owner: Optional[str] = None

class StageUpdateRequest(BaseModel):
    stage: str
    probability: Optional[int] = None

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

# --- Quote Schemas ---
class QuoteItemCreate(BaseModel):
    description: str
    quantity: int = 1
    unit_price: float

class QuoteItemResponse(BaseModel):
    id: str
    description: str
    quantity: int
    unit_price: float
    total_price: float

class QuoteCreate(BaseModel):
    deal_id: Optional[str] = None
    company_id: Optional[str] = None
    valid_until: Optional[str] = None
    items: List[QuoteItemCreate]

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
    total_amount: float
    valid_until: Optional[str] = None
    items: List[QuoteItemResponse] = []

# --- Summary ---
class CRMSummaryResponse(BaseModel):
    total_pipeline_value: float
    total_deals_count: int
    won_revenue: float
    win_rate_percent: float
    leads_count: int
    qualified_leads_count: int
