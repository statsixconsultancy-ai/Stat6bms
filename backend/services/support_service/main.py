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

from services.support_service.models import Ticket, TicketMessage, KnowledgeBaseArticle
from services.support_service.schemas import (
    TicketCreate, TicketStatusUpdate, TicketResponse, TicketDetailResponse,
    TicketMessageCreate, TicketMessageResponse,
    SLAAnalyticsResponse, TicketFeedbackRequest, Customer360ContextResponse,
    KBArticleCreate, KBArticleResponse
)
from services.support_service.seed import seed_support_data

config = get_service_config("support-service", default_port=8009, db_filename="support.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="BMS Omnichannel Support & Incident Desk Microservice",
    description="SLA Countdown Timers, Multi-Tier Ticket Escalations, Customer Threads & Resolution Tracking",
    version="2.0.0"
)

setup_microservice_middleware(app, "support-service", config.cors_origins)

@app.on_event("startup")
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_support_data(session)
    finally:
        session.close()

def get_db():
    yield from db_mgr.get_session()

# ----------------------------------------------------
# 1. Health & Webhooks
# ----------------------------------------------------
@app.get("/health")
def health():
    return {"service": "support-service", "status": "UP", "port": config.service_port}

@app.post("/webhooks/events")
async def handle_events(event: dict):
    return {"status": "received", "event_name": event.get("event_name")}

# ----------------------------------------------------
# 2. SLA Analytics (Defined before /support/tickets/{id})
# ----------------------------------------------------
@app.get("/support/analytics/sla", response_model=SLAAnalyticsResponse)
def get_sla_analytics(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    tickets = db.query(Ticket).filter_by(org_id=user_ctx.org_id).all()
    total = len(tickets)
    open_count = sum(1 for t in tickets if t.status in ["Open", "In Progress"])
    resolved_count = sum(1 for t in tickets if t.status in ["Resolved", "Closed"])
    breached_count = sum(1 for t in tickets if t.is_breached)
    compliance = ((total - breached_count) / total * 100.0) if total > 0 else 100.0

    return SLAAnalyticsResponse(
        total_tickets=total,
        open_tickets=open_count,
        resolved_tickets=resolved_count,
        sla_compliance_rate_percent=round(compliance, 1),
        average_resolution_hours=2.4
    )

# ----------------------------------------------------
# 3. Tickets Endpoints
# ----------------------------------------------------
def _ticket_resp(t: Ticket) -> TicketResponse:
    d = t.to_dict()
    d["sla_status"] = "BREACHED" if t.is_breached else "ON_TRACK"
    return TicketResponse(**d)

@app.get("/support/tickets", response_model=List[TicketResponse])
def list_tickets(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    query = db.query(Ticket).filter_by(org_id=user_ctx.org_id)
    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    tickets = query.order_by(Ticket.created_at.desc()).all()
    return [_ticket_resp(t) for t in tickets]

@app.post("/support/tickets", response_model=TicketResponse)
async def create_ticket(
    req: TicketCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    tkt_num = f"TKT-2026-{uuid.uuid4().hex[:6].upper()}"

    sla_target = 2.0 if req.priority == "Urgent" else (4.0 if req.priority == "High" else 8.0)

    ticket = Ticket(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        ticket_number=tkt_num,
        customer_name=req.customer_name,
        customer_email=req.customer_email,
        subject=req.subject,
        description=req.description,
        priority=req.priority or "Medium",
        status="Open",
        assigned_to=req.assigned_to or "Support Lead",
        sla_target_hours=sla_target,
        elapsed_hours=0.0,
        is_breached=False
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    if ticket.priority == "Urgent":
        await event_bus.publish("ticket.urgent", {
            "ticket_id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "subject": ticket.subject,
            "customer": ticket.customer_name
        }, org_id=user_ctx.org_id)

    return _ticket_resp(ticket)

@app.get("/support/tickets/{id}", response_model=TicketDetailResponse)
def get_ticket_detail(id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    t = db.query(Ticket).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Ticket not found")

    messages = [
        TicketMessageResponse(
            id=m.id,
            ticket_id=m.ticket_id,
            sender_name=m.sender_name,
            sender_type=m.sender_type,
            message=m.message,
            created_at=m.created_at.isoformat() if m.created_at else "2026-09-24"
        )
        for m in t.messages
    ]

    t_dict = t.to_dict()
    t_dict["messages"] = messages
    return TicketDetailResponse(**t_dict)

@app.post("/support/tickets/{id}/messages", response_model=TicketMessageResponse)
def add_ticket_message(
    id: str,
    req: TicketMessageCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    msg = TicketMessage(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        ticket_id=ticket.id,
        sender_name=req.sender_name,
        sender_type=req.sender_type or "Agent",
        message=req.message
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return TicketMessageResponse(
        id=msg.id,
        ticket_id=msg.ticket_id,
        sender_name=msg.sender_name,
        sender_type=msg.sender_type,
        message=msg.message,
        created_at=msg.created_at.isoformat() if msg.created_at else "2026-09-24"
    )

@app.patch("/support/tickets/{id}/status", response_model=TicketResponse)
def update_ticket_status(
    id: str,
    req: TicketStatusUpdate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.status = req.status
    db.commit()
    db.refresh(ticket)
    return _ticket_resp(ticket)

@app.post("/support/tickets/{id}/escalate", response_model=TicketResponse)
async def escalate_ticket(id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    """Escalates ticket priority to 'Urgent' and broadcasts 'ticket.urgent' event."""
    ticket = db.query(Ticket).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.priority = "Urgent"
    ticket.sla_target_hours = 1.0  # 1-hour critical response SLA
    ticket.assigned_to = "Executive Escalation Response Team"
    db.commit()
    db.refresh(ticket)

    await event_bus.publish("ticket.urgent", {
        "ticket_id": ticket.id,
        "ticket_number": ticket.ticket_number,
        "subject": ticket.subject,
        "customer": ticket.customer_name
    }, org_id=user_ctx.org_id)

    return _ticket_resp(ticket)

# ----------------------------------------------------
# 4. CSAT / NPS Ticket Feedback Ratings
# ----------------------------------------------------
@app.post("/support/tickets/{id}/feedback", response_model=TicketResponse)
def submit_ticket_feedback(
    id: str,
    req: TicketFeedbackRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    ticket.csat_score = max(1, min(5, req.csat_score))
    if req.nps_score is not None:
        ticket.nps_score = max(0, min(10, req.nps_score))
    if req.feedback_comment:
        ticket.feedback_comment = req.feedback_comment
    
    db.commit()
    db.refresh(ticket)
    return _ticket_resp(ticket)

# ----------------------------------------------------
# 5. Customer 360 Context & Incident Timeline
# ----------------------------------------------------
@app.get("/support/tickets/{id}/context", response_model=Customer360ContextResponse)
def get_customer_360_context(
    id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Query all tickets belonging to this customer email
    cust_tickets = db.query(Ticket).filter_by(
        org_id=user_ctx.org_id,
        customer_email=ticket.customer_email
    ).order_by(Ticket.created_at.desc()).all()

    total = len(cust_tickets)
    open_cnt = sum(1 for t in cust_tickets if t.status in ["Open", "In Progress"])
    resolved_cnt = sum(1 for t in cust_tickets if t.status in ["Resolved", "Closed"])
    
    csat_scores = [t.csat_score for t in cust_tickets if t.csat_score is not None]
    avg_csat = round(sum(csat_scores) / len(csat_scores), 1) if csat_scores else 5.0

    return Customer360ContextResponse(
        customer_email=ticket.customer_email,
        customer_name=ticket.customer_name,
        total_tickets=total,
        open_tickets=open_cnt,
        resolved_tickets=resolved_cnt,
        average_csat=avg_csat,
        recent_tickets=[_ticket_resp(t) for t in cust_tickets[:5]],
        associated_crm_context={
            "customer_tier": "Enterprise Tier 1",
            "sla_tier": ticket.sla_policy,
            "account_health": "Healthy",
            "active_deal_count": 2,
            "total_contract_value": 150000.00
        },
        crm_context={
            "company": ticket.customer_name,
            "tier": "Enterprise Tier 1",
            "active_deals_value": 150000.00,
            "total_deal_value": 150000.00
        },
        finance_context={
            "total_invoiced": 285000.00,
            "total_paid": 285000.00,
            "outstanding_balance": 0.00,
            "overdue_balance": 0.00
        }
    )

# ----------------------------------------------------
# 6. Knowledge Base & FAQ Center
# ----------------------------------------------------
@app.get("/support/kb/articles", response_model=List[KBArticleResponse])
def list_kb_articles(
    category: Optional[str] = None,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    query = db.query(KnowledgeBaseArticle).filter_by(org_id=user_ctx.org_id, is_published=True)
    if category:
        query = query.filter_by(category=category)
    articles = query.order_by(KnowledgeBaseArticle.helpful_votes.desc()).all()
    return [KBArticleResponse(**a.to_dict()) for a in articles]

@app.post("/support/kb/articles", response_model=KBArticleResponse)
def create_kb_article(
    req: KBArticleCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    article = KnowledgeBaseArticle(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        title=req.title,
        category=req.category or "General",
        content=req.content,
        is_published=req.is_published if req.is_published is not None else True,
        view_count=0,
        helpful_votes=0
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return KBArticleResponse(**article.to_dict())

@app.get("/support/kb/articles/{id}", response_model=KBArticleResponse)
def get_kb_article(
    id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    article = db.query(KnowledgeBaseArticle).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Knowledge base article not found")
    article.view_count += 1
    db.commit()
    return KBArticleResponse(**article.to_dict())

@app.post("/support/kb/articles/{id}/vote", response_model=KBArticleResponse)
def vote_kb_article(
    id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    article = db.query(KnowledgeBaseArticle).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Knowledge base article not found")
    article.helpful_votes += 1
    db.commit()
    return KBArticleResponse(**article.to_dict())

