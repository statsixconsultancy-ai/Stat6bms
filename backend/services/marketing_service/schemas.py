from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel

# --- Campaign Schemas ---
class CampaignCreate(BaseModel):
    name: str
    type: Optional[str] = "Paid Search"
    status: Optional[str] = "Active"
    budget: float = 0.0
    actual_spend: float = 0.0
    spent: Optional[float] = None
    attributed_revenue: float = 0.0
    revenue_attributed: Optional[float] = None
    leads_generated: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    target_audience: Optional[str] = "Enterprise B2B Decision Makers"
    utm_source: Optional[str] = None
    utm_medium: Optional[str] = None
    utm_campaign: Optional[str] = None

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
    spent: float = 0.0
    attributed_revenue: float
    revenue_attributed: float = 0.0
    leads_generated: int = 0
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

# --- Drip Journey & Broadcast Schemas ---
class DripJourneyCreate(BaseModel):
    name: str
    trigger_event: Optional[str] = "lead.captured"
    steps_config: Optional[str] = '[{"step": 1, "channel": "email", "delay_hours": 0, "template": "Welcome"}, {"step": 2, "channel": "whatsapp", "delay_hours": 48, "template": "Demo Invite"}]'
    steps: Optional[List[Union[str, Dict[str, Any]]]] = None
    is_active: Optional[bool] = True

class DripJourneyResponse(BaseModel):
    id: str
    org_id: str
    name: str
    trigger_event: str
    steps_config: str
    steps: List[Union[str, Dict[str, Any]]] = []
    is_active: bool
    enrolled_count: int
    completed_count: int
    converted_count: int = 0

class BroadcastCampaignCreate(BaseModel):
    name: str
    channel: Optional[str] = "email"
    target_segment: Optional[str] = "All Leads"
    segment_filter: Optional[str] = None
    recipient_count: Optional[int] = None
    message_template: str
    scheduled_at: Optional[str] = None

class BroadcastCampaignResponse(BaseModel):
    id: str
    org_id: str
    name: str
    channel: str
    target_segment: str
    message_template: str
    scheduled_at: Optional[str] = None
    status: str
    recipient_count: int
    delivered_count: int
    opened_count: int = 0
    open_rate: float
    click_rate: float

class ROIAttributionRequest(BaseModel):
    campaign_id: Optional[str] = None
    deal_id: Optional[str] = None
    invoice_id: Optional[str] = None
    attributed_revenue: Optional[float] = None
    deal_value: Optional[float] = None
    attribution_model: Optional[str] = "last_touch"  # first_touch, last_touch, linear
    model: Optional[str] = None
    notes: Optional[str] = None

class ROIAttributionResponse(BaseModel):
    campaign_id: str
    campaign_name: str
    deal_value: Optional[float] = None
    model: Optional[str] = None
    new_spend: float
    new_attributed_revenue: float
    calculated_roi_percent: float
    attribution_status: str = "attributed"
    touchpoints: List[Dict[str, Any]] = []

