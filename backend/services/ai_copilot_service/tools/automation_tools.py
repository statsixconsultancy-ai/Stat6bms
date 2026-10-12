import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from common.config import get_service_config
from common.database import create_db_manager
from services.automation_service.models import ScheduledTask, HITLApprovalRequest
from services.ai_copilot_service.tools.base import (
    ToolDefinition, DataTier, SideEffect, ApprovalRequirement
)


# --- Schemas ---

class ScheduleTaskArgs(BaseModel):
    task_name: str = Field(description="Descriptive name of the automated background task")
    target_service: str = Field(description="Target microservice e.g. 'finance-service', 'inventory-service'")
    action_type: str = Field(description="Normalized action identifier e.g. 'SEND_PAYMENT_REMINDER', 'SYNC_STOCK'")
    payload: Dict[str, Any] = Field(description="Key-value payload dictionary for the action")
    scheduled_for: str = Field(description="ISO-8601 target execution timestamp e.g. '2026-10-11T10:00:00'")
    precondition_check: Optional[Dict[str, Any]] = Field(default=None, description="Precondition criteria e.g. {'field': 'status', 'expected': 'OVERDUE'}")
    requires_hitl: bool = Field(default=False, description="Whether to require human approval before execution")


class ListScheduledTasksArgs(BaseModel):
    status: Optional[str] = Field(default=None, description="Filter: PENDING, WAITING_APPROVAL, EXECUTED, CANCELLED")
    limit: int = Field(default=10, description="Max tasks to return")


class CancelScheduledTaskArgs(BaseModel):
    task_id: str = Field(description="Unique ID of the scheduled task to cancel")
    reason: Optional[str] = Field(default="Cancelled by user request", description="Reason for cancellation")


# --- Executors ---

def _get_automation_session():
    cfg = get_service_config("automation-service", 8012, "automation.db")
    mgr = create_db_manager(cfg.database_url)
    return next(mgr.get_session())


def execute_schedule_task(args: ScheduleTaskArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_automation_session()
    try:
        task_id = str(uuid.uuid4())
        hitl_id = str(uuid.uuid4()) if args.requires_hitl else None

        task = ScheduledTask(
            id=task_id,
            org_id=user_ctx.org_id,
            task_name=args.task_name,
            target_service=args.target_service,
            action_type=args.action_type,
            payload=json.dumps(args.payload),
            scheduled_for=args.scheduled_for,
            precondition_check=json.dumps(args.precondition_check) if args.precondition_check else None,
            status="PENDING",
            requires_hitl=args.requires_hitl,
            hitl_approval_id=hitl_id
        )
        session.add(task)

        if args.requires_hitl:
            hitl = HITLApprovalRequest(
                id=hitl_id,
                org_id=user_ctx.org_id,
                task_id=task_id,
                requested_by="AI_AGENT_COPILOT",
                assigned_approver_role="FINANCE_MANAGER" if "finance" in args.target_service else "SUPER_ADMIN",
                risk_level="HIGH" if ("finance" in args.target_service or "payroll" in args.task_name.lower()) else "MEDIUM",
                title=f"Approval Required: {args.task_name}",
                summary=f"Automated action '{args.action_type}' for {args.target_service} scheduled for {args.scheduled_for}.",
                action_diff=json.dumps(args.payload),
                status="PENDING"
            )
            session.add(hitl)

        session.commit()
        return {
            "task_id": task_id,
            "task_name": args.task_name,
            "target_service": args.target_service,
            "scheduled_for": args.scheduled_for,
            "status": "PENDING",
            "requires_hitl": args.requires_hitl,
            "hitl_approval_id": hitl_id,
            "message": f"Task '{args.task_name}' successfully scheduled for {args.scheduled_for}."
        }
    finally:
        session.close()


def execute_list_scheduled_tasks(args: ListScheduledTasksArgs, user_ctx: Any) -> List[Dict[str, Any]]:
    session = _get_automation_session()
    try:
        q = session.query(ScheduledTask).filter_by(org_id=user_ctx.org_id)
        if args.status:
            q = q.filter_by(status=args.status)
        tasks = q.order_by(ScheduledTask.created_at.desc()).limit(args.limit).all()
        return [
            {
                "id": t.id,
                "task_name": t.task_name,
                "target_service": t.target_service,
                "action_type": t.action_type,
                "scheduled_for": t.scheduled_for,
                "status": t.status,
                "requires_hitl": t.requires_hitl,
                "executed_at": t.executed_at
            }
            for t in tasks
        ]
    finally:
        session.close()


def execute_cancel_scheduled_task(args: CancelScheduledTaskArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_automation_session()
    try:
        task = session.query(ScheduledTask).filter_by(id=args.task_id, org_id=user_ctx.org_id).first()
        if not task:
            # Try matching by name
            task = session.query(ScheduledTask).filter(
                ScheduledTask.task_name.ilike(f"%{args.task_id}%"),
                ScheduledTask.org_id == user_ctx.org_id
            ).first()
        if not task:
            return {"error": "TASK_NOT_FOUND", "message": f"Scheduled task '{args.task_id}' not found."}

        task.status = "CANCELLED"
        task.execution_result = json.dumps({"reason": args.reason, "cancelled_at": datetime.utcnow().isoformat()})
        session.commit()
        return {
            "id": task.id,
            "task_name": task.task_name,
            "status": "CANCELLED",
            "message": f"Task '{task.task_name}' successfully cancelled."
        }
    finally:
        session.close()


# --- Tool Registry Definitions ---

AUTOMATION_TOOLS = [
    ToolDefinition(
        name="schedule_task",
        description="Register an operational background task to execute at a designated future time, governed by state preconditions and HITL safety approval.",
        category="automation",
        args_schema=ScheduleTaskArgs,
        side_effect=SideEffect.SCHEDULE,
        required_permission="automation.schedule",
        output_tier=DataTier.TIER_1_INTERNAL,
        approval_requirement=ApprovalRequirement.USER_CONFIRM,
        executor=execute_schedule_task
    ),
    ToolDefinition(
        name="list_scheduled_tasks",
        description="List active background tasks, execution countdowns, and pending human-in-the-loop approvals.",
        category="automation",
        args_schema=ListScheduledTasksArgs,
        side_effect=SideEffect.READ,
        required_permission="automation.view",
        output_tier=DataTier.TIER_1_INTERNAL,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_list_scheduled_tasks
    ),
    ToolDefinition(
        name="cancel_scheduled_task",
        description="Cancel a scheduled background task before its execution window arrives.",
        category="automation",
        args_schema=CancelScheduledTaskArgs,
        side_effect=SideEffect.WRITE,
        required_permission="automation.manage",
        output_tier=DataTier.TIER_1_INTERNAL,
        approval_requirement=ApprovalRequirement.USER_CONFIRM,
        executor=execute_cancel_scheduled_task
    ),
]
