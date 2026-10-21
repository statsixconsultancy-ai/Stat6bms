import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean
from common.models import Base, TenantModel

class AuditLog(TenantModel):
    __tablename__ = "comp_audit_logs"

    actor_id = Column(String(255), nullable=False, index=True)
    actor_email = Column(String(255), nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)  # LOGIN, USER_CREATED, INVOICE_PAID, ROLE_MODIFIED
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    client_ip = Column(String(100), default="127.0.0.1")
    metadata_json = Column(Text, nullable=True)

class DataSubjectRequest(TenantModel):
    __tablename__ = "comp_dsr_requests"

    requester_email = Column(String(255), nullable=False, index=True)
    request_type = Column(String(50), default="EXPORT")  # EXPORT, ERASURE
    status = Column(String(50), default="Completed")  # Completed, Processing
    completed_at = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)

class ComplianceControl(TenantModel):
    __tablename__ = "comp_controls"

    framework = Column(String(50), default="SOC2 Type II", index=True)  # SOC2 Type II, GDPR, ISO 27001
    control_code = Column(String(50), nullable=False, unique=True, index=True)  # CC6.1, CC6.2, etc.
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="Passed")  # Passed, In Review, Failed
    last_tested = Column(String(50), default="2026-09-20")


class VaultSecret(TenantModel):
    """
    STAT6 Enterprise Password & Secrets Vault (Replaces Zoho Vault)
    Stores credentials encrypted at rest with PBKDF2-HMAC-SHA256 authenticated cipher
    and logs every reveal/rotation to the immutable AuditLog.
    """
    __tablename__ = "comp_vault_secrets"

    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), default="API_KEY", index=True)  # API_KEY, DATABASE_CREDENTIAL, OAUTH_SECRET, CLOUD_INFRA, CORPORATE_LOGIN
    username = Column(String(255), nullable=True)
    service_url = Column(String(500), nullable=True)
    encrypted_payload = Column(Text, nullable=False)
    masked_preview = Column(String(100), nullable=False)
    environment = Column(String(50), default="PRODUCTION")  # PRODUCTION, STAGING, DEVELOPMENT
    allowed_roles = Column(String(255), default="ADMIN,MANAGER")
    rotation_days = Column(Integer, default=90)
    last_rotated_at = Column(String(50), nullable=True)
    access_count = Column(Integer, default=0)
    created_by = Column(String(255), default="admin@acroflow.enterprise")

