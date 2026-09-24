import os
import sys
import uuid
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.config import get_service_config
from common.database import create_db_manager
from common.models import Base
from common.security import get_user_context, UserContext
from common.middleware import setup_microservice_middleware
from common.event_bus import event_bus

from services.projects_service.models import Project, Sprint, Task, TimeEntry
from services.projects_service.schemas import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    SprintCreate, SprintResponse,
    TaskCreate, TaskMoveRequest, TaskResponse,
    WorklogRequest, TimeEntryResponse,
    BurndownResponse
)
from services.projects_service.seed import seed_projects_data

config = get_service_config("projects-service", default_port=8004, db_filename="projects.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="BMS Project Operations & Jira Agile Microservice",
    description="Sprint Backlogs, Jira-Style Agile Board Kanban, Worklogs & Velocity Tracking",
    version="2.0.0"
)

setup_microservice_middleware(app, "projects-service", config.cors_origins)

@app.on_event("startup")
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_projects_data(session)
    finally:
        session.close()

def get_db():
    yield from db_mgr.get_session()

# ----------------------------------------------------
# 1. Health & Event Broker Webhooks
# ----------------------------------------------------
@app.get("/health")
def health():
    return {"service": "projects-service", "status": "UP", "port": config.service_port}

@app.post("/webhooks/events")
async def handle_events(event: dict, db: Session = Depends(get_db)):
    """
    Subscribes to 'deal.won' events from CRM.
    Automatically provisions a new client delivery project and initial sprint.
    """
    event_name = event.get("event_name")
    payload = event.get("payload", {})
    org_id = event.get("org_id", "org-acroflow-main")

    if event_name == "deal.won":
        p_code = f"PRJ-{uuid.uuid4().hex[:4].upper()}"
        deal_title = payload.get("title", "Commercial Engagement")
        deal_amount = payload.get("amount", 100000.0)
        client_name = payload.get("company_name", "Enterprise Client")

        project = Project(
            id=str(uuid.uuid4()),
            org_id=org_id,
            name=f"Delivery: {deal_title}",
            code=p_code,
            client_name=client_name,
            description=f"Auto-provisioned client delivery workspace for Deal {payload.get('deal_id')}.",
            status="Active",
            budget=deal_amount,
            spent_amount=0.0,
            start_date="2026-10-01",
            target_end_date="2027-03-31",
            manager="Marcus Chen"
        )
        db.add(project)
        db.flush()

        sprint = Sprint(
            id=str(uuid.uuid4()),
            org_id=org_id,
            project_id=project.id,
            name="Sprint 1 — Kickoff & Architecture Discovery",
            goal="Establish client SLA, repositories, and architecture blueprint.",
            status="Active",
            start_date="2026-10-01",
            end_date="2026-10-15"
        )
        db.add(sprint)
        db.commit()

        return {"status": "project_provisioned", "project_id": project.id, "project_code": p_code}

    return {"status": "ignored", "event_name": event_name}

# ----------------------------------------------------
# 2. Projects Endpoints
# ----------------------------------------------------
@app.get("/projects", response_model=List[ProjectResponse])
def list_projects(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    projects = db.query(Project).filter_by(org_id=user_ctx.org_id).order_by(Project.created_at.desc()).all()
    return [ProjectResponse(**p.to_dict()) for p in projects]

@app.post("/projects", response_model=ProjectResponse)
def create_project(req: ProjectCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    existing = db.query(Project).filter_by(code=req.code, org_id=user_ctx.org_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Project code '{req.code}' already exists")

    project = Project(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        name=req.name,
        code=req.code,
        client_name=req.client_name or "Enterprise Client",
        description=req.description,
        status="Active",
        budget=req.budget,
        spent_amount=0.0,
        start_date=req.start_date,
        target_end_date=req.target_end_date,
        manager=req.manager or "Project Lead"
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return ProjectResponse(**project.to_dict())

# ----------------------------------------------------
# 2. Jira Agile Board Tasks & Kanban Moves (Defined before /projects/{id})
# ----------------------------------------------------
@app.get("/projects/tasks", response_model=List[TaskResponse])
def list_tasks(
    project_id: Optional[str] = None,
    sprint_id: Optional[str] = None,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter_by(org_id=user_ctx.org_id)
    if project_id:
        query = query.filter_by(project_id=project_id)
    if sprint_id:
        query = query.filter_by(sprint_id=sprint_id)
    tasks = query.all()
    return [TaskResponse(**t.to_dict()) for t in tasks]

@app.post("/projects/tasks", response_model=TaskResponse)
def create_task(req: TaskCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    seq = db.query(Task).filter_by(project_id=req.project_id).count() + 1
    task_key = req.task_key or f"TSK-{seq:03d}"

    task = Task(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        project_id=req.project_id,
        sprint_id=req.sprint_id,
        task_key=task_key,
        title=req.title,
        description=req.description,
        status=req.status or "In progress",
        priority=req.priority or "Medium",
        issue_type=req.issue_type or "Task",
        estimate_hours=req.estimate_hours or 8.0,
        logged_hours=0.0,
        assignee=req.assignee or "Engineer"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return TaskResponse(**task.to_dict())

@app.patch("/projects/tasks/{id}/move", response_model=TaskResponse)
def move_task_status(
    id: str,
    req: TaskMoveRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Transitions task across Jira Agile board lanes:
    'Blocked' | 'In progress' | 'Ready for review' | 'Done'
    """
    valid_statuses = ["Blocked", "In progress", "Ready for review", "Done"]
    if req.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    task = db.query(Task).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = req.status
    db.commit()
    db.refresh(task)
    return TaskResponse(**task.to_dict())

@app.post("/projects/tasks/{id}/worklog", response_model=TimeEntryResponse)
def log_work_hours(
    id: str,
    req: WorklogRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Logs billable/non-billable hours, increments task progress and project spend."""
    task = db.query(Task).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    entry = TimeEntry(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        task_id=task.id,
        user_id=user_ctx.user_id,
        user_name=user_ctx.email or "Team Member",
        hours=req.hours,
        date=req.date or "2026-09-24",
        notes=req.notes,
        is_billable=req.is_billable if req.is_billable is not None else True
    )
    db.add(entry)

    # Increment task logged hours
    task.logged_hours += req.hours

    # Increment project spent amount (at $150/hr blended billable rate)
    if entry.is_billable and task.project:
        task.project.spent_amount += (req.hours * 150.0)

    db.commit()
    db.refresh(entry)
    return TimeEntryResponse(**entry.to_dict())

# ----------------------------------------------------
# 3. Projects Endpoints
# ----------------------------------------------------
@app.get("/projects/{id}", response_model=ProjectResponse)
def get_project(id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    p = db.query(Project).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse(**p.to_dict())

# ----------------------------------------------------
# 4. Sprints Endpoints
# ----------------------------------------------------
@app.get("/projects/{project_id}/sprints", response_model=List[SprintResponse])
def list_sprints(project_id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    sprints = db.query(Sprint).filter_by(project_id=project_id, org_id=user_ctx.org_id).all()
    return [SprintResponse(**s.to_dict()) for s in sprints]

@app.post("/projects/{project_id}/sprints", response_model=SprintResponse)
def create_sprint(project_id: str, req: SprintCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    sprint = Sprint(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        project_id=project_id,
        name=req.name,
        goal=req.goal,
        status="Active",
        start_date=req.start_date,
        end_date=req.end_date
    )
    db.add(sprint)
    db.commit()
    db.refresh(sprint)
    return SprintResponse(**sprint.to_dict())

# ----------------------------------------------------
# 5. Burndown & Agile Board Analytics
# ----------------------------------------------------
@app.get("/projects/{project_id}/burndown", response_model=BurndownResponse)
def get_project_burndown(project_id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    tasks = db.query(Task).filter_by(project_id=project_id, org_id=user_ctx.org_id).all()
    total_tasks = len(tasks)
    done_count = sum(1 for t in tasks if t.status == "Done")
    in_progress_count = sum(1 for t in tasks if t.status == "In progress")
    blocked_count = sum(1 for t in tasks if t.status == "Blocked")
    review_count = sum(1 for t in tasks if t.status == "Ready for review")

    completion_rate = (done_count / total_tasks * 100.0) if total_tasks > 0 else 0.0
    tot_est = sum(t.estimate_hours for t in tasks)
    tot_log = sum(t.logged_hours for t in tasks)

    return BurndownResponse(
        project_id=project_id,
        total_tasks=total_tasks,
        done_tasks=done_count,
        in_progress_tasks=in_progress_count,
        blocked_tasks=blocked_count,
        review_tasks=review_count,
        completion_rate_percent=round(completion_rate, 1),
        total_estimate_hours=tot_est,
        total_logged_hours=tot_log
    )
