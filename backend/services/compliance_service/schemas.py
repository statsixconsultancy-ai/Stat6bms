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
