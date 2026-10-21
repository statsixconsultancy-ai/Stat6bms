import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class Project(TenantModel):
    __tablename__ = "prj_projects"

    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)  # e.g., PRJ-APEX
    client_name = Column(String(255), default="Enterprise Client")
    description = Column(Text, nullable=True)
    status = Column(String(50), default="Active", index=True)  # Active, Completed, On Hold, Planning
    budget = Column(Float, default=0.0)
    spent_amount = Column(Float, default=0.0)
    start_date = Column(String(50), nullable=True)
    target_end_date = Column(String(50), nullable=True)
    manager = Column(String(255), default="Project Lead")

    sprints = relationship("Sprint", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")

class Sprint(TenantModel):
    __tablename__ = "prj_sprints"

    project_id = Column(String(36), ForeignKey("prj_projects.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    goal = Column(Text, nullable=True)
    status = Column(String(50), default="Active", index=True)  # Active, Planned, Completed
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)

    project = relationship("Project", back_populates="sprints")
    tasks = relationship("Task", back_populates="sprint")

class Task(TenantModel):
    __tablename__ = "prj_tasks"

    project_id = Column(String(36), ForeignKey("prj_projects.id"), nullable=False, index=True)
    sprint_id = Column(String(36), ForeignKey("prj_sprints.id"), nullable=True, index=True)
    task_key = Column(String(50), nullable=False, unique=True, index=True)  # e.g., PRJ-101
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="In progress", index=True)  # Blocked, In progress, Ready for review, Done
    priority = Column(String(50), default="Medium")  # Low, Medium, High, Critical
    issue_type = Column(String(50), default="Task")  # Story, Bug, Task, Epic
    estimate_hours = Column(Float, default=8.0)
    logged_hours = Column(Float, default=0.0)
    assignee = Column(String(255), default="Engineer")
    dependencies = Column(Text, default="[]")  # List of prerequisite task keys
    dependency_type = Column(String(10), default="FS")  # FS, SS, FF, SF
    is_critical_path = Column(Boolean, default=False)
    early_start_day = Column(Integer, default=0)
    early_finish_day = Column(Integer, default=0)
    late_start_day = Column(Integer, default=0)
    late_finish_day = Column(Integer, default=0)
    total_float = Column(Integer, default=0)
    story_points = Column(Integer, default=3)

    project = relationship("Project", back_populates="tasks")
    sprint = relationship("Sprint", back_populates="tasks")
    time_entries = relationship("TimeEntry", back_populates="task", cascade="all, delete-orphan")

class TimeEntry(TenantModel):
    __tablename__ = "prj_time_entries"

    task_id = Column(String(36), ForeignKey("prj_tasks.id"), nullable=False, index=True)
    user_id = Column(String(255), default="usr-dev-001")
    user_name = Column(String(255), default="Engineer")
    hours = Column(Float, nullable=False)
    date = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    is_billable = Column(Boolean, default=True)

    task = relationship("Task", back_populates="time_entries")

class Milestone(TenantModel):
    __tablename__ = "prj_milestones"

    project_id = Column(String(36), ForeignKey("prj_projects.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    due_date = Column(String(50), nullable=False)
    amount = Column(Float, default=0.0)
    status = Column(String(50), default="Pending", index=True)  # Pending, Completed, Billed

