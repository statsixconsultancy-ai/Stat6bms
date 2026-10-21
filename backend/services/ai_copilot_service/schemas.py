from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class CopilotQueryRequest(BaseModel):
    query: str
    context_domain: Optional[str] = "all"


class CopilotQueryResponse(BaseModel):
    query: str
    intent: str
    answer: str
    sources: List[str] = []
    key_metrics: Dict[str, Any] = {}
    recommendations: List[str] = []


class AnomalyInsightResponse(BaseModel):
    id: str
    org_id: str
    category: str
    severity: str
    title: str
    description: str
    recommended_action: str
    is_resolved: bool


class CopilotSuggestionResponse(BaseModel):
    topic: str
    headline: str
    impact: str
    suggested_action: str


# --- Chatbot & Omnipresent Agentic Execution Schemas ---

class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: Optional[str] = None


class PageContext(BaseModel):
    module: Optional[str] = None
    route: Optional[str] = None
    selected_ids: Optional[List[str]] = []
    filters: Optional[Dict[str, Any]] = {}
    timezone: Optional[str] = "UTC"
    client_time: Optional[str] = None


class ChatbotRequest(BaseModel):
    message: Optional[str] = None
    prompt: Optional[str] = None
    query: Optional[str] = None
    conversation_id: Optional[str] = None
    history: Optional[List[ChatMessage]] = []
    page_context: Optional[PageContext] = None


class ScheduledTaskSummary(BaseModel):
    task_id: Optional[str] = None
    task_name: str
    target_service: str
    scheduled_for: str
    requires_hitl: bool = False
    hitl_approval_id: Optional[str] = None
    status: str = "PENDING"


class DataTable(BaseModel):
    columns: List[str]
    rows: List[List[Any]]


class ConfirmationCard(BaseModel):
    action: str
    title: str
    details: str


class ChatbotResponse(BaseModel):
    reply: str
    answer: Optional[str] = None
    intent: str
    immediate_data: Dict[str, Any] = {}
    scheduled_task: Optional[ScheduledTaskSummary] = None
    data_table: Optional[DataTable] = None
    confirmation_card: Optional[ConfirmationCard] = None
    sources: List[str] = []
    actions_suggested: List[str] = []
    output_tier: Optional[str] = "TIER_1_INTERNAL"
