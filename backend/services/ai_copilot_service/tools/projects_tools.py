import uuid
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from common.config import get_service_config
from common.database import create_db_manager
from services.projects_service.models import Task, Project, Sprint
from services.ai_copilot_service.tools.base import (
    ToolDefinition, DataTier, SideEffect, ApprovalRequirement
)


# --- Schemas ---

class ListIssuesArgs(BaseModel):
    status: Optional[str] = Field(default=None, description="Task status filter: Blocked, In progress, Ready for review, Done")
    is_blocked: Optional[bool] = Field(default=None, description="Set True to query only blocked items")
    priority: Optional[str] = Field(default=None, description="Priority filter: High, Critical, Medium")
    limit: int = Field(default=15, description="Max tasks to return")


class CreateIssueArgs(BaseModel):
    title: str = Field(description="Descriptive issue title")
    issue_type: Optional[str] = Field(default="Task", description="Type: Story, Bug, Task")
    priority: Optional[str] = Field(default="High", description="Priority: Low, Medium, High, Critical")
    points: Optional[int] = Field(default=5, description="Story point estimate (1-13)")
    assignee: Optional[str] = Field(default="Marcus Chen", description="Assignee engineer name")
    description: Optional[str] = Field(default=None, description="Detailed technical acceptance criteria")


class UpdateIssueStatusArgs(BaseModel):
    issue_id: str = Field(description="Task key (e.g. 'FIN-50', 'FIN-51') or internal ID")
    new_status: str = Field(description="Target status: 'In progress', 'Ready for review', 'Done', 'Blocked'")


# --- Executors ---

def _get_projects_session():
    cfg = get_service_config("projects-service", 8004, "projects.db")
    mgr = create_db_manager(cfg.database_url)
    return next(mgr.get_session())


def execute_list_issues(args: ListIssuesArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_projects_session()
    try:
        q = session.query(Task).filter_by(org_id=user_ctx.org_id)
        if args.is_blocked:
            q = q.filter(Task.status.ilike("%block%"))
        elif args.status:
            q = q.filter(Task.status.ilike(f"%{args.status}%"))
        if args.priority:
            q = q.filter(Task.priority.ilike(f"%{args.priority}%"))

        tasks = q.limit(args.limit).all()
        blocked_count = sum(1 for t in tasks if "block" in t.status.lower())

        return {
            "total_count": len(tasks),
            "blocked_count": blocked_count,
            "tasks": [
                {
                    "id": t.id,
                    "key": t.task_key,
                    "title": t.title,
                    "status": t.status,
                    "priority": t.priority,
                    "type": t.issue_type,
                    "assignee": t.assignee,
                    "estimate_hours": t.estimate_hours
                }
                for t in tasks
            ]
        }
    finally:
        session.close()


def execute_create_issue(args: CreateIssueArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_projects_session()
    try:
        project = session.query(Project).filter_by(org_id=user_ctx.org_id).first()
        proj_id = project.id if project else str(uuid.uuid4())
        sprint = session.query(Sprint).filter_by(org_id=user_ctx.org_id, status="Active").first()
        sprint_id = sprint.id if sprint else None

        existing_count = session.query(Task).filter_by(org_id=user_ctx.org_id).count()
        task_key = f"FIN-{existing_count + 52}"

        task_id = str(uuid.uuid4())
        new_task = Task(
            id=task_id,
            org_id=user_ctx.org_id,
            project_id=proj_id,
            sprint_id=sprint_id,
            task_key=task_key,
            title=args.title,
            description=args.description or "Created via STAT6 Omni-Copilot",
            status="In progress",
            priority=args.priority or "High",
            issue_type=args.issue_type or "Task",
            estimate_hours=float(args.points or 5) * 2.0,
            assignee=args.assignee or "Marcus Chen"
        )
        session.add(new_task)
        session.commit()
        return {
            "id": task_id,
            "key": task_key,
            "title": args.title,
            "status": "In progress",
            "priority": new_task.priority,
            "assignee": new_task.assignee,
            "message": f"Sprint 44 task '{task_key}: {args.title}' successfully created on board."
        }
    finally:
        session.close()


def execute_update_issue_status(args: UpdateIssueStatusArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_projects_session()
    try:
        task = session.query(Task).filter_by(org_id=user_ctx.org_id, task_key=args.issue_id).first()
        if not task:
            task = session.query(Task).filter_by(org_id=user_ctx.org_id, id=args.issue_id).first()
        if not task:
            task = session.query(Task).filter(Task.title.ilike(f"%{args.issue_id}%"), Task.org_id == user_ctx.org_id).first()
        if not task:
            return {"error": "TASK_NOT_FOUND", "message": f"Task '{args.issue_id}' not found on project board."}

        old_status = task.status
        task.status = args.new_status
        session.commit()
        return {
            "id": task.id,
            "key": task.task_key,
            "title": task.title,
            "previous_status": old_status,
            "new_status": task.status,
            "message": f"Issue {task.task_key} transitioned from '{old_status}' to '{task.status}'."
        }
    finally:
        session.close()


# --- Tool Registry Definitions ---

PROJECTS_TOOLS = [
    ToolDefinition(
        name="list_issues",
        description="Inspect active Sprint 44 Kanban board tasks, blockers, priorities, and assigned engineers.",
        category="projects",
        args_schema=ListIssuesArgs,
        side_effect=SideEffect.READ,
        required_permission="projects.tasks.view",
        output_tier=DataTier.TIER_1_INTERNAL,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_list_issues
    ),
    ToolDefinition(
        name="create_issue",
        description="Create a new engineering issue, bug ticket, or user story on the active Sprint Kanban board.",
        category="projects",
        args_schema=CreateIssueArgs,
        side_effect=SideEffect.WRITE,
        required_permission="projects.tasks.create",
        output_tier=DataTier.TIER_1_INTERNAL,
        approval_requirement=ApprovalRequirement.USER_CONFIRM,
        executor=execute_create_issue
    ),
    ToolDefinition(
        name="update_issue_status",
        description="Transition a Sprint issue's status across the board (e.g. from 'In progress' to 'Ready for review' or 'Done').",
        category="projects",
        args_schema=UpdateIssueStatusArgs,
        side_effect=SideEffect.WRITE,
        required_permission="projects.tasks.update",
        output_tier=DataTier.TIER_1_INTERNAL,
        approval_requirement=ApprovalRequirement.USER_CONFIRM,
        executor=execute_update_issue_status
    ),
]
