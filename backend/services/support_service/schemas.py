from typing import Optional, List
from pydantic import BaseModel

# --- Ticket Message Schemas ---
class TicketMessageCreate(BaseModel):
    sender_name: str
    sender_type: Optional[str] = "Agent"
    message: str

class TicketMessageResponse(BaseModel):
    id: str
    ticket_id: str
    sender_name: str
    sender_type: str
    message: str
    created_at: str

# --- Ticket Schemas ---
class TicketCreate(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    description: Optional[str] = None
    priority: Optional[str] = "Medium"
    assigned_to: Optional[str] = "Tier 1 Specialist"

class TicketStatusUpdate(BaseModel):
    status: str

class TicketResponse(BaseModel):
    id: str
    org_id: str
    ticket_number: str
    customer_name: str
    customer_email: str
    subject: str
    description: Optional[str] = None
    priority: str
    status: str
    assigned_to: str
    sla_target_hours: float
    elapsed_hours: float
    is_breached: bool
    sla_policy: Optional[str] = "Standard B2B SLA"
    resolution_due_at: Optional[str] = None
    csat_score: Optional[int] = None
    nps_score: Optional[int] = None
    feedback_comment: Optional[str] = None
    tags: Optional[str] = "[]"

class TicketDetailResponse(TicketResponse):
    messages: List[TicketMessageResponse] = []

class TicketFeedbackRequest(BaseModel):
    csat_score: int  # 1 to 5
    nps_score: Optional[int] = None  # 0 to 10
    feedback_comment: Optional[str] = None

class Customer360ContextResponse(BaseModel):
    customer_email: str
    customer_name: str
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    average_csat: float
    recent_tickets: List[TicketResponse] = []
    associated_crm_context: dict = {}

class KBArticleCreate(BaseModel):
    title: str
    category: Optional[str] = "General"
    content: str
    is_published: Optional[bool] = True

class KBArticleResponse(BaseModel):
    id: str
    org_id: str
    title: str
    category: str
    content: str
    is_published: bool
    view_count: int
    helpful_votes: int

class SLAAnalyticsResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    sla_compliance_rate_percent: float
    average_resolution_hours: float

