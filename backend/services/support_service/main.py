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

from services.support_service.models import Ticket, TicketMessage
from services.support_service.schemas import (
    TicketCreate, TicketStatusUpdate, TicketResponse, TicketDetailResponse,
    TicketMessageCreate, TicketMessageResponse,
    SLAAnalyticsResponse
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
    return [TicketResponse(**t.to_dict()) for t in tickets]

@app.post("/support/tickets", response_model=TicketResponse)
async def create_ticket(
    req: TicketCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    seq = db.query(Ticket).filter_by(org_id=user_ctx.org_id).count() + 1
    tkt_num = f"TKT-2026-{seq:03d}"

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

    return TicketResponse(**ticket.to_dict())

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
    return TicketResponse(**ticket.to_dict())

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

    return TicketResponse(**ticket.to_dict())
