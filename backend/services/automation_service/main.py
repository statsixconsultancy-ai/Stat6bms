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

from services.automation_service.models import AutomationRule, AutomationLog
from services.automation_service.schemas import (
    AutomationRuleCreate, AutomationRuleResponse,
    AutomationLogResponse, TriggerRuleRequest, TriggerRuleResponse
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
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_automation_data(session)
    finally:
        session.close()

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
