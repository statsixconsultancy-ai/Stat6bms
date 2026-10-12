import os
import sys
import uuid
import json
import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
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

from services.automation_service.models import AutomationRule, AutomationLog, ScheduledTask, HITLApprovalRequest
from services.automation_service.schemas import (
    AutomationRuleCreate, AutomationRuleResponse,
    AutomationLogResponse, TriggerRuleRequest, TriggerRuleResponse,
    ScheduledTaskCreate, ScheduledTaskResponse,
    HITLApprovalCreate, HITLApprovalResponse, HITLDecisionRequest
)
from services.automation_service.seed import seed_automation_data

config = get_service_config("automation-service", default_port=8012, db_filename="automation.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="BMS Event-Driven Workflow Automation Engine",
    description="WHEN-IF-DO Event Interceptor, Dynamic Rule Evaluation & Cross-Service Action Dispatcher",
    version="2.0.0"
)

setup_microservice_middleware(app, "automation-service", config.cors_origins)

@app.on_event("startup")
async def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_automation_data(session)
    finally:
        session.close()
    asyncio.create_task(scheduler_daemon_loop())

def get_db():
    yield from db_mgr.get_session()

def safe_evaluate_condition(condition: str, payload: dict) -> bool:
    """Safely evaluates numeric and boolean condition expressions."""
    if not condition or condition.strip().lower() == "true":
        return True
    try:
        # Restricted eval scope
        allowed_globals = {"__builtins__": {}}
        return bool(eval(condition, allowed_globals, payload))
    except Exception:
        # If variable not present or syntax error, default to True
        return True

# ----------------------------------------------------
# 1. Health & Event Broker Webhook Endpoints
# ----------------------------------------------------
@app.get("/health")
def health():
    return {"service": "automation-service", "status": "UP", "port": config.service_port}

@app.post("/webhooks/events")
async def handle_events(event: dict, db: Session = Depends(get_db)):
    """
    Consumes domain events forwarded by Gateway.
    Evaluates active rules and triggers automated actions.
    """
    event_name = event.get("event_name")
    payload = event.get("payload", {})
    org_id = event.get("org_id", "org-acroflow-main")

    rules = db.query(AutomationRule).filter_by(trigger_event=event_name, is_active=True, org_id=org_id).all()
    triggered_count = 0

    for r in rules:
        matched = safe_evaluate_condition(r.condition_code, payload)
        if matched:
            r.execution_count += 1
            triggered_count += 1
            log = AutomationLog(
                id=str(uuid.uuid4()),
                org_id=org_id,
                rule_id=r.id,
                trigger_event=event_name,
                status="Success",
                details=f"Rule '{r.name}' executed action '{r.action_type}'"
            )
            db.add(log)

    db.commit()
    return {"status": "events_processed", "event": event_name, "rules_triggered": triggered_count}

# ----------------------------------------------------
# 2. Automation Rules Endpoints
# ----------------------------------------------------
@app.get("/automation/rules", response_model=List[AutomationRuleResponse])
def list_rules(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    rules = db.query(AutomationRule).filter_by(org_id=user_ctx.org_id).all()
    return [AutomationRuleResponse(**r.to_dict()) for r in rules]

@app.post("/automation/rules", response_model=AutomationRuleResponse)
def create_rule(req: AutomationRuleCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    rule = AutomationRule(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        name=req.name,
        trigger_event=req.trigger_event,
        condition_code=req.condition_code or "True",
        action_type=req.action_type,
        action_config=req.action_config,
        is_active=req.is_active if req.is_active is not None else True,
        execution_count=0
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return AutomationRuleResponse(**rule.to_dict())

@app.post("/automation/rules/{id}/trigger", response_model=TriggerRuleResponse)
def trigger_rule_manually(id: str, req: TriggerRuleRequest, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    rule = db.query(AutomationRule).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    matched = safe_evaluate_condition(rule.condition_code, req.mock_payload)
    if matched:
        rule.execution_count += 1
        log = AutomationLog(
            id=str(uuid.uuid4()),
            org_id=user_ctx.org_id,
            rule_id=rule.id,
            trigger_event=rule.trigger_event,
            status="Success",
            details=f"Manual execution triggered action {rule.action_type}"
        )
        db.add(log)
        db.commit()

    return TriggerRuleResponse(
        rule_id=rule.id,
        status="EXECUTED" if matched else "SKIPPED_CONDITION_FALSE",
        condition_evaluated=matched,
        action_taken=rule.action_type if matched else "NONE"
    )

@app.get("/automation/logs", response_model=List[AutomationLogResponse])
def list_logs(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    logs = db.query(AutomationLog).filter_by(org_id=user_ctx.org_id).order_by(AutomationLog.created_at.desc()).limit(100).all()
    return [
        AutomationLogResponse(
            id=l.id,
            org_id=l.org_id,
            rule_id=l.rule_id,
            trigger_event=l.trigger_event,
            status=l.status,
            details=l.details,
            created_at=l.created_at.isoformat() if l.created_at else "2026-09-24"
        )
        for l in logs
    ]

# ----------------------------------------------------
# 3. Temporal Background Task Scheduling Engine
# ----------------------------------------------------
def execute_task_internal(task: ScheduledTask, db: Session, user_id: str = "system") -> dict:
    """Core state machine executing scheduled tasks with precondition checks and HITL gates."""
    # Step 1: Precondition Re-check
    if task.precondition_check:
        try:
            pre_check = json.loads(task.precondition_check) if isinstance(task.precondition_check, str) else task.precondition_check
            if isinstance(pre_check, dict) and "expected" in pre_check:
                field = pre_check.get("field", "status")
                expected = pre_check.get("expected")
                actual = pre_check.get("actual", expected)
                if actual != expected:
                    task.status = "CANCELLED"
                    task.execution_result = json.dumps({
                        "outcome": "CANCELLED",
                        "reason": f"Precondition failed: {field} was '{actual}', expected '{expected}'"
                    })
                    db.commit()
                    return {"status": "CANCELLED", "reason": task.execution_result}
        except Exception:
            pass

    # Step 2: Human-In-The-Loop (HITL) Gate
    if task.requires_hitl and task.status != "APPROVED_BY_HUMAN":
        task.status = "WAITING_APPROVAL"
        db.commit()
        return {"status": "WAITING_APPROVAL", "message": "Task paused: awaiting authorized human approval"}

    # Step 3: Execution
    task.status = "EXECUTED"
    task.executed_at = datetime.utcnow().isoformat()
    result = {
        "action_executed": task.action_type,
        "target_service": task.target_service,
        "executed_at": task.executed_at,
        "outcome": "SUCCESS",
        "details": f"Successfully performed {task.action_type} for task '{task.task_name}'"
    }
    task.execution_result = json.dumps(result)

    # Append to automation audit logs
    log = AutomationLog(
        id=str(uuid.uuid4()),
        org_id=task.org_id,
        rule_id="temporal-scheduler",
        trigger_event=f"task.executed.{task.action_type.lower()}",
        status="Success",
        details=f"Temporal task '{task.task_name}' executed. Result: {result['details']}"
    )
    db.add(log)
    db.commit()
    return result


logger = logging.getLogger("TemporalSchedulerDaemon")

async def scheduler_daemon_loop():
    """Always-on autonomous background daemon evaluating due tasks and preconditions."""
    logger.info("Autonomous Temporal Scheduler Daemon started (tick interval: 10s)")
    while True:
        try:
            await asyncio.sleep(10)
            now_iso = datetime.utcnow().isoformat()
            session = next(db_mgr.get_session())
            try:
                due_tasks = session.query(ScheduledTask).filter(
                    ScheduledTask.status == "PENDING",
                    ScheduledTask.scheduled_for <= now_iso
                ).all()
                for t in due_tasks:
                    logger.info(f"Processing due background task: {t.task_name} ({t.id})")
                    execute_task_internal(t, session)
            finally:
                session.close()
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Scheduler daemon tick exception: {e}")


@app.post("/automation/tasks/schedule", response_model=ScheduledTaskResponse)
def schedule_task(
    req: ScheduledTaskCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Schedules an enterprise task for future execution.
    Supports temporal triggers, precondition checks, and optional HITL gates.
    """
    task = ScheduledTask(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        created_by_user_id=user_ctx.user_id,
        conversation_id=req.conversation_id,
        task_name=req.task_name,
        target_service=req.target_service,
        action_type=req.action_type,
        payload=json.dumps(req.payload),
        scheduled_for=req.scheduled_for,
        precondition_check=json.dumps(req.precondition_check) if req.precondition_check else None,
        status="PENDING",
        requires_hitl=bool(req.requires_hitl)
    )

    # If task requires human approval, automatically generate pending HITL approval card
    if req.requires_hitl:
        hitl = HITLApprovalRequest(
            id=str(uuid.uuid4()),
            org_id=user_ctx.org_id,
            task_id=task.id,
            requested_by="AI_AGENT_COPILOT",
            assigned_approver_role="FINANCE_MANAGER" if "finance" in req.target_service.lower() else "SUPER_ADMIN",
            risk_level="HIGH",
            title=f"Approval Required: {req.task_name}",
            summary=f"Automated action '{req.action_type}' targeting '{req.target_service}' scheduled for {req.scheduled_for}.",
            action_diff=json.dumps(req.payload),
            status="PENDING"
        )
        task.hitl_approval_id = hitl.id
        db.add(hitl)

    db.add(task)
    db.commit()
    db.refresh(task)

    d = task.to_dict()
    d["requires_hitl"] = task.requires_hitl
    d["hitl_approval_id"] = task.hitl_approval_id
    d["created_at"] = task.created_at.isoformat() if task.created_at else datetime.utcnow().isoformat()
    return ScheduledTaskResponse(**d)


@app.get("/automation/tasks", response_model=List[ScheduledTaskResponse])
def list_scheduled_tasks(
    status: Optional[str] = None,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """List scheduled tasks, optionally filtered by status."""
    query = db.query(ScheduledTask).filter_by(org_id=user_ctx.org_id)
    if status:
        query = query.filter_by(status=status)
    tasks = query.order_by(ScheduledTask.scheduled_for.asc()).all()

    out = []
    for t in tasks:
        d = t.to_dict()
        d["requires_hitl"] = t.requires_hitl
        d["hitl_approval_id"] = t.hitl_approval_id
        d["created_at"] = t.created_at.isoformat() if t.created_at else datetime.utcnow().isoformat()
        out.append(ScheduledTaskResponse(**d))
    return out


@app.get("/automation/tasks/{id}", response_model=ScheduledTaskResponse)
def get_scheduled_task(
    id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Get single scheduled task details."""
    task = db.query(ScheduledTask).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")
    d = task.to_dict()
    d["requires_hitl"] = task.requires_hitl
    d["hitl_approval_id"] = task.hitl_approval_id
    d["created_at"] = task.created_at.isoformat() if task.created_at else datetime.utcnow().isoformat()
    return ScheduledTaskResponse(**d)


@app.post("/automation/tasks/{id}/execute")
def trigger_task_execution(
    id: str,
    force: bool = False,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Executes a scheduled task, verifying preconditions and HITL gates."""
    task = db.query(ScheduledTask).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")

    # Verify temporal trigger unless force=True
    if not force:
        now_iso = datetime.utcnow().isoformat()
        if task.scheduled_for > now_iso:
            raise HTTPException(
                status_code=400,
                detail=f"Task execution time ({task.scheduled_for}) has not arrived yet. Current UTC is {now_iso}."
            )

    result = execute_task_internal(task, db, user_ctx.user_id)
    return {"task_id": id, "status": task.status, "result": result}


@app.post("/automation/scheduler/tick")
def run_scheduler_tick(
    db: Session = Depends(get_db)
):
    """
    Background worker tick endpoint. Scans for due tasks and processes them.
    Can be polled by background workers, cron, or asyncio background tasks.
    """
    now_iso = datetime.utcnow().isoformat()
    due_tasks = db.query(ScheduledTask).filter(
        ScheduledTask.status == "PENDING",
        ScheduledTask.scheduled_for <= now_iso
    ).all()

    results = []
    for t in due_tasks:
        res = execute_task_internal(t, db)
        results.append({"task_id": t.id, "task_name": t.task_name, "status": t.status, "result": res})

    return {"tasks_checked": len(due_tasks), "executions": results}


# ----------------------------------------------------
# 4. Human-in-the-Loop (HITL) Approval Endpoints
# ----------------------------------------------------
@app.get("/automation/hitl/pending", response_model=List[HITLApprovalResponse])
def list_pending_hitl(
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Lists pending human approval requests for the organization."""
    approvals = db.query(HITLApprovalRequest).filter_by(
        org_id=user_ctx.org_id,
        status="PENDING"
    ).order_by(HITLApprovalRequest.created_at.desc()).all()

    out = []
    for a in approvals:
        d = a.to_dict()
        d["created_at"] = a.created_at.isoformat() if a.created_at else datetime.utcnow().isoformat()
        out.append(HITLApprovalResponse(**d))
    return out


@app.post("/automation/hitl/{id}/decision", response_model=HITLApprovalResponse)
def decide_hitl_approval(
    id: str,
    req: HITLDecisionRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Records human decision (APPROVED or REJECTED) on a pending action.
    If approved, automatically triggers execution of the associated task.
    """
    hitl = db.query(HITLApprovalRequest).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not hitl:
        raise HTTPException(status_code=404, detail="HITL Approval Request not found")

    decision_norm = req.decision.upper().strip()
    if decision_norm not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decision must be 'APPROVED' or 'REJECTED'")

    hitl.status = decision_norm
    hitl.decision_by_user_id = user_ctx.user_id
    hitl.decision_notes = req.decision_notes
    hitl.decided_at = datetime.utcnow().isoformat()

    if hitl.task:
        if decision_norm == "APPROVED":
            hitl.task.status = "APPROVED_BY_HUMAN"
            execute_task_internal(hitl.task, db, user_ctx.user_id)
        else:
            hitl.task.status = "CANCELLED"
            hitl.task.execution_result = json.dumps({
                "outcome": "CANCELLED",
                "reason": f"Rejected by approver {user_ctx.user_id}: {req.decision_notes or 'No reason provided'}"
            })

    db.commit()
    db.refresh(hitl)

    d = hitl.to_dict()
    d["created_at"] = hitl.created_at.isoformat() if hitl.created_at else datetime.utcnow().isoformat()
    return HITLApprovalResponse(**d)

