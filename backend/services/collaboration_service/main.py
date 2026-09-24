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

from services.collaboration_service.models import ChatChannel, ChatMessage
from services.collaboration_service.schemas import (
    ChatChannelCreate, ChatChannelResponse,
    ChatMessageCreate, ChatMessageResponse
)
from services.collaboration_service.seed import seed_collaboration_data

config = get_service_config("collaboration-service", default_port=8010, db_filename="collaboration.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="BMS Real-Time Collaboration & Chat Microservice",
    description="Topic-Based Channels, Incident Swarming, Event Alerts & Multi-User Discussions",
    version="2.0.0"
)

setup_microservice_middleware(app, "collaboration-service", config.cors_origins)

@app.on_event("startup")
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_collaboration_data(session)
    finally:
        session.close()

def get_db():
    yield from db_mgr.get_session()

# ----------------------------------------------------
# 1. Health & Event Broker Webhook Endpoints
# ----------------------------------------------------
@app.get("/health")
def health():
    return {"service": "collaboration-service", "status": "UP", "port": config.service_port}

@app.post("/webhooks/events")
async def handle_events(event: dict, db: Session = Depends(get_db)):
    """
    Subscribes to domain events and automatically broadcasts alerts into team channels:
    - 'ticket.urgent' -> posts to '#incident-response'
    - 'deal.won' -> posts to '#deals'
    """
    event_name = event.get("event_name")
    payload = event.get("payload", {})
    org_id = event.get("org_id", "org-acroflow-main")

    if event_name == "ticket.urgent":
        ch = db.query(ChatChannel).filter_by(name="incident-response", org_id=org_id).first()
        if ch:
            msg = ChatMessage(
                id=str(uuid.uuid4()),
                org_id=org_id,
                channel_id=ch.id,
                user_id="sys-event-broker",
                user_name="BMS Incident Bot",
                message=f"CRITICAL ESCALATION: Ticket {payload.get('ticket_number')} ('{payload.get('subject')}') from {payload.get('customer')}. Response SLA: 1.0 hr.",
                message_type="event_alert"
            )
            db.add(msg)
            db.commit()
            return {"status": "alert_posted", "channel": "incident-response"}

    elif event_name == "deal.won":
        ch = db.query(ChatChannel).filter_by(name="deals", org_id=org_id).first()
        if ch:
            msg = ChatMessage(
                id=str(uuid.uuid4()),
                org_id=org_id,
                channel_id=ch.id,
                user_id="sys-event-broker",
                user_name="BMS Sales Bot",
                message=f"NEW CLOSED-WON CONTRACT: {payload.get('title')} for ${payload.get('amount', 0):,.2f} with {payload.get('company_name')}!",
                message_type="event_alert"
            )
            db.add(msg)
            db.commit()
            return {"status": "alert_posted", "channel": "deals"}

    return {"status": "ignored", "event_name": event_name}

# ----------------------------------------------------
# 2. Channels Endpoints
# ----------------------------------------------------
@app.get("/chat/channels", response_model=List[ChatChannelResponse])
def list_channels(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    channels = db.query(ChatChannel).filter_by(org_id=user_ctx.org_id).all()
    return [ChatChannelResponse(**c.to_dict()) for c in channels]

@app.post("/chat/channels", response_model=ChatChannelResponse)
def create_channel(req: ChatChannelCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    existing = db.query(ChatChannel).filter_by(name=req.name, org_id=user_ctx.org_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Channel '#{req.name}' already exists")

    ch = ChatChannel(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        name=req.name,
        description=req.description,
        is_private=req.is_private or False
    )
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return ChatChannelResponse(**ch.to_dict())

# ----------------------------------------------------
# 3. Channel Messages Endpoints
# ----------------------------------------------------
@app.get("/chat/channels/{channel_id}/messages", response_model=List[ChatMessageResponse])
def get_channel_messages(channel_id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    ch = db.query(ChatChannel).filter_by(id=channel_id, org_id=user_ctx.org_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")

    messages = db.query(ChatMessage).filter_by(channel_id=channel_id, org_id=user_ctx.org_id).order_by(ChatMessage.created_at.asc()).all()
    results = []
    for m in messages:
        results.append(ChatMessageResponse(
            id=m.id,
            org_id=m.org_id,
            channel_id=m.channel_id,
            user_id=m.user_id,
            user_name=m.user_name,
            message=m.message,
            message_type=m.message_type,
            created_at=m.created_at.isoformat() if m.created_at else "2026-09-24"
        ))
    return results

@app.post("/chat/channels/{channel_id}/messages", response_model=ChatMessageResponse)
def post_channel_message(
    channel_id: str,
    req: ChatMessageCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    ch = db.query(ChatChannel).filter_by(id=channel_id, org_id=user_ctx.org_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")

    sender = user_ctx.email.split("@")[0].replace(".", " ").title() if user_ctx.email else "Team Member"

    msg = ChatMessage(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        channel_id=ch.id,
        user_id=user_ctx.user_id,
        user_name=sender,
        message=req.message,
        message_type=req.message_type or "text"
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return ChatMessageResponse(
        id=msg.id,
        org_id=msg.org_id,
        channel_id=msg.channel_id,
        user_id=msg.user_id,
        user_name=msg.user_name,
        message=msg.message,
        message_type=msg.message_type,
        created_at=msg.created_at.isoformat() if msg.created_at else "2026-09-24"
    )
