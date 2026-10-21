import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class ChatChannel(TenantModel):
    __tablename__ = "collab_channels"

    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    is_private = Column(Boolean, default=False)
    channel_type = Column(String(50), default="public") # public, private, direct, project

    messages = relationship("ChatMessage", back_populates="channel", cascade="all, delete-orphan")

class ChatMessage(TenantModel):
    __tablename__ = "collab_messages"

    channel_id = Column(String(36), ForeignKey("collab_channels.id"), nullable=False, index=True)
    user_id = Column(String(255), default="usr-dev-001")
    user_name = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, event_alert, system
    
    # Contextual Record Card Support (renders Deals, Invoices, Tasks inside chat)
    card_type = Column(String(50), default="none") # none, deal, invoice, task, lead, ticket
    card_data = Column(JSON, default=dict) # e.g. {"id": "DEAL-1", "title": "Apex Sensors", "amount": 125000}

    channel = relationship("ChatChannel", back_populates="messages")

class Announcement(TenantModel):
    __tablename__ = "collab_announcements"

    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    priority = Column(String(50), default="normal") # normal, urgent, critical
    author_name = Column(String(255), nullable=False)
    acknowledgments = Column(JSON, default=list) # List of user IDs who acknowledged
    expires_at = Column(DateTime, nullable=True)

class CalendarEvent(TenantModel):
    __tablename__ = "collab_calendar_events"

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    event_type = Column(String(50), default="meeting") # meeting, milestone, leave, follow_up
    attendees = Column(JSON, default=list) # List of attendee email addresses
    location_or_link = Column(String(500), nullable=True) # Zoom, Google Meet or room

class RecordNote(TenantModel):
    """
    Polymorphic Note & Mention Engine
    Attach notes with @mentions to any record (Deals, Invoices, Tasks, Tickets)
    """
    __tablename__ = "collab_record_notes"

    entity_type = Column(String(50), nullable=False, index=True) # Deal, Invoice, Task, Ticket, Employee
    entity_id = Column(String(100), nullable=False, index=True)
    author_id = Column(String(255), nullable=False)
    author_name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    mentions = Column(JSON, default=list) # list of mentioned usernames / user_ids
    attachments = Column(JSON, default=list)

class ActivityStreamItem(TenantModel):
    """
    Personalized universal activity stream across all 14 modules
    """
    __tablename__ = "collab_activity_stream"

    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(String(100), nullable=False, index=True)
    action = Column(String(100), nullable=False) # CREATED, UPDATED, WON, PAID, ASSIGNED, ESCALATED
    actor_name = Column(String(255), nullable=False)
    summary = Column(String(500), nullable=False)
