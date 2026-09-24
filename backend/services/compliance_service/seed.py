import uuid
from sqlalchemy.orm import Session
from services.compliance_service.models import AuditLog, ComplianceControl

def seed_compliance_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds regulatory compliance controls and immutable audit trails."""
    if session.query(ComplianceControl).filter_by(org_id=org_id).first():
        return

    # 1. Audit Logs
    a1 = AuditLog(
        id=str(uuid.uuid4()),
        org_id=org_id,
        actor_id="usr-dev-001",
        actor_email="admin@acroflow.enterprise",
        action="USER_AUTHENTICATED",
        resource_type="AUTH",
        resource_id="usr-dev-001",
        client_ip="192.168.1.10"
    )
    a2 = AuditLog(
        id=str(uuid.uuid4()),
        org_id=org_id,
        actor_id="usr-dev-001",
        actor_email="admin@acroflow.enterprise",
        action="ROLE_GRANTED",
        resource_type="IAM",
        resource_id="usr-dev-002",
        client_ip="192.168.1.10"
    )
    session.add_all([a1, a2])
    session.flush()

    # 2. SOC2 Type II Controls
    c1 = ComplianceControl(id=str(uuid.uuid4()), org_id=org_id, framework="SOC2 Type II", control_code="CC6.1", name="Logical Access Security & MFA Enforcement", status="Passed", last_tested="2026-09-20")
    c2 = ComplianceControl(id=str(uuid.uuid4()), org_id=org_id, framework="SOC2 Type II", control_code="CC6.2", name="Pre-Flight Identity Verification & Credential Issuance", status="Passed", last_tested="2026-09-20")
    c3 = ComplianceControl(id=str(uuid.uuid4()), org_id=org_id, framework="SOC2 Type II", control_code="CC6.3", name="Role-Based Privilege Least Authorization", status="Passed", last_tested="2026-09-20")
    c4 = ComplianceControl(id=str(uuid.uuid4()), org_id=org_id, framework="SOC2 Type II", control_code="CC7.1", name="Continuous Vulnerability & Threat Monitoring", status="Passed", last_tested="2026-09-21")
    c5 = ComplianceControl(id=str(uuid.uuid4()), org_id=org_id, framework="SOC2 Type II", control_code="CC8.1", name="Microservice Change Management & CI/CD Gating", status="Passed", last_tested="2026-09-22")
    session.add_all([c1, c2, c3, c4, c5])
    session.commit()
