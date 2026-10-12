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


# --- Temporal Scheduled Tasks Schemas ---
class ScheduledTaskCreate(BaseModel):
    task_name: str
    target_service: str
    action_type: str
    payload: Dict[str, Any]
    scheduled_for: str  # ISO-8601 string e.g. "2026-10-09T10:00:00Z"
    precondition_check: Optional[Dict[str, Any]] = None
    requires_hitl: Optional[bool] = False
    conversation_id: Optional[str] = None


class ScheduledTaskResponse(BaseModel):
    id: str
    org_id: str
    task_name: str
    target_service: str
    action_type: str
    payload: str
    scheduled_for: str
    precondition_check: Optional[str] = None
    status: str
    requires_hitl: bool
    hitl_approval_id: Optional[str] = None
    executed_at: Optional[str] = None
    execution_result: Optional[str] = None
    created_at: str


# --- Human-In-The-Loop (HITL) Schemas ---
class HITLApprovalCreate(BaseModel):
    task_id: Optional[str] = None
    title: str
    summary: str
    action_diff: Dict[str, Any]
    assigned_approver_role: Optional[str] = "FINANCE_MANAGER"
    risk_level: Optional[str] = "HIGH"
    expires_at: Optional[str] = None


class HITLApprovalResponse(BaseModel):
    id: str
    org_id: str
    task_id: Optional[str] = None
    requested_by: str
    assigned_approver_role: str
    risk_level: str
    title: str
    summary: str
    action_diff: str
    status: str
    decision_by_user_id: Optional[str] = None
    decision_notes: Optional[str] = None
    decided_at: Optional[str] = None
    expires_at: Optional[str] = None
    created_at: str


class HITLDecisionRequest(BaseModel):
    decision: str  # APPROVED, REJECTED
    decision_notes: Optional[str] = None

