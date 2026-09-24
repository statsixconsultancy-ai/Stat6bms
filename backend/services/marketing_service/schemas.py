from typing import Optional, List
from pydantic import BaseModel

# --- Campaign Schemas ---
class CampaignCreate(BaseModel):
    name: str
    type: Optional[str] = "Paid Search"
    status: Optional[str] = "Active"
    budget: float = 0.0
    actual_spend: float = 0.0
    attributed_revenue: float = 0.0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    target_audience: Optional[str] = "Enterprise B2B Decision Makers"

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    actual_spend: Optional[float] = None
    attributed_revenue: Optional[float] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    target_audience: Optional[str] = None

class CampaignResponse(BaseModel):
    id: str
    org_id: str
    name: str
    type: str
    status: str
    budget: float
    actual_spend: float
    attributed_revenue: float
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    target_audience: str
    roi_percent: Optional[float] = 0.0

# --- Landing Page Schemas ---
class LandingPageCreate(BaseModel):
    campaign_id: Optional[str] = None
    title: str
    slug: str

class LandingPageResponse(BaseModel):
    id: str
    org_id: str
    campaign_id: Optional[str] = None
    title: str
    slug: str
    views_count: int
    conversions_count: int
    bounce_rate: float
    conversion_rate_percent: float = 0.0

# --- Lead Form & Public Submission Schemas ---
class LeadFormCreate(BaseModel):
    campaign_id: Optional[str] = None
    name: str
    fields_config: Optional[str] = '["first_name", "last_name", "email", "phone", "company_name"]'
    is_active: Optional[bool] = True

class LeadFormResponse(BaseModel):
    id: str
    org_id: str
    campaign_id: Optional[str] = None
    name: str
    fields_config: str
    is_active: bool

class PublicFormSubmitRequest(BaseModel):
    form_id: Optional[str] = None
    campaign_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    company_name: str
    phone: Optional[str] = None
    utm_source: Optional[str] = "direct"
    utm_medium: Optional[str] = "web"
    utm_campaign: Optional[str] = "enterprise_bms_launch"
    notes: Optional[str] = None

class FormSubmissionResponse(BaseModel):
    id: str
    form_id: Optional[str] = None
    campaign_id: Optional[str] = None
    email: str
    first_name: str
    last_name: str
    company_name: str
    status: str = "received"
    message: str = "Submission received and lead dispatched to CRM engine."

# --- UTM & ROI Schemas ---
class UTMTrackingResponse(BaseModel):
    id: str
    source: str
    medium: str
    campaign_name: str
    clicks: int
    conversions: int
    spend: float

class MarketingROIResponse(BaseModel):
    total_campaigns: int
    active_campaigns: int
    total_marketing_spend: float
    total_attributed_revenue: float
    blended_roi_percent: float
    total_conversions: int
    blended_cac: float
