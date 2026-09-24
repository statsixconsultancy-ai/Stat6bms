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
