from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AutomationRuleCreate(BaseModel):
    name: str
    trigger_event: str
    condition_code: Optional[str] = "True"
    action_type: str
    action_config: Optional[str] = None
    is_active: Optional[bool] = True

class AutomationRuleResponse(BaseModel):
    id: str
    org_id: str
    name: str
    trigger_event: str
    condition_code: str
    action_type: str
    action_config: Optional[str] = None
    is_active: bool
    execution_count: int

class AutomationLogResponse(BaseModel):
    id: str
    org_id: str
    rule_id: str
    trigger_event: str
    status: str
    details: Optional[str] = None
    created_at: str

class TriggerRuleRequest(BaseModel):
    mock_payload: Dict[str, Any]

class TriggerRuleResponse(BaseModel):
    rule_id: str
    status: str
    condition_evaluated: bool
    action_taken: str
