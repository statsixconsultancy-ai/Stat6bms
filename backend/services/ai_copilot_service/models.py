import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean
from common.models import Base, TenantModel

class AnomalyInsight(TenantModel):
    __tablename__ = "ai_anomalies"

    category = Column(String(100), nullable=False, index=True)  # Supply Chain, Support, Financial, Commercial
    severity = Column(String(50), default="Warning", index=True)  # Info, Warning, Critical
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)

class CopilotQueryLog(TenantModel):
    __tablename__ = "ai_query_logs"

    user_id = Column(String(255), default="usr-dev-001")
    query_text = Column(Text, nullable=False)
    intent = Column(String(100), default="EXECUTIVE_SUMMARY")
    response_text = Column(Text, nullable=False)
    tool_calls_made = Column(Text, nullable=True)
