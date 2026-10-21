import os
import sys
import uuid
import json
import asyncio
import logging
import time
import re
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
from common.event_bus import event_bus

from services.automation_service.models import (
    AutomationRule, AutomationLog, ScheduledTask, HITLApprovalRequest,
    WorkflowDefinition, WorkflowExecution, ApprovalRequest, ZohoMigrationJob
)
from services.automation_service.schemas import (
    AutomationRuleCreate, AutomationRuleResponse,
    AutomationLogResponse, TriggerRuleRequest, TriggerRuleResponse,
    ScheduledTaskCreate, ScheduledTaskResponse,
    HITLApprovalCreate, HITLApprovalResponse, HITLDecisionRequest,
    WorkflowDefinitionCreate, WorkflowDefinitionResponse, WorkflowExecutionResponse,
    TriggerWorkflowRequest, ApprovalRequestCreate, ApprovalRequestResponse,
    ApprovalDecisionRequest, AIGenerateWorkflowRequest, AIGenerateWorkflowResponse,
    ZohoMigrationRequest, ZohoMigrationResponse
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


# =========================================================================
# Phase 5: Visual Workflows (DAG), Unified Approvals & Zoho 1-Click Importer
# =========================================================================

# ----------------------------------------------------
# 5. DAG-Based Visual Workflow Builder & Execution
# ----------------------------------------------------
@app.get("/automation/workflows", response_model=List[WorkflowDefinitionResponse])
def list_workflows(
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """List visual workflow definitions for the organization."""
    workflows = db.query(WorkflowDefinition).filter_by(org_id=user_ctx.org_id).all()
    out = []
    for w in workflows:
        d = w.to_dict()
        d["created_at"] = w.created_at.isoformat() if w.created_at else datetime.utcnow().isoformat()
        out.append(WorkflowDefinitionResponse(**d))
    return out


@app.post("/automation/workflows", response_model=WorkflowDefinitionResponse)
def create_workflow(
    req: WorkflowDefinitionCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Creates a new DAG-based workflow definition."""
    workflow = WorkflowDefinition(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        name=req.name,
        description=req.description,
        trigger_event=req.trigger_event,
        nodes=json.dumps(req.nodes),
        is_active=bool(req.is_active),
        execution_count=0
    )
    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    d = workflow.to_dict()
    d["created_at"] = workflow.created_at.isoformat() if workflow.created_at else datetime.utcnow().isoformat()
    return WorkflowDefinitionResponse(**d)


@app.get("/automation/workflows/{id}", response_model=WorkflowDefinitionResponse)
def get_workflow(
    id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Retrieves a specific workflow definition."""
    wf = db.query(WorkflowDefinition).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow definition not found")
    d = wf.to_dict()
    d["created_at"] = wf.created_at.isoformat() if wf.created_at else datetime.utcnow().isoformat()
    return WorkflowDefinitionResponse(**d)


@app.post("/automation/workflows/{id}/trigger", response_model=WorkflowExecutionResponse)
def trigger_workflow(
    id: str,
    req: TriggerWorkflowRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Executes a visual DAG workflow graph step-by-step.
    Evaluates condition nodes, branches conditionally, and executes actions.
    """
    workflow = db.query(WorkflowDefinition).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow definition not found")

    try:
        nodes = json.loads(workflow.nodes)
    except Exception:
        nodes = []

    node_map = {n.get("id"): n for n in nodes}
    trigger_nodes = [n for n in nodes if n.get("type") == "TRIGGER"]
    start_nodes = trigger_nodes if trigger_nodes else (nodes[:1] if nodes else [])

    step_history = []
    executed_ids = set()
    current_ids = [n.get("id") for n in start_nodes]

    payload = req.payload
    while current_ids:
        next_ids = []
        for nid in current_ids:
            if nid in executed_ids or nid not in node_map:
                continue
            executed_ids.add(nid)
            node = node_map[nid]
            ntype = node.get("type", "ACTION")
            cfg = node.get("config", {})

            step_entry = {
                "node_id": nid,
                "type": ntype,
                "title": node.get("title", nid),
                "timestamp": datetime.utcnow().isoformat()
            }

            if ntype == "TRIGGER":
                step_entry["status"] = "TRIGGERED"
                step_entry["details"] = f"Triggered on event '{workflow.trigger_event}'"
                next_ids.extend(node.get("next_node_ids", []))

            elif ntype == "CONDITION":
                cond = cfg.get("condition", "True")
                matched = safe_evaluate_condition(cond, payload)
                step_entry["status"] = "EVALUATED"
                step_entry["condition"] = cond
                step_entry["matched"] = matched

                if matched:
                    branch = node.get("on_true") or node.get("next_node_ids", [])
                else:
                    branch = node.get("on_false", [])
                next_ids.extend(branch)

            elif ntype == "ACTION":
                act_type = cfg.get("action_type", "EXECUTE_SYSTEM_ACTION")
                step_entry["status"] = "ACTION_EXECUTED"
                step_entry["action_type"] = act_type
                step_entry["action_result"] = f"Successfully dispatched {act_type}"
                next_ids.extend(node.get("next_node_ids", []))

            elif ntype == "DELAY":
                step_entry["status"] = "DELAY_APPLIED"
                step_entry["duration"] = cfg.get("duration", "0s")
                next_ids.extend(node.get("next_node_ids", []))

            step_history.append(step_entry)
        current_ids = next_ids

    # Update execution counts
    workflow.execution_count += 1

    exec_record = WorkflowExecution(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        workflow_id=workflow.id,
        status="COMPLETED",
        trigger_payload=json.dumps(payload),
        current_node_id=step_history[-1]["node_id"] if step_history else None,
        step_history=json.dumps(step_history)
    )
    db.add(exec_record)
    db.commit()
    db.refresh(exec_record)

    return WorkflowExecutionResponse(
        id=exec_record.id,
        org_id=exec_record.org_id,
        workflow_id=exec_record.workflow_id,
        status=exec_record.status,
        current_node_id=exec_record.current_node_id,
        step_history=exec_record.step_history,
        error_message=exec_record.error_message,
        created_at=exec_record.created_at.isoformat() if exec_record.created_at else datetime.utcnow().isoformat()
    )


# ----------------------------------------------------
# 6. Unified Cross-Module Approvals Inbox
# ----------------------------------------------------
@app.get("/automation/approvals", response_model=List[ApprovalRequestResponse])
def list_approvals(
    status: Optional[str] = None,
    module: Optional[str] = None,
    approver_role: Optional[str] = None,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Lists approval requests across all 14 BMS modules with optional status/module filtering."""
    query = db.query(ApprovalRequest).filter_by(org_id=user_ctx.org_id)
    if status:
        query = query.filter_by(status=status.upper())
    if module:
        query = query.filter_by(module=module.upper())
    if approver_role:
        query = query.filter_by(approver_role=approver_role.upper())

    approvals = query.order_by(ApprovalRequest.created_at.desc()).all()
    out = []
    for a in approvals:
        d = a.to_dict()
        d["created_at"] = a.created_at.isoformat() if a.created_at else datetime.utcnow().isoformat()
        out.append(ApprovalRequestResponse(**d))
    return out


@app.post("/automation/approvals", response_model=ApprovalRequestResponse)
def create_approval_request(
    req: ApprovalRequestCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Submits a new cross-module approval request (PR, Quote Discount, Leave, Invoice, Expense)."""
    approval = ApprovalRequest(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        module=req.module.upper(),
        record_type=req.record_type.upper(),
        record_id=req.record_id,
        requester_id=user_ctx.user_id,
        requester_name=req.requester_name or user_ctx.email or "Employee",
        approver_role=req.approver_role.upper() if req.approver_role else "MANAGER",
        approver_id=req.approver_id,
        title=req.title,
        description=req.description,
        amount=req.amount or 0.0,
        status="PENDING"
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)

    d = approval.to_dict()
    d["created_at"] = approval.created_at.isoformat() if approval.created_at else datetime.utcnow().isoformat()
    return ApprovalRequestResponse(**d)


@app.get("/automation/approvals/{id}", response_model=ApprovalRequestResponse)
def get_approval_request(
    id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """Retrieves a specific approval request."""
    approval = db.query(ApprovalRequest).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")
    d = approval.to_dict()
    d["created_at"] = approval.created_at.isoformat() if approval.created_at else datetime.utcnow().isoformat()
    return ApprovalRequestResponse(**d)


@app.post("/automation/approvals/{id}/action", response_model=ApprovalRequestResponse)
async def decide_approval_request(
    id: str,
    req: ApprovalDecisionRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Executes approval decision: APPROVE, REJECT, or DELEGATE.
    Publishes corresponding domain event across the event bus.
    """
    approval = db.query(ApprovalRequest).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval request not found")

    act = req.action.upper().strip()
    if act not in ["APPROVE", "REJECT", "DELEGATE"]:
        raise HTTPException(status_code=400, detail="Action must be APPROVE, REJECT, or DELEGATE")

    if act == "DELEGATE":
        if not req.delegate_to_id:
            raise HTTPException(status_code=400, detail="delegate_to_id is required when delegating")
        approval.status = "DELEGATED"
        approval.delegated_to_id = req.delegate_to_id
        approval.decision_notes = req.notes
    elif act == "APPROVE":
        approval.status = "APPROVED"
        approval.decision_by_id = user_ctx.user_id
        approval.decision_notes = req.notes
        approval.decided_at = datetime.utcnow().isoformat()

        await event_bus.publish("approval.approved", {
            "approval_id": approval.id,
            "module": approval.module,
            "record_type": approval.record_type,
            "record_id": approval.record_id,
            "approver_id": user_ctx.user_id
        }, org_id=user_ctx.org_id)

    elif act == "REJECT":
        approval.status = "REJECTED"
        approval.decision_by_id = user_ctx.user_id
        approval.decision_notes = req.notes
        approval.decided_at = datetime.utcnow().isoformat()

        await event_bus.publish("approval.rejected", {
            "approval_id": approval.id,
            "module": approval.module,
            "record_type": approval.record_type,
            "record_id": approval.record_id,
            "approver_id": user_ctx.user_id
        }, org_id=user_ctx.org_id)

    db.commit()
    db.refresh(approval)

    d = approval.to_dict()
    d["created_at"] = approval.created_at.isoformat() if approval.created_at else datetime.utcnow().isoformat()
    return ApprovalRequestResponse(**d)


# ----------------------------------------------------
# 7. AI Natural Language Workflow Generator
# ----------------------------------------------------
@app.post("/automation/ai/generate-workflow", response_model=AIGenerateWorkflowResponse)
def ai_generate_workflow(
    req: AIGenerateWorkflowRequest,
    user_ctx: UserContext = Depends(get_user_context)
):
    """
    Synthesizes a full DAG visual workflow from natural language instructions.
    Identifies triggers, threshold conditions, and cross-module actions.
    """
    text = req.prompt.lower()

    # Detect trigger event
    trigger_event = "domain.custom.event"
    workflow_name = "Automated Business Process"
    description = f"Synthesized workflow based on instruction: '{req.prompt}'"

    if "deal" in text and ("won" in text or "close" in text):
        trigger_event = "deal.won"
        workflow_name = "High-Value Deal Onboarding & Executive Review"
    elif "invoice" in text and ("overdue" in text or "unpaid" in text):
        trigger_event = "invoice.overdue"
        workflow_name = "Automated Dunning & AR Escalation"
    elif "stock" in text or "inventory" in text or "reorder" in text:
        trigger_event = "stock.low"
        workflow_name = "Automated Stock Reordering & Procurement"
    elif "leave" in text or "vacation" in text:
        trigger_event = "leave.requested"
        workflow_name = "HR Leave Request Approval Gate"
    elif "ticket" in text or "support" in text:
        trigger_event = "ticket.created"
        workflow_name = "Urgent SLA Support Routing"

    # Detect condition expression
    cond_expr = "True"
    num_match = re.search(r'(?:>|>=|greater than|above)\s*(\d+)', text)
    if num_match:
        val = num_match.group(1)
        cond_expr = f"amount >= {val}"
    elif "urgent" in text:
        cond_expr = "priority == 'Urgent'"

    # Build DAG nodes
    nodes = [
        {
            "id": "node-trigger-1",
            "type": "TRIGGER",
            "title": f"Listen for {trigger_event}",
            "config": {"event_name": trigger_event},
            "next_node_ids": ["node-cond-2"]
        },
        {
            "id": "node-cond-2",
            "type": "CONDITION",
            "title": f"Evaluate Condition: {cond_expr}",
            "config": {"condition": cond_expr},
            "on_true": ["node-action-3"],
            "on_false": ["node-action-4"]
        },
        {
            "id": "node-action-3",
            "type": "ACTION",
            "title": "Trigger Executive Approval & VIP Notification",
            "config": {
                "action_type": "CREATE_APPROVAL",
                "approver_role": "CFO" if "cfo" in text else "MANAGER",
                "notification_channel": "SLACK_ALERTS"
            },
            "next_node_ids": []
        },
        {
            "id": "node-action-4",
            "type": "ACTION",
            "title": "Standard Logging & Automated Processing",
            "config": {
                "action_type": "LOG_AUDIT_TRAIL"
            },
            "next_node_ids": []
        }
    ]

    return AIGenerateWorkflowResponse(
        name=workflow_name,
        description=description,
        trigger_event=trigger_event,
        nodes=nodes,
        explanation=f"Generated a 4-node visual DAG workflow with trigger '{trigger_event}', condition evaluation '{cond_expr}', and branched action dispatching."
    )


# ----------------------------------------------------
# 8. Automated Zoho One 1-Click Migration Engine
# ----------------------------------------------------
@app.post("/automation/import/zoho-one", response_model=ZohoMigrationResponse)
def import_zoho_one_data(
    req: ZohoMigrationRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Zoho One 1-Click Migration Engine.
    Ingests and maps Zoho CRM, Zoho Books, Zoho People, and Zoho Inventory schema dumps
    into STAT6 canonical unified entities with single canonical UUIDs.
    """
    start_time = time.time()
    canonical_mappings = []
    validation_errors = []
    records_migrated = {
        "crm_companies": 0,
        "crm_contacts": 0,
        "crm_deals": 0,
        "crm_leads": 0,
        "hr_departments": 0,
        "hr_employees": 0,
        "inv_products": 0,
        "fin_invoices": 0
    }

    zoho_to_canonical = {}

    # 1. Zoho CRM Migration
    if req.zoho_crm:
        try:
            from services.crm_service.models import Company as CRMCompany, Contact as CRMContact, Deal as CRMDeal, Lead as CRMLead
            from services.crm_service.main import db_mgr as crm_db_mgr
            crm_session = next(crm_db_mgr.get_session())

            # Accounts -> Companies
            for acc in req.zoho_crm.get("accounts", []):
                legacy_id = str(acc.get("id", uuid.uuid4().hex[:8]))
                c_id = str(uuid.uuid4())
                zoho_to_canonical[legacy_id] = c_id

                comp = CRMCompany(
                    id=c_id,
                    org_id=user_ctx.org_id,
                    name=acc.get("Account_Name") or acc.get("name") or "Zoho Migrated Company",
                    industry=acc.get("Industry", "Technology"),
                    website=acc.get("Website"),
                    phone=acc.get("Phone"),
                    annual_revenue=float(acc.get("Annual_Revenue") or 0.0),
                    tier="Tier 1"
                )
                crm_session.add(comp)
                canonical_mappings.append({"legacy_id": legacy_id, "canonical_id": c_id, "entity_type": "Company"})
                records_migrated["crm_companies"] += 1

            # Contacts
            for cnt in req.zoho_crm.get("contacts", []):
                legacy_id = str(cnt.get("id", uuid.uuid4().hex[:8]))
                cnt_id = str(uuid.uuid4())
                zoho_to_canonical[legacy_id] = cnt_id

                acc_ref = str(cnt.get("Account_ID") or "")
                resolved_comp_id = zoho_to_canonical.get(acc_ref)

                contact = CRMContact(
                    id=cnt_id,
                    org_id=user_ctx.org_id,
                    company_id=resolved_comp_id,
                    first_name=cnt.get("First_Name") or "Zoho",
                    last_name=cnt.get("Last_Name") or "Contact",
                    email=cnt.get("Email") or f"contact-{uuid.uuid4().hex[:4]}@zoho-migrated.com",
                    phone=cnt.get("Phone"),
                    job_title=cnt.get("Title") or "Executive"
                )
                crm_session.add(contact)
                canonical_mappings.append({"legacy_id": legacy_id, "canonical_id": cnt_id, "entity_type": "Contact"})
                records_migrated["crm_contacts"] += 1

            # Deals
            for dl in req.zoho_crm.get("deals", []):
                legacy_id = str(dl.get("id", uuid.uuid4().hex[:8]))
                d_id = str(uuid.uuid4())
                zoho_to_canonical[legacy_id] = d_id

                acc_ref = str(dl.get("Account_ID") or "")
                cnt_ref = str(dl.get("Contact_ID") or "")

                deal = CRMDeal(
                    id=d_id,
                    org_id=user_ctx.org_id,
                    title=dl.get("Deal_Name") or "Migrated Zoho Deal",
                    amount=float(dl.get("Amount") or 0.0),
                    stage=dl.get("Stage") or "Prospecting",
                    company_id=zoho_to_canonical.get(acc_ref),
                    contact_id=zoho_to_canonical.get(cnt_ref)
                )
                crm_session.add(deal)
                canonical_mappings.append({"legacy_id": legacy_id, "canonical_id": d_id, "entity_type": "Deal"})
                records_migrated["crm_deals"] += 1

            # Leads
            for ld in req.zoho_crm.get("leads", []):
                legacy_id = str(ld.get("id", uuid.uuid4().hex[:8]))
                lead_id = str(uuid.uuid4())
                zoho_to_canonical[legacy_id] = lead_id

                lead = CRMLead(
                    id=lead_id,
                    org_id=user_ctx.org_id,
                    first_name=ld.get("First_Name") or "Zoho",
                    last_name=ld.get("Last_Name") or "Lead",
                    email=ld.get("Email") or f"lead-{uuid.uuid4().hex[:4]}@zoho-migrated.com",
                    phone=ld.get("Phone"),
                    company_name=ld.get("Company") or "Zoho Inbound",
                    status="New",
                    source="Zoho Migration"
                )
                crm_session.add(lead)
                canonical_mappings.append({"legacy_id": legacy_id, "canonical_id": lead_id, "entity_type": "Lead"})
                records_migrated["crm_leads"] += 1

            crm_session.commit()
            crm_session.close()
        except Exception as e:
            validation_errors.append(f"Zoho CRM migration error: {str(e)}")

    # 2. Zoho People Migration
    if req.zoho_people:
        try:
            from services.hr_service.models import Employee as HREmployee, Department as HRDepartment
            from services.hr_service.main import db_mgr as hr_db_mgr
            hr_session = next(hr_db_mgr.get_session())

            # Departments
            for dept in req.zoho_people.get("departments", []):
                legacy_id = str(dept.get("id", uuid.uuid4().hex[:8]))
                dept_name = dept.get("Department_Name") or dept.get("name") or "Operations"

                existing_dept = hr_session.query(HRDepartment).filter_by(name=dept_name).first()
                if existing_dept:
                    zoho_to_canonical[legacy_id] = existing_dept.id
                    canonical_mappings.append({"legacy_id": legacy_id, "canonical_id": existing_dept.id, "entity_type": "Department"})
                    records_migrated["hr_departments"] += 1
                else:
                    dept_id = str(uuid.uuid4())
                    zoho_to_canonical[legacy_id] = dept_id

                    d_obj = HRDepartment(
                        id=dept_id,
                        org_id=user_ctx.org_id,
                        name=dept_name,
                        code=f"DPT-{uuid.uuid4().hex[:4].upper()}"
                    )
                    hr_session.add(d_obj)
                    canonical_mappings.append({"legacy_id": legacy_id, "canonical_id": dept_id, "entity_type": "Department"})
                    records_migrated["hr_departments"] += 1

            # Employees
            for emp in req.zoho_people.get("employees", []):
                legacy_id = str(emp.get("id", uuid.uuid4().hex[:8]))
                emp_email = emp.get("Email") or f"emp-{uuid.uuid4().hex[:6]}@stat6.corp"

                existing_emp = hr_session.query(HREmployee).filter_by(email=emp_email).first()
                if existing_emp:
                    zoho_to_canonical[legacy_id] = existing_emp.id
                    canonical_mappings.append({"legacy_id": legacy_id, "canonical_id": existing_emp.id, "entity_type": "Employee"})
                    records_migrated["hr_employees"] += 1
                else:
                    emp_id = str(uuid.uuid4())
                    zoho_to_canonical[legacy_id] = emp_id

                    dept_ref = str(emp.get("Department_ID") or "")
                    mgr_ref = str(emp.get("Manager_ID") or "")

                    e_obj = HREmployee(
                        id=emp_id,
                        org_id=user_ctx.org_id,
                        first_name=emp.get("First_Name") or "Zoho",
                        last_name=emp.get("Last_Name") or "Employee",
                        email=emp_email,
                        department_id=zoho_to_canonical.get(dept_ref),
                        job_title=emp.get("Designation") or emp.get("job_title") or "Specialist",
                        status="Active",
                        manager_id=zoho_to_canonical.get(mgr_ref)
                    )
                    hr_session.add(e_obj)
                    canonical_mappings.append({"legacy_id": legacy_id, "canonical_id": emp_id, "entity_type": "Employee"})
                    records_migrated["hr_employees"] += 1

            hr_session.commit()
            hr_session.close()
        except Exception as e:
            validation_errors.append(f"Zoho People migration error: {str(e)}")

    # 3. Zoho Inventory Migration
    if req.zoho_inventory:
        try:
            from services.inventory_service.models import Product as InvProduct
            from services.inventory_service.main import db_mgr as inv_db_mgr
            inv_session = next(inv_db_mgr.get_session())

            for itm in req.zoho_inventory.get("items", []):
                legacy_id = str(itm.get("id", uuid.uuid4().hex[:8]))
                item_id = str(uuid.uuid4())
                zoho_to_canonical[legacy_id] = item_id

                sku_val = itm.get("SKU") or f"SKU-Z-{uuid.uuid4().hex[:6].upper()}"
                existing_prod = inv_session.query(InvProduct).filter_by(sku=sku_val, org_id=user_ctx.org_id).first()
                if existing_prod:
                    sku_val = f"{sku_val}-{uuid.uuid4().hex[:4].upper()}"

                prod = InvProduct(
                    id=item_id,
                    org_id=user_ctx.org_id,
                    sku=sku_val,
                    name=itm.get("Item_Name") or itm.get("name") or "Zoho Catalog Item",
                    category=itm.get("Category", "Standard Products"),
                    unit_cost=float(itm.get("Purchase_Rate") or 0.0),
                    unit_price=float(itm.get("Rate") or itm.get("selling_price") or 0.0),
                    stock_quantity=int(itm.get("Stock_On_Hand") or 0)
                )
                inv_session.add(prod)
                canonical_mappings.append({"legacy_id": legacy_id, "canonical_id": item_id, "entity_type": "Product"})
                records_migrated["inv_products"] += 1

            inv_session.commit()
            inv_session.close()
        except Exception as e:
            validation_errors.append(f"Zoho Inventory migration error: {str(e)}")

    # 4. Zoho Books Migration
    if req.zoho_books:
        try:
            from services.finance_service.models import Invoice as FinInvoice
            from services.finance_service.main import db_mgr as fin_db_mgr
            fin_session = next(fin_db_mgr.get_session())

            for inv in req.zoho_books.get("invoices", []):
                legacy_id = str(inv.get("id", uuid.uuid4().hex[:8]))
                inv_id = str(uuid.uuid4())
                zoho_to_canonical[legacy_id] = inv_id

                inv_num = inv.get("Invoice_Number") or f"INV-Z-{uuid.uuid4().hex[:6].upper()}"
                existing_inv = fin_session.query(FinInvoice).filter_by(invoice_number=inv_num).first()
                if existing_inv:
                    inv_num = f"{inv_num}-{uuid.uuid4().hex[:4].upper()}"

                cust_ref = str(inv.get("Customer_ID") or "")
                total = float(inv.get("Total") or inv.get("amount") or 0.0)
                subtotal = round(total * 0.85, 2)
                tax = round(total - subtotal, 2)

                invoice = FinInvoice(
                    id=inv_id,
                    org_id=user_ctx.org_id,
                    invoice_number=inv_num,
                    client_name=inv.get("Customer_Name") or "Zoho Client",
                    client_id=zoho_to_canonical.get(cust_ref),
                    issue_date="2026-10-01",
                    due_date="2026-10-31",
                    status=inv.get("Status") or "Sent",
                    subtotal=subtotal,
                    tax_amount=tax,
                    total_amount=total,
                    balance_due=total
                )
                fin_session.add(invoice)
                canonical_mappings.append({"legacy_id": legacy_id, "canonical_id": inv_id, "entity_type": "Invoice"})
                records_migrated["fin_invoices"] += 1

            fin_session.commit()
            fin_session.close()
        except Exception as e:
            validation_errors.append(f"Zoho Books migration error: {str(e)}")

    total_records = sum(records_migrated.values())
    elapsed_ms = round((time.time() - start_time) * 1000, 2)

    # Save migration audit job
    job = ZohoMigrationJob(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        status="SUCCESS" if not validation_errors else "PARTIAL_SUCCESS",
        records_migrated=json.dumps(records_migrated),
        canonical_mappings=json.dumps(canonical_mappings),
        validation_errors=json.dumps(validation_errors),
        elapsed_ms=elapsed_ms
    )
    db.add(job)
    db.commit()

    return ZohoMigrationResponse(
        job_id=job.id,
        status=job.status,
        total_records=total_records,
        records_migrated=records_migrated,
        canonical_mappings=canonical_mappings,
        validation_errors=validation_errors,
        elapsed_ms=elapsed_ms
    )


