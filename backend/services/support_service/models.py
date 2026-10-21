import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class Ticket(TenantModel):
    __tablename__ = "sup_tickets"

    ticket_number = Column(String(50), nullable=False, unique=True, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(50), default="Medium", index=True)  # Low, Medium, High, Urgent
    status = Column(String(50), default="Open", index=True)  # Open, In Progress, Resolved, Closed
    assigned_to = Column(String(255), default="Support Lead")
    sla_target_hours = Column(Float, default=4.0)
    elapsed_hours = Column(Float, default=0.0)
    is_breached = Column(Boolean, default=False)
    sla_policy = Column(String(100), default="Standard B2B SLA")
    resolution_due_at = Column(String(50), nullable=True)
    csat_score = Column(Integer, nullable=True)  # 1 to 5 stars
    nps_score = Column(Integer, nullable=True)   # 0 to 10
    feedback_comment = Column(Text, nullable=True)
    tags = Column(String(255), default="[]")

    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan")

class TicketMessage(TenantModel):
    __tablename__ = "sup_ticket_messages"

    ticket_id = Column(String(36), ForeignKey("sup_tickets.id"), nullable=False, index=True)
    sender_name = Column(String(255), nullable=False)
    sender_type = Column(String(50), default="Agent")  # Agent, Customer, System
    message = Column(Text, nullable=False)

    ticket = relationship("Ticket", back_populates="messages")

class KnowledgeBaseArticle(TenantModel):
    __tablename__ = "sup_kb_articles"

    title = Column(String(255), nullable=False, index=True)
    category = Column(String(100), default="General", index=True)  # Billing, Technical, How-To, Security
    content = Column(Text, nullable=False)
    is_published = Column(Boolean, default=True)
    view_count = Column(Integer, default=0)
    helpful_votes = Column(Integer, default=0)

