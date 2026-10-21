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


# =========================================================================
# Phase 5: Visual Workflows, Unified Approvals & Zoho Migration Schemas
# =========================================================================

# --- Visual Workflows Schemas ---
class WorkflowNode(BaseModel):
    id: str
    type: str  # TRIGGER, CONDITION, ACTION, DELAY
    title: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    next_node_ids: Optional[List[str]] = []

class WorkflowDefinitionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_event: str
    nodes: List[Dict[str, Any]]
    is_active: Optional[bool] = True

class WorkflowDefinitionResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str] = None
    trigger_event: str
    nodes: str
    is_active: bool
    execution_count: int
    created_at: str

class WorkflowExecutionResponse(BaseModel):
    id: str
    org_id: str
    workflow_id: str
    status: str
    current_node_id: Optional[str] = None
    step_history: str
    error_message: Optional[str] = None
    created_at: str

class TriggerWorkflowRequest(BaseModel):
    payload: Dict[str, Any]


# --- Unified Multi-Module Approvals Schemas ---
class ApprovalRequestCreate(BaseModel):
    module: str  # PROCUREMENT, FINANCE, CRM, HR
    record_type: str  # PURCHASE_REQUISITION, QUOTE_DISCOUNT, LEAVE_REQUEST, EXPENSE, INVOICE
    record_id: str
    requester_name: Optional[str] = None
    approver_role: Optional[str] = "MANAGER"
    approver_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    amount: Optional[float] = 0.0

class ApprovalRequestResponse(BaseModel):
    id: str
    org_id: str
    module: str
    record_type: str
    record_id: str
    requester_id: str
    requester_name: Optional[str] = None
    approver_role: str
    approver_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    amount: float
    status: str
    decision_by_id: Optional[str] = None
    decision_notes: Optional[str] = None
    delegated_to_id: Optional[str] = None
    decided_at: Optional[str] = None
    created_at: str

class ApprovalDecisionRequest(BaseModel):
    action: str  # APPROVE, REJECT, DELEGATE
    notes: Optional[str] = None
    delegate_to_id: Optional[str] = None


# --- AI Natural Language Workflow Generator ---
class AIGenerateWorkflowRequest(BaseModel):
    prompt: str

class AIGenerateWorkflowResponse(BaseModel):
    name: str
    description: str
    trigger_event: str
    nodes: List[Dict[str, Any]]
    explanation: str


# --- Zoho One 1-Click Migration Schemas ---
class ZohoMigrationRequest(BaseModel):
    zoho_crm: Optional[Dict[str, List[Dict[str, Any]]]] = None
    zoho_books: Optional[Dict[str, List[Dict[str, Any]]]] = None
    zoho_people: Optional[Dict[str, List[Dict[str, Any]]]] = None
    zoho_inventory: Optional[Dict[str, List[Dict[str, Any]]]] = None

class ZohoMigrationResponse(BaseModel):
    job_id: str
    status: str
    total_records: int
    records_migrated: Dict[str, int]
    canonical_mappings: List[Dict[str, str]]
    validation_errors: List[str]
    elapsed_ms: float


