import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class AutomationRule(TenantModel):
    __tablename__ = "auto_rules"

    name = Column(String(255), nullable=False, index=True)
    trigger_event = Column(String(100), nullable=False, index=True)  # deal.won, stock.low, ticket.urgent, etc.
    condition_code = Column(String(255), default="True")  # e.g., "amount >= 100000"
    action_type = Column(String(100), nullable=False)     # DISPATCH_NOTIFICATION, LOG_COMPLIANCE, EXECUTE_WEBHOOK
    action_config = Column(Text, nullable=True)           # JSON configuration for payload
    is_active = Column(Boolean, default=True, index=True)
    execution_count = Column(Integer, default=0)

    logs = relationship("AutomationLog", back_populates="rule", cascade="all, delete-orphan")

class AutomationLog(TenantModel):
    __tablename__ = "auto_logs"

    rule_id = Column(String(36), ForeignKey("auto_rules.id"), nullable=False, index=True)
    trigger_event = Column(String(100), nullable=False)
    status = Column(String(50), default="Success")  # Success, Skipped, Error
    details = Column(Text, nullable=True)

    rule = relationship("AutomationRule", back_populates="logs")


class ScheduledTask(TenantModel):
    __tablename__ = "auto_scheduled_tasks"

    created_by_user_id = Column(String(64), nullable=False, default="user-system")
    conversation_id = Column(String(64), nullable=True, index=True)
    task_name = Column(String(255), nullable=False)
    target_service = Column(String(64), nullable=False)  # e.g., 'finance-service', 'crm-service'
    action_type = Column(String(64), nullable=False)     # e.g., 'SEND_PAYMENT_REMINDER', 'DRAFT_PO'
    payload = Column(Text, nullable=False, default="{}") # JSON string
    scheduled_for = Column(String(64), nullable=False, index=True) # ISO-8601 string
    precondition_check = Column(Text, nullable=True)     # JSON condition dict e.g. {"field": "status", "expected": "OVERDUE"}
    status = Column(String(32), nullable=False, default="PENDING", index=True) # PENDING, DUE, WAITING_APPROVAL, EXECUTED, CANCELLED, FAILED
    requires_hitl = Column(Boolean, default=False)
    hitl_approval_id = Column(String(36), nullable=True)
    executed_at = Column(String(64), nullable=True)
    execution_result = Column(Text, nullable=True)

    hitl_requests = relationship("HITLApprovalRequest", back_populates="task", cascade="all, delete-orphan")


class HITLApprovalRequest(TenantModel):
    __tablename__ = "auto_hitl_approvals"

    task_id = Column(String(36), ForeignKey("auto_scheduled_tasks.id"), nullable=True, index=True)
    requested_by = Column(String(64), nullable=False, default="AI_AGENT_COPILOT")
    assigned_approver_role = Column(String(64), nullable=False, default="FINANCE_MANAGER") # e.g., FINANCE_MANAGER, SUPER_ADMIN
    risk_level = Column(String(16), nullable=False, default="HIGH") # LOW, MEDIUM, HIGH, CRITICAL
    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    action_diff = Column(Text, nullable=False, default="{}") # JSON string of proposed change
    status = Column(String(32), nullable=False, default="PENDING", index=True) # PENDING, APPROVED, REJECTED, EXPIRED
    decision_by_user_id = Column(String(64), nullable=True)
    decision_notes = Column(Text, nullable=True)
    decided_at = Column(String(64), nullable=True)
    expires_at = Column(String(64), nullable=True)

    task = relationship("ScheduledTask", back_populates="hitl_requests")


# =========================================================================
# Phase 5: Visual Workflows, Unified Approvals & Zoho Migration Models
# =========================================================================
class WorkflowDefinition(TenantModel):
    __tablename__ = "auto_workflows"

    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    trigger_event = Column(String(100), nullable=False, index=True)
    nodes = Column(Text, nullable=False, default="[]")  # JSON serialized DAG nodes
    is_active = Column(Boolean, default=True, index=True)
    execution_count = Column(Integer, default=0)

    executions = relationship("WorkflowExecution", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowExecution(TenantModel):
    __tablename__ = "auto_workflow_executions"

    workflow_id = Column(String(36), ForeignKey("auto_workflows.id"), nullable=False, index=True)
    status = Column(String(32), default="COMPLETED", index=True)  # RUNNING, COMPLETED, FAILED, PAUSED
    trigger_payload = Column(Text, nullable=True)  # JSON string
    current_node_id = Column(String(64), nullable=True)
    step_history = Column(Text, nullable=False, default="[]")  # JSON string of steps
    error_message = Column(Text, nullable=True)

    workflow = relationship("WorkflowDefinition", back_populates="executions")


class ApprovalRequest(TenantModel):
    __tablename__ = "auto_unified_approvals"

    module = Column(String(64), nullable=False, index=True)  # PROCUREMENT, FINANCE, CRM, HR
    record_type = Column(String(64), nullable=False, index=True)  # PURCHASE_REQUISITION, QUOTE_DISCOUNT, LEAVE_REQUEST, EXPENSE, INVOICE
    record_id = Column(String(64), nullable=False, index=True)
    requester_id = Column(String(64), nullable=False)
    requester_name = Column(String(255), nullable=True)
    approver_role = Column(String(64), nullable=False, default="MANAGER", index=True)
    approver_id = Column(String(64), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(Float, default=0.0)
    status = Column(String(32), default="PENDING", index=True)  # PENDING, APPROVED, REJECTED, DELEGATED
    decision_by_id = Column(String(64), nullable=True)
    decision_notes = Column(Text, nullable=True)
    delegated_to_id = Column(String(64), nullable=True)
    decided_at = Column(String(64), nullable=True)


class ZohoMigrationJob(TenantModel):
    __tablename__ = "auto_zoho_migrations"

    status = Column(String(32), default="SUCCESS", index=True)
    records_migrated = Column(Text, default="{}")  # JSON summary
    canonical_mappings = Column(Text, default="[]")  # JSON mappings
    validation_errors = Column(Text, default="[]")  # JSON errors
    elapsed_ms = Column(Float, default=0.0)
