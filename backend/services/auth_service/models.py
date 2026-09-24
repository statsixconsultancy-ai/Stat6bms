from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text
from common.models import Base, TenantModel, generate_uuid

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    industry = Column(String(100), default="Technology")
    currency = Column(String(10), default="USD")
    timezone = Column(String(50), default="UTC")
    plan = Column(String(50), default="Enterprise")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug,
            "industry": self.industry,
            "currency": self.currency,
            "timezone": self.timezone,
            "plan": self.plan,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class User(TenantModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="admin") # admin, manager, member, auditor
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)

    def to_dict(self):
        d = super().to_dict()
        d.pop("password_hash", None)
        return d

class Role(TenantModel):
    __tablename__ = "roles"

    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    permissions = Column(JSON, default=list) # e.g. ["crm:*", "projects:read"]

class AuthAuditLog(TenantModel):
    __tablename__ = "auth_audit_logs"

    actor_id = Column(String(36), nullable=True)
    actor_name = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False) # LOGIN, LOGOUT, REGISTER, ROLE_CHANGE
    ip_address = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
