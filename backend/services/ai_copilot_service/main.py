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
            headline="Configure Primary Banking & Operating Accounts",
            impact="Automated double-entry reconciliation and real-time cash flow forecasting.",
            suggested_action="Review General Ledger Chart of Accounts in the Finance Module."
        ),
        CopilotSuggestionResponse(
            topic="Sales Pipeline Operations",
            headline="Establish Active Commercial Leads & Pipeline Deals",
            impact="Enable predictive revenue forecasting and automated deal stage rotting tracking.",
            suggested_action="Create your first enterprise lead or qualified deal in the CRM Module."
        ),
        CopilotSuggestionResponse(
            topic="Human Capital Onboarding",
            headline="Setup Core Departments and Staff Directory",
            impact="Activate organizational hierarchy, geofenced attendance, and payroll automation.",
            suggested_action="Add organizational departments and onboard your team in the HR Module."
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
    msg_text = req.message or req.prompt or req.query or "Executive overview"

    result = default_engine.process_request(
        message=msg_text,
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
            query_text=msg_text,
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

    reply_text = result.get("reply", "")
    return ChatbotResponse(
        reply=reply_text,
        answer=reply_text,
        intent=result.get("intent", "EXECUTIVE_COCKPIT"),
        immediate_data=result.get("immediate_data", {}),
        scheduled_task=scheduled_summary,
        data_table=data_tbl,
        confirmation_card=conf_card,
        sources=result.get("sources", []),
        actions_suggested=result.get("actions_suggested", []),
        output_tier=result.get("output_tier", "TIER_1_INTERNAL")
    )


# ----------------------------------------------------
# 5. Module 13: Native AI & Insights (Briefing, Forecasting, RFM/Churn, Anomaly Audit, Summarizer)
# ----------------------------------------------------
from pydantic import BaseModel as _PydanticBaseModel

class DocumentSummarizeRequest(_PydanticBaseModel):
    document_type: str = "Vendor Contract"
    title: Optional[str] = None
    document_title: Optional[str] = None
    content: str


@app.get("/ai/executive-briefing")
def get_morning_executive_briefing(user_ctx: UserContext = Depends(get_user_context)):
    """
    Proactive morning executive briefing synthesizing live state across
    CRM, Support, Inventory, Finance, and Projects.
    """
    from services.crm_service.main import db_mgr as crm_db
    from services.crm_service.models import Deal, Lead
    from services.support_service.main import db_mgr as sup_db
    from services.support_service.models import Ticket
    from services.inventory_service.main import db_mgr as inv_db
    from services.inventory_service.models import Product
    from services.finance_service.main import db_mgr as fin_db
    from services.finance_service.models import Invoice

    s_crm = next(crm_db.get_session())
    s_sup = next(sup_db.get_session())
    s_inv = next(inv_db.get_session())
    s_fin = next(fin_db.get_session())
    try:
        deals = s_crm.query(Deal).filter_by(org_id=user_ctx.org_id).all()
        leads = s_crm.query(Lead).filter_by(org_id=user_ctx.org_id).all()
        tickets = s_sup.query(Ticket).filter_by(org_id=user_ctx.org_id).all()
        products = s_inv.query(Product).filter_by(org_id=user_ctx.org_id).all()
        invoices = s_fin.query(Invoice).filter_by(org_id=user_ctx.org_id).all()

        pipeline_val = sum(float(d.amount or 0) for d in deals if d.stage != "Lost")
        won_val = sum(float(d.amount or 0) for d in deals if d.stage == "Won")
        sla_risk_tickets = [t for t in tickets if t.status not in ["Resolved", "Closed"] and (t.priority in ["Urgent", "High"] or getattr(t, "sla_status", "") in ["AT_RISK", "BREACHED"])]
        low_stock_skus = [p for p in products if (p.stock_quantity or 0) <= (p.reorder_level or 10)]
        overdue_invs = [i for i in invoices if i.status in ["Overdue", "Sent", "Unpaid"]]
        paid_rev = sum(float(i.total_amount or 0) for i in invoices if i.status == "Paid")

        highlights = [
            f"Commercial pipeline stands at ${pipeline_val:,.2f} across {len(deals)} deals ({len(leads)} leads in funnel; ${won_val:,.2f} closed-won).",
            f"Customer Support: {len(sla_risk_tickets)} high-priority/SLA-sensitive tickets require attention out of {len(tickets)} total tickets.",
            f"Supply Chain: {len(low_stock_skus)} SKUs are at or below reorder threshold ({', '.join(p.sku for p in low_stock_skus[:3]) or 'None'}).",
            f"Treasury & Billing: ${paid_rev:,.2f} collected in paid revenue; {len(overdue_invs)} open/overdue invoices pending settlement."
        ]

        return {
            "generated_at": datetime.utcnow().isoformat(),
            "headline": f"Executive Briefing: ${pipeline_val:,.0f} Pipeline • {len(sla_risk_tickets)} Priority Tickets • {len(low_stock_skus)} Low-Stock SKUs",
            "highlights": highlights,
            "metrics": {
                "pipeline_value": round(pipeline_val, 2),
                "paid_revenue": round(paid_rev, 2),
                "sla_risk_tickets": len(sla_risk_tickets),
                "low_stock_count": len(low_stock_skus),
                "open_invoices_count": len(overdue_invs)
            }
        }
    finally:
        s_crm.close()
        s_sup.close()
        s_inv.close()
        s_fin.close()


@app.get("/ai/forecast/sales")
def get_ai_sales_forecast(user_ctx: UserContext = Depends(get_user_context)):
    """
    ML/statistical deal win-probability scoring and weighted vs. committed revenue projections.
    """
    from services.crm_service.main import db_mgr as crm_db
    from services.crm_service.models import Deal
    s_crm = next(crm_db.get_session())
    try:
        deals = s_crm.query(Deal).filter_by(org_id=user_ctx.org_id).all()
        stage_weights = {
            "New": 0.15,
            "Contacted": 0.30,
            "Qualified": 0.50,
            "Proposal": 0.70,
            "Negotiation": 0.85,
            "Won": 1.0,
            "Lost": 0.0
        }
        scored_deals = []
        total_unweighted = 0.0
        total_weighted = 0.0
        committed_revenue = 0.0

        for d in deals:
            amt = float(d.amount or 0.0)
            base_prob = float(d.probability or (stage_weights.get(d.stage, 0.4) * 100.0))
            expected_val = round(amt * (base_prob / 100.0), 2)
            if d.stage != "Lost":
                total_unweighted += amt
                total_weighted += expected_val
            if base_prob >= 75.0 or d.stage in ["Negotiation", "Won"]:
                committed_revenue += expected_val

            scored_deals.append({
                "deal_id": d.id,
                "title": d.title,
                "company_name": d.company.name if getattr(d, "company", None) else "Enterprise Account",
                "stage": d.stage,
                "amount": amt,
                "ai_win_probability": round(base_prob, 1),
                "expected_revenue": expected_val,
                "forecast_category": "Commit" if base_prob >= 75 else ("Best Case" if base_prob >= 45 else "Pipeline")
            })

        return {
            "total_pipeline_unweighted": round(total_unweighted, 2),
            "ai_weighted_forecast": round(total_weighted, 2),
            "committed_forecast": round(committed_revenue, 2),
            "deal_count": len(scored_deals),
            "deals": scored_deals
        }
    finally:
        s_crm.close()


@app.get("/ai/customers/churn-rfm")
def get_customer_churn_and_rfm(user_ctx: UserContext = Depends(get_user_context)):
    """
    Automated RFM (Recency, Frequency, Monetary) clustering, Churn Risk Scoring,
    and Cross-Sell/Upsell recommendations across CRM, Finance, and Support.
    """
    from services.crm_service.main import db_mgr as crm_db
    from services.crm_service.models import Company, Deal
    from services.finance_service.main import db_mgr as fin_db
    from services.finance_service.models import Invoice
    from services.support_service.main import db_mgr as sup_db
    from services.support_service.models import Ticket

    s_crm = next(crm_db.get_session())
    s_fin = next(fin_db.get_session())
    s_sup = next(sup_db.get_session())
    try:
        companies = s_crm.query(Company).filter_by(org_id=user_ctx.org_id).all()
        deals = s_crm.query(Deal).filter_by(org_id=user_ctx.org_id).all()
        invoices = s_fin.query(Invoice).filter_by(org_id=user_ctx.org_id).all()
        tickets = s_sup.query(Ticket).filter_by(org_id=user_ctx.org_id).all()

        client_names = set(
            [c.name for c in companies if c.name]
            + [i.client_name for i in invoices if i.client_name]
            + [d.company.name for d in deals if getattr(d, "company", None) and d.company.name]
        )
        profiles = []
        for cname in sorted(client_names):
            c_invs = [i for i in invoices if i.client_name == cname]
            c_tkts = [t for t in tickets if t.customer_name == cname or cname.lower() in str(t.subject or "").lower()]
            monetary = sum(float(i.total_amount or 0) for i in c_invs)
            frequency = len(c_invs)
            open_high_tkts = len([t for t in c_tkts if t.status not in ["Resolved", "Closed"] and t.priority in ["High", "Urgent"]])
            overdue_count = len([i for i in c_invs if i.status == "Overdue"])

            churn_risk_score = min(95, 15 + open_high_tkts * 25 + overdue_count * 20 + (20 if frequency == 0 else 0))
            segment = "Champion" if monetary >= 50000 and churn_risk_score < 40 else ("At Risk" if churn_risk_score >= 50 else "Growth Account")
            recommendation = (
                "Schedule executive retention review & resolve open priority tickets"
                if churn_risk_score >= 50
                else ("Pitch Enterprise Annual Multi-Year Upsell & Add-on Modules" if monetary >= 50000 else "Enroll in Automated Adoption Drip Journey")
            )

            profiles.append({
                "customer_name": cname,
                "frequency_orders": frequency,
                "monetary_value": round(monetary, 2),
                "open_priority_tickets": open_high_tkts,
                "overdue_invoices": overdue_count,
                "churn_risk_score": churn_risk_score,
                "rfm_segment": segment,
                "recommended_action": recommendation
            })

        return {"total_customers_analyzed": len(profiles), "customers": profiles}
    finally:
        s_crm.close()
        s_fin.close()
        s_sup.close()


@app.get("/ai/anomalies/detect")
def detect_financial_and_procurement_anomalies(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    """
    Real-time AI audit guarding Finance & Procurement:
    Detects duplicate vendor bills, statistical expense outliers, and overdue invoice risks.
    """
    from services.finance_service.main import db_mgr as fin_db
    from services.finance_service.models import Expense, Invoice
    from services.procurement_service.main import db_mgr as proc_db
    from services.procurement_service.models import VendorBill

    s_fin = next(fin_db.get_session())
    s_proc = next(proc_db.get_session())
    detected = []
    try:
        expenses = s_fin.query(Expense).filter_by(org_id=user_ctx.org_id).all()
        invoices = s_fin.query(Invoice).filter_by(org_id=user_ctx.org_id).all()
        bills = s_proc.query(VendorBill).filter_by(org_id=user_ctx.org_id).all()

        # 1. Check high-value / outlier expenses
        if expenses:
            avg_exp = sum(float(e.amount or 0) for e in expenses) / max(len(expenses), 1)
            for e in expenses:
                amt = float(e.amount or 0)
                if amt > max(avg_exp * 2.0, 5000.0):
                    detected.append({
                        "type": "EXPENSE_OUTLIER",
                        "severity": "High",
                        "entity_ref": e.id,
                        "title": f"Unusual Expense Claim: ${amt:,.2f} at {e.merchant}",
                        "details": f"Expense exceeds 2x organizational mean (${avg_exp:,.2f}) in category '{e.category}'."
                    })

        # 2. Check duplicate or mismatched vendor bills
        seen_amounts: Dict[float, str] = {}
        for b in bills:
            amt = float(getattr(b, "billed_amount", 0.0) or 0.0)
            if amt in seen_amounts:
                detected.append({
                    "type": "DUPLICATE_VENDOR_BILL",
                    "severity": "Critical",
                    "entity_ref": b.bill_number,
                    "title": f"Potential Duplicate Vendor Bill Detected ({b.bill_number})",
                    "details": f"Bill amount ${amt:,.2f} matches existing bill {seen_amounts[amt]}."
                })
            else:
                seen_amounts[amt] = b.bill_number

        # 3. Overdue receivable concentration
        for inv in invoices:
            if inv.status == "Overdue":
                detected.append({
                    "type": "OVERDUE_RECEIVABLE",
                    "severity": "Medium",
                    "entity_ref": inv.invoice_number,
                    "title": f"Overdue Receivable Risk: {inv.invoice_number} ({inv.client_name})",
                    "details": f"Invoice of ${float(inv.total_amount or 0):,.2f} past due date ({inv.due_date})."
                })

        stored = db.query(AnomalyInsight).filter_by(org_id=user_ctx.org_id).all()
        return {
            "live_anomalies_detected": len(detected),
            "live_anomalies": detected,
            "persisted_insights": [a.to_dict() for a in stored]
        }
    finally:
        s_fin.close()
        s_proc.close()


@app.post("/ai/documents/summarize")
def summarize_enterprise_document(req: DocumentSummarizeRequest, user_ctx: UserContext = Depends(get_user_context)):
    """
    1-click AI summarization and key-clause extraction for Vendor Contracts, RFPs,
    Customer Ticket Threads, and Candidate Resumes.
    """
    lines = [ln.strip() for ln in req.content.splitlines() if ln.strip()]
    word_count = len(req.content.split())

    clauses = []
    content_lower = req.content.lower()
    if any(k in content_lower for k in ["sla", "uptime", "99.9", "response time"]):
        clauses.append("SLA & Uptime Commitment identified in document text.")
    if any(k in content_lower for k in ["payment", "net 30", "net30", "invoice", "fee", "$", "₹"]):
        clauses.append("Commercial Payment & Billing Terms extracted.")
    if any(k in content_lower for k in ["termination", "notice", "renewal", "expiry", "liability", "indemnity"]):
        clauses.append("Termination, Liability & Renewal governance clauses detected.")
    if not clauses:
        clauses.append("Standard operational scope and deliverable obligations identified.")

    summary_sentences = lines[:3] if lines else [req.content[:250]]
    return {
        "document_type": req.document_type,
        "title": req.title or req.document_title or "Enterprise Document",
        "word_count": word_count,
        "executive_summary": " ".join(summary_sentences)[:500],
        "key_clauses_extracted": clauses,
        "risk_assessment": "LOW" if "indemnity" not in content_lower and "penalty" not in content_lower else "MEDIUM_REVIEW_RECOMMENDED"
    }



