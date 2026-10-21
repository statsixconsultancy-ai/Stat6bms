import os
import sys
import uuid
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status, Query
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

from services.collaboration_service.models import (
    ChatChannel,
    ChatMessage,
    Announcement,
    CalendarEvent,
    RecordNote,
    ActivityStreamItem
)
from services.collaboration_service.schemas import (
    ChatChannelCreate, ChatChannelResponse,
    ChatMessageCreate, ChatMessageResponse,
    AnnouncementCreate, AnnouncementResponse,
    CalendarEventCreate, CalendarEventResponse,
    RecordNoteCreate, RecordNoteResponse,
    ActivityStreamItemResponse
)
from services.collaboration_service.seed import seed_collaboration_data

config = get_service_config("collaboration-service", default_port=8010, db_filename="collaboration.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="STAT6 Collaboration & Communication Microservice",
    description="Team Chat, Contextual Record Cards, Announcements, Shared Calendar, Notes & Activity Stream",
    version="2.4.0"
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
    return {
        "service": "collaboration-service",
        "status": "UP",
        "port": config.service_port,
        "features": ["record_cards", "announcements", "calendar", "polymorphic_notes", "activity_stream"]
    }

@app.post("/webhooks/events")
async def handle_events(event: dict, db: Session = Depends(get_db)):
    """Subscribes to domain events, emits activity stream records and posts alerts."""
    event_name = event.get("event_name", "UNKNOWN")
    payload = event.get("payload", {})
    org_id = event.get("org_id", "org-acroflow-main")

    # Record in universal activity stream
    activity = ActivityStreamItem(
        id=str(uuid.uuid4()),
        org_id=org_id,
        entity_type=event_name.split(".")[0].upper() if "." in event_name else "SYSTEM",
        entity_id=str(payload.get("id") or payload.get("deal_id") or payload.get("ticket_id") or "sys"),
        action=event_name.upper(),
        actor_name="STAT6 Event Mesh",
        summary=f"Event {event_name}: {payload.get('title') or payload.get('name') or payload.get('subject') or 'Updated'}"
    )
    db.add(activity)

    if event_name == "ticket.urgent":
        ch = db.query(ChatChannel).filter_by(name="incident-response", org_id=org_id).first()
        if ch:
            msg = ChatMessage(
                id=str(uuid.uuid4()),
                org_id=org_id,
                channel_id=ch.id,
                user_id="sys-event-broker",
                user_name="STAT6 Incident Bot",
                message=f"CRITICAL ESCALATION: Ticket {payload.get('ticket_number')} ('{payload.get('subject')}') from {payload.get('customer')}. Response SLA: 1.0 hr.",
                message_type="event_alert",
                card_type="ticket",
                card_data=payload
            )
            db.add(msg)

    elif event_name == "deal.won":
        ch = db.query(ChatChannel).filter_by(name="deals", org_id=org_id).first()
        if ch:
            msg = ChatMessage(
                id=str(uuid.uuid4()),
                org_id=org_id,
                channel_id=ch.id,
                user_id="sys-event-broker",
                user_name="STAT6 Sales Bot",
                message=f"CLOSED-WON CONTRACT: {payload.get('title')} for ${payload.get('amount', 0):,.2f} with {payload.get('company_name')}!",
                message_type="event_alert",
                card_type="deal",
                card_data=payload
            )
            db.add(msg)

    db.commit()
    return {"status": "event_processed", "event_name": event_name}

# ----------------------------------------------------
# 2. Channels & Messaging with Contextual Record Cards
# ----------------------------------------------------
@app.get("/chat/channels", response_model=List[ChatChannelResponse])
def list_channels(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    channels = db.query(ChatChannel).filter_by(org_id=user_ctx.org_id).all()
    return [
        ChatChannelResponse(
            id=c.id,
            org_id=c.org_id,
            name=c.name,
            description=c.description,
            is_private=c.is_private or False,
            channel_type=c.channel_type or "public",
            unread_count=0
        )
        for c in channels
    ]

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
        is_private=req.is_private or False,
        channel_type=req.channel_type or "public"
    )
    db.add(ch)
    db.commit()
    db.refresh(ch)
    return ChatChannelResponse(
        id=ch.id,
        org_id=ch.org_id,
        name=ch.name,
        description=ch.description,
        is_private=ch.is_private,
        channel_type=ch.channel_type,
        unread_count=0
    )

@app.get("/chat/channels/{channel_id}/messages", response_model=List[ChatMessageResponse])
def get_channel_messages(channel_id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    ch = db.query(ChatChannel).filter_by(id=channel_id, org_id=user_ctx.org_id).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")

    messages = db.query(ChatMessage).filter_by(channel_id=channel_id, org_id=user_ctx.org_id).order_by(ChatMessage.created_at.asc()).all()
    return [
        ChatMessageResponse(
            id=m.id,
            org_id=m.org_id,
            channel_id=m.channel_id,
            user_id=m.user_id,
            user_name=m.user_name,
            message=m.message,
            message_type=m.message_type,
            card_type=m.card_type or "none",
            card_data=m.card_data or {},
            created_at=m.created_at.isoformat() if m.created_at else "2026-10-16T12:00:00"
        )
        for m in messages
    ]

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
        message_type=req.message_type or "text",
        card_type=req.card_type or "none",
        card_data=req.card_data or {}
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
        card_type=msg.card_type,
        card_data=msg.card_data,
        created_at=msg.created_at.isoformat() if msg.created_at else "2026-10-16T12:00:00"
    )

# ----------------------------------------------------
# 3. Announcements & Town Halls (Zoho Connect Alt)
# ----------------------------------------------------
@app.get("/chat/announcements", response_model=List[AnnouncementResponse])
def list_announcements(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    items = db.query(Announcement).filter_by(org_id=user_ctx.org_id).order_by(Announcement.created_at.desc()).all()
    return [
        AnnouncementResponse(
            id=a.id,
            org_id=a.org_id,
            title=a.title,
            body=a.body,
            priority=a.priority or "normal",
            author_name=a.author_name,
            acknowledgments=a.acknowledgments or [],
            expires_at=a.expires_at.isoformat() if a.expires_at else None,
            created_at=a.created_at.isoformat() if a.created_at else "2026-10-16"
        )
        for a in items
    ]

@app.post("/chat/announcements", response_model=AnnouncementResponse)
def create_announcement(req: AnnouncementCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    sender = user_ctx.email.split("@")[0].replace(".", " ").title() if user_ctx.email else "Admin"
    item = Announcement(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        title=req.title,
        body=req.body,
        priority=req.priority,
        author_name=sender,
        acknowledgments=[],
        expires_at=req.expires_at
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return AnnouncementResponse(
        id=item.id,
        org_id=item.org_id,
        title=item.title,
        body=item.body,
        priority=item.priority,
        author_name=item.author_name,
        acknowledgments=[],
        expires_at=item.expires_at.isoformat() if item.expires_at else None,
        created_at=item.created_at.isoformat() if item.created_at else "2026-10-16"
    )

@app.post("/chat/announcements/{announcement_id}/acknowledge")
def acknowledge_announcement(announcement_id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    item = db.query(Announcement).filter_by(id=announcement_id, org_id=user_ctx.org_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Announcement not found")
    acks = list(item.acknowledgments or [])
    if user_ctx.user_id not in acks:
        acks.append(user_ctx.user_id)
        item.acknowledgments = acks
        db.commit()
    return {"status": "acknowledged", "announcement_id": announcement_id, "total_acks": len(acks)}

# ----------------------------------------------------
# 4. Shared Calendar Engine (Zoho Calendar Alt)
# ----------------------------------------------------
@app.get("/chat/calendar/events", response_model=List[CalendarEventResponse])
def list_calendar_events(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    events = db.query(CalendarEvent).filter_by(org_id=user_ctx.org_id).order_by(CalendarEvent.start_time.asc()).all()
    return [
        CalendarEventResponse(
            id=e.id,
            org_id=e.org_id,
            title=e.title,
            description=e.description,
            start_time=e.start_time.isoformat(),
            end_time=e.end_time.isoformat(),
            event_type=e.event_type or "meeting",
            attendees=e.attendees or [],
            location_or_link=e.location_or_link
        )
        for e in events
    ]

@app.post("/chat/calendar/events", response_model=CalendarEventResponse)
def create_calendar_event(req: CalendarEventCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    evt = CalendarEvent(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        title=req.title,
        description=req.description,
        start_time=req.start_time,
        end_time=req.end_time,
        event_type=req.event_type,
        attendees=req.attendees or [],
        location_or_link=req.location_or_link
    )
    db.add(evt)
    db.commit()
    db.refresh(evt)
    return CalendarEventResponse(
        id=evt.id,
        org_id=evt.org_id,
        title=evt.title,
        description=evt.description,
        start_time=evt.start_time.isoformat(),
        end_time=evt.end_time.isoformat(),
        event_type=evt.event_type,
        attendees=evt.attendees or [],
        location_or_link=evt.location_or_link
    )

@app.delete("/chat/calendar/events/{event_id}")
def delete_calendar_event(event_id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    evt = db.query(CalendarEvent).filter_by(id=event_id, org_id=user_ctx.org_id).first()
    if not evt:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    db.delete(evt)
    db.commit()
    return {"status": "deleted", "event_id": event_id}

# ----------------------------------------------------
# 5. Polymorphic Record Notes & Mentions (#record, @user)
# ----------------------------------------------------
@app.get("/chat/notes", response_model=List[RecordNoteResponse])
def get_record_notes(
    entity_type: str = Query(...),
    entity_id: str = Query(...),
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    notes = db.query(RecordNote).filter_by(
        org_id=user_ctx.org_id,
        entity_type=entity_type,
        entity_id=entity_id
    ).order_by(RecordNote.created_at.asc()).all()
    return [
        RecordNoteResponse(
            id=n.id,
            org_id=n.org_id,
            entity_type=n.entity_type,
            entity_id=n.entity_id,
            author_id=n.author_id,
            author_name=n.author_name,
            content=n.content,
            mentions=n.mentions or [],
            attachments=n.attachments or [],
            created_at=n.created_at.isoformat() if n.created_at else "2026-10-16"
        )
        for n in notes
    ]

@app.post("/chat/notes", response_model=RecordNoteResponse)
def add_record_note(req: RecordNoteCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    sender = user_ctx.email.split("@")[0].replace(".", " ").title() if user_ctx.email else "Team Member"
    note = RecordNote(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        entity_type=req.entity_type,
        entity_id=req.entity_id,
        author_id=user_ctx.user_id,
        author_name=sender,
        content=req.content,
        mentions=req.mentions or [],
        attachments=req.attachments or []
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return RecordNoteResponse(
        id=note.id,
        org_id=note.org_id,
        entity_type=note.entity_type,
        entity_id=note.entity_id,
        author_id=note.author_id,
        author_name=note.author_name,
        content=note.content,
        mentions=note.mentions or [],
        attachments=note.attachments or [],
        created_at=note.created_at.isoformat() if note.created_at else "2026-10-16"
    )

# ----------------------------------------------------
# 6. Universal Activity Stream
# ----------------------------------------------------
@app.get("/chat/activity-stream", response_model=List[ActivityStreamItemResponse])
def get_activity_stream(
    limit: int = 50,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    items = db.query(ActivityStreamItem).filter_by(org_id=user_ctx.org_id).order_by(ActivityStreamItem.created_at.desc()).limit(limit).all()
    return [
        ActivityStreamItemResponse(
            id=a.id,
            org_id=a.org_id,
            entity_type=a.entity_type,
            entity_id=a.entity_id,
            action=a.action,
            actor_name=a.actor_name,
            summary=a.summary,
            created_at=a.created_at.isoformat() if a.created_at else "2026-10-16"
        )
        for a in items
    ]
