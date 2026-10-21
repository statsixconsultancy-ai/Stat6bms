from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class AuditLogCreate(BaseModel):
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    client_ip: Optional[str] = "127.0.0.1"
    metadata_json: Optional[str] = None

class AuditLogResponse(BaseModel):
    id: str
    org_id: str
    actor_id: str
    actor_email: str
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    client_ip: str
    created_at: str

class GDPRExportRequest(BaseModel):
    subject_email: str

class GDPRExportResponse(BaseModel):
    request_id: str
    subject_email: str
    status: str
    export_bundle: Dict[str, Any]
    generated_at: str

class GDPRAnonymizeRequest(BaseModel):
    subject_email: str
    confirmation: bool = True

class GDPRAnonymizeResponse(BaseModel):
    request_id: str
    subject_email: str
    status: str
    redacted_records_count: int
    anonymized_at: str

class RBACEvaluateRequest(BaseModel):
    user_id: str
    user_role: str = "member"
    persona: str = "EMPLOYEE"
    module: str # e.g. 'finance', 'hr', 'crm', 'procurement'
    action: str = "READ" # CREATE, READ, UPDATE, DELETE, EXPORT, APPROVE
    resource_owner_id: Optional[str] = None

class RBACEvaluateResponse(BaseModel):
    allowed: bool
    reason: str
    masked_fields: List[str] = []
    visible_scope: str = "ORG" # OWN, SUBORDINATE, DEPARTMENT, ORG

class ComplianceControlResponse(BaseModel):
    id: str
    framework: str
    control_code: str
    name: str
    status: str
    last_tested: str

class SOC2ReadinessResponse(BaseModel):
    framework: str
    total_controls: int
    passed_controls: int
    compliance_score_percent: float
    status: str
    controls: List[ComplianceControlResponse] = []


class VaultSecretCreate(BaseModel):
    name: str
    category: str = "API_KEY"
    username: Optional[str] = None
    service_url: Optional[str] = None
    secret_value: str
    environment: str = "PRODUCTION"
    allowed_roles: str = "ADMIN,MANAGER"
    rotation_days: int = 90


class VaultSecretRotateRequest(BaseModel):
    new_secret_value: str


class VaultSecretResponse(BaseModel):
    id: str
    org_id: str
    name: str
    category: str
    username: Optional[str] = None
    service_url: Optional[str] = None
    masked_preview: str
    environment: str
    allowed_roles: str
    rotation_days: int
    last_rotated_at: Optional[str] = None
    access_count: int
    created_by: Optional[str] = None
    created_at: Optional[str] = None


class VaultSecretRevealResponse(BaseModel):
    id: str
    name: str
    category: str
    username: Optional[str] = None
    plaintext_secret: str
    access_count: int
    audit_log_id: str
    revealed_at: str

