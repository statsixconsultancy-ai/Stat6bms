from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class ChatChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: Optional[bool] = False
    channel_type: Optional[str] = "public"

class ChatChannelResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str] = None
    is_private: bool
    channel_type: str = "public"
    unread_count: int = 0

class ChatMessageCreate(BaseModel):
    message: str
    message_type: Optional[str] = "text"
    card_type: Optional[str] = "none"
    card_data: Optional[Dict[str, Any]] = None

class ChatMessageResponse(BaseModel):
    id: str
    org_id: str
    channel_id: str
    user_id: str
    user_name: str
    message: str
    message_type: str
    card_type: str = "none"
    card_data: Optional[Dict[str, Any]] = None
    created_at: str

class AnnouncementCreate(BaseModel):
    title: str
    body: str
    priority: str = "normal" # normal, urgent, critical
    expires_at: Optional[datetime] = None

class AnnouncementResponse(BaseModel):
    id: str
    org_id: str
    title: str
    body: str
    priority: str
    author_name: str
    acknowledgments: List[str] = []
    expires_at: Optional[str] = None
    created_at: str

class CalendarEventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    event_type: str = "meeting" # meeting, milestone, leave, follow_up
    attendees: Optional[List[str]] = []
    location_or_link: Optional[str] = None

class CalendarEventResponse(BaseModel):
    id: str
    org_id: str
    title: str
    description: Optional[str] = None
    start_time: str
    end_time: str
    event_type: str
    attendees: List[str] = []
    location_or_link: Optional[str] = None

class RecordNoteCreate(BaseModel):
    entity_type: str
    entity_id: str
    content: str
    mentions: Optional[List[str]] = []
    attachments: Optional[List[str]] = []

class RecordNoteResponse(BaseModel):
    id: str
    org_id: str
    entity_type: str
    entity_id: str
    author_id: str
    author_name: str
    content: str
    mentions: List[str] = []
    attachments: List[str] = []
    created_at: str

class ActivityStreamItemResponse(BaseModel):
    id: str
    org_id: str
    entity_type: str
    entity_id: str
    action: str
    actor_name: str
    summary: str
    created_at: str
