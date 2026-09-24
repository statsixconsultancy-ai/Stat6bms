import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class AutomationRule(TenantModel):
    __tablename__ = "auto_rules"

    name = Column(String(255), nullable=False, index=True)
    trigger_event = Column(String(100), nullable=False, index=True)  # deal.won, stock.low, ticket.urgent, etc.
    condition_code = Column(String(255), default="True")  # e.g., "amount >= 100000"
    action_type = Column(String(100), nullable=False)     # DISPATCH_NOTIFICATION, LOG_COMPLIANCE, EXECUTE_WEBHOOK
    action_config = Column(Text, nullable=True)           # JSON configuration for payload
    is_active = Column(Boolean, default=True, index=True)
    execution_count = Column(Integer, default=0)

    logs = relationship("AutomationLog", back_populates="rule", cascade="all, delete-orphan")

class AutomationLog(TenantModel):
    __tablename__ = "auto_logs"

    rule_id = Column(String(36), ForeignKey("auto_rules.id"), nullable=False, index=True)
    trigger_event = Column(String(100), nullable=False)
    status = Column(String(50), default="Success")  # Success, Skipped, Error
    details = Column(Text, nullable=True)

    rule = relationship("AutomationRule", back_populates="logs")
