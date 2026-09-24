import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class ChatChannel(TenantModel):
    __tablename__ = "collab_channels"

    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(String(255), nullable=True)
    is_private = Column(Boolean, default=False)

    messages = relationship("ChatMessage", back_populates="channel", cascade="all, delete-orphan")

class ChatMessage(TenantModel):
    __tablename__ = "collab_messages"

    channel_id = Column(String(36), ForeignKey("collab_channels.id"), nullable=False, index=True)
    user_id = Column(String(255), default="usr-dev-001")
    user_name = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    message_type = Column(String(50), default="text")  # text, event_alert

    channel = relationship("ChatChannel", back_populates="messages")
