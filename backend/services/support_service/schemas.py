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

class TicketDetailResponse(TicketResponse):
    messages: List[TicketMessageResponse] = []

class SLAAnalyticsResponse(BaseModel):
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    sla_compliance_rate_percent: float
    average_resolution_hours: float
