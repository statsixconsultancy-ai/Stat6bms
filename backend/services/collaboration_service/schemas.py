from typing import Optional, List
from pydantic import BaseModel

class ChatChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_private: Optional[bool] = False

class ChatChannelResponse(BaseModel):
    id: str
    org_id: str
    name: str
    description: Optional[str] = None
    is_private: bool
    unread_count: int = 0

class ChatMessageCreate(BaseModel):
    message: str
    message_type: Optional[str] = "text"

class ChatMessageResponse(BaseModel):
    id: str
    org_id: str
    channel_id: str
    user_id: str
    user_name: str
    message: str
    message_type: str
    created_at: str
