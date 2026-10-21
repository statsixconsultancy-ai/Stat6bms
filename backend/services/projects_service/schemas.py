from typing import Optional, List
from pydantic import BaseModel

# --- Project Schemas ---
class ProjectCreate(BaseModel):
    name: str
    code: str
    client_name: Optional[str] = "Enterprise Client"
    description: Optional[str] = None
    budget: float = 0.0
    start_date: Optional[str] = None
    target_end_date: Optional[str] = None
    manager: Optional[str] = "Project Lead"

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    budget: Optional[float] = None
    spent_amount: Optional[float] = None
    manager: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    org_id: str
    name: str
    code: str
    client_name: str
    description: Optional[str] = None
    status: str
    budget: float
    spent_amount: float
    start_date: Optional[str] = None
    target_end_date: Optional[str] = None
    manager: str

# --- Sprint Schemas ---
class SprintCreate(BaseModel):
    project_id: str
    name: str
    goal: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class SprintResponse(BaseModel):
    id: str
    org_id: str
    project_id: str
    name: str
    goal: Optional[str] = None
    status: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None

# --- Task / Issue Schemas ---
class TaskCreate(BaseModel):
    project_id: str
    sprint_id: Optional[str] = None
    task_key: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: Optional[str] = "In progress"  # Blocked, In progress, Ready for review, Done
    priority: Optional[str] = "Medium"
    issue_type: Optional[str] = "Task"
    estimate_hours: Optional[float] = 8.0
    assignee: Optional[str] = "Marcus Chen"

class TaskMoveRequest(BaseModel):
    status: str  # Blocked, In progress, Ready for review, Done

class TaskResponse(BaseModel):
    id: str
    org_id: str
    project_id: str
    sprint_id: Optional[str] = None
    task_key: str
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    issue_type: str
    estimate_hours: float
    logged_hours: float
    assignee: str
    dependencies: Optional[str] = "[]"
    is_critical_path: Optional[bool] = False
    story_points: Optional[int] = 3

# --- Worklog / TimeEntry Schemas ---
class WorklogRequest(BaseModel):
    hours: float
    date: Optional[str] = None
    notes: Optional[str] = None
    is_billable: Optional[bool] = True

class TimeEntryResponse(BaseModel):
    id: str
    org_id: str
    task_id: str
    user_id: str
    user_name: str
    hours: float
    date: Optional[str] = None
    notes: Optional[str] = None
    is_billable: bool

# --- Burndown & Project Detail ---
class BurndownResponse(BaseModel):
    project_id: str
    total_tasks: int
    done_tasks: int
    in_progress_tasks: int
    blocked_tasks: int
    review_tasks: int
    completion_rate_percent: float
    total_estimate_hours: float
    total_logged_hours: float
    total_story_points: int = 0
    remaining_story_points: int = 0

# --- Gantt & Critical Path Method (CPM) ---
class CriticalPathNode(BaseModel):
    task_key: str
    title: str
    duration_days: int
    early_start: int
    early_finish: int
    late_start: int
    late_finish: int
    total_float: int
    is_critical: bool

class CriticalPathResponse(BaseModel):
    project_id: str
    project_name: str
    project_duration_days: int
    critical_path_tasks: List[str]
    nodes: List[CriticalPathNode]

# --- Milestone Schemas ---
class MilestoneCreate(BaseModel):
    name: str
    due_date: str
    amount: Optional[float] = 0.0

class MilestoneResponse(BaseModel):
    id: str
    org_id: str
    project_id: str
    name: str
    due_date: str
    amount: float
    status: str

# --- Project Financials (PSA Real-Time Costing) ---
class ProjectFinancialsResponse(BaseModel):
    project_id: str
    project_name: str
    contract_budget: float
    total_billable_revenue: float
    total_labor_cost: float
    total_expenses: float
    net_profit: float
    profit_margin_percent: float

