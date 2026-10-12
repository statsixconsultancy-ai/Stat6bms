import os
import sys
import uuid
import json
from datetime import datetime, timedelta
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

from services.ai_copilot_service.models import AnomalyInsight, CopilotQueryLog
from services.ai_copilot_service.schemas import (
    CopilotQueryRequest, CopilotQueryResponse,
    AnomalyInsightResponse, CopilotSuggestionResponse,
    ChatbotRequest, ChatbotResponse, ScheduledTaskSummary, ChatMessage,
    DataTable, ConfirmationCard
)
from services.ai_copilot_service.engine import default_engine
from services.ai_copilot_service.tools.registry import default_registry
from services.ai_copilot_service.seed import seed_ai_copilot_data

config = get_service_config("ai-copilot-service", default_port=8013, db_filename="ai_copilot.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="BMS Autonomous AI Copilot & Executive Intelligence Microservice",
    description="Cross-Microservice Synthesis, Business Anomaly Detection & Proactive Operational Recommendations",
    version="2.0.0"
)

setup_microservice_middleware(app, "ai-copilot-service", config.cors_origins)

@app.on_event("startup")
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_ai_copilot_data(session)
    finally:
        session.close()

def get_db():
    yield from db_mgr.get_session()

# ----------------------------------------------------
# 1. Health Endpoint
# ----------------------------------------------------
@app.get("/health")
def health():
    return {"service": "ai-copilot-service", "status": "UP", "port": config.service_port}

# ----------------------------------------------------
# 2. Copilot Query Engine
# ----------------------------------------------------
@app.post("/ai/query", response_model=CopilotQueryResponse)
def handle_copilot_query(
    req: CopilotQueryRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Synthesizes enterprise data across all 14 BMS microservices to answer
    operational, commercial, financial, and strategic queries.
    """
    res = default_engine.process_request(
        message=req.query,
        page_context={"module": req.context_domain or "overview"},
        user_ctx=user_ctx
    )

    answer = res.get("reply", "")
    intent = res.get("intent", "EXECUTIVE_COCKPIT")
    sources = res.get("sources", ["gateway:8000"])
    metrics = res.get("immediate_data", {})
    recs = res.get("actions_suggested", [])

    # Log query
    try:
        log = CopilotQueryLog(
            id=str(uuid.uuid4()),
            org_id=user_ctx.org_id,
            user_id=user_ctx.user_id,
            query_text=req.query,
            intent=intent,
            response_text=answer,
            tool_calls_made=",".join(sources)
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

    return CopilotQueryResponse(
        query=req.query,
        intent=intent,
        answer=answer,
        sources=sources,
        key_metrics=metrics,
        recommendations=recs
    )

# ----------------------------------------------------
# 3. Anomaly Insights & Proactive Suggestions
# ----------------------------------------------------
@app.get("/ai/anomalies", response_model=List[AnomalyInsightResponse])
def list_anomalies(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    anomalies = db.query(AnomalyInsight).filter_by(org_id=user_ctx.org_id).all()
    return [AnomalyInsightResponse(**a.to_dict()) for a in anomalies]

@app.get("/ai/suggestions", response_model=List[CopilotSuggestionResponse])
def get_strategic_suggestions(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    return [
        CopilotSuggestionResponse(
            topic="Treasury Optimization",
            headline="High Cash Balance Idle in Low-Yield Operating Account",
            impact="+$4,200/mo incremental yield with zero operational risk.",
            suggested_action="Sweep $500,000 from Operating Cash 1010 to Treasury Yield Fund."
        ),
        CopilotSuggestionResponse(
            topic="Deal Velocity Acceleration",
            headline="Quantum Dynamics $250k Contract in Negotiation for 14 Days",
            impact="Closing before quarter-end increases Q3 target attainment to 142%.",
            suggested_action="Schedule executive sponsor sync with Dr. Eleanor Vance."
        ),
        CopilotSuggestionResponse(
            topic="Supply Chain Resilience",
            headline="Single-Source Supplier Concentration for LiDAR Sensors",
            impact="Avoid production bottleneck on rover delivery project ROBO-01.",
            suggested_action="Issue RFI to secondary sensor vendor to establish backup SLA."
        )
    ]


# ----------------------------------------------------
# 4. Omnipresent Agentic Chatbot Engine with Schema-Bound Tools & HITL
# ----------------------------------------------------
@app.get("/ai/tools")
def list_available_tools(user_ctx: UserContext = Depends(get_user_context)):
    """Returns the schema-bound tool catalogue permitted for the caller's authenticated role."""
    tools = default_registry.list_tools(user_ctx.role)
    return [
        {
            "name": t.name,
            "description": t.description,
            "category": t.category,
            "side_effect": t.side_effect.value,
            "output_tier": t.output_tier.value,
            "approval_requirement": t.approval_requirement.value,
            "approver_role": t.approver_role,
            "parameters": t.args_schema.model_json_schema()
        }
        for t in tools
    ]


@app.post("/ai/chat", response_model=ChatbotResponse)
def handle_chatbot_conversation(
    req: ChatbotRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Omnipresent Agentic Chatbot:
    1. Ingests natural language with DOM viewport context envelope.
    2. Executes schema-bound tool contracts with Pydantic validation.
    3. Enforces Tier 3 'Data Stays Home' privacy boundary for executive payroll/financials.
    4. Handles temporal background scheduling with HITL governance gates.
    """
    page_ctx_dict = req.page_context.model_dump() if req.page_context else {}
    history_list = [h.model_dump() for h in req.history] if req.history else []

    result = default_engine.process_request(
        message=req.message,
        page_context=page_ctx_dict,
        user_ctx=user_ctx,
        history=history_list
    )

    # Record cryptographic query audit log
    try:
        log = CopilotQueryLog(
            id=str(uuid.uuid4()),
            org_id=user_ctx.org_id,
            user_id=user_ctx.user_id,
            query_text=req.message,
            intent=result.get("intent", "GENERAL_ASSISTANT"),
            response_text=result.get("reply", ""),
            tool_calls_made=",".join(result.get("sources", []))
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

    scheduled_summary = None
    if result.get("scheduled_task"):
        st = result["scheduled_task"]
        scheduled_summary = ScheduledTaskSummary(
            task_id=st.get("task_id"),
            task_name=st.get("task_name"),
            target_service=st.get("target_service"),
            scheduled_for=st.get("scheduled_for"),
            requires_hitl=st.get("requires_hitl", False),
            hitl_approval_id=st.get("hitl_approval_id"),
            status=st.get("status", "PENDING")
        )

    data_tbl = None
    if result.get("data_table"):
        dt = result["data_table"]
        data_tbl = DataTable(
            columns=dt.get("columns", []),
            rows=dt.get("rows", [])
        )

    conf_card = None
    if result.get("confirmation_card"):
        cc = result["confirmation_card"]
        conf_card = ConfirmationCard(
            action=cc.get("action", "CONFIRM"),
            title=cc.get("title", ""),
            details=cc.get("details", "")
        )

    return ChatbotResponse(
        reply=result.get("reply", ""),
        intent=result.get("intent", "EXECUTIVE_COCKPIT"),
        immediate_data=result.get("immediate_data", {}),
        scheduled_task=scheduled_summary,
        data_table=data_tbl,
        confirmation_card=conf_card,
        sources=result.get("sources", []),
        actions_suggested=result.get("actions_suggested", []),
        output_tier=result.get("output_tier", "TIER_1_INTERNAL")
    )


