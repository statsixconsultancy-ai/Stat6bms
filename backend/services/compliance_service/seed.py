import uuid
from sqlalchemy.orm import Session
from services.compliance_service.models import ComplianceControl

def seed_compliance_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds regulatory compliance framework controls. Zero preloaded secrets or audit trails."""
    if not session.query(ComplianceControl).filter_by(org_id=org_id).first():
        c1 = ComplianceControl(id=str(uuid.uuid4()), org_id=org_id, framework="SOC2 Type II", control_code="CC6.1", name="Logical Access Security & MFA Enforcement", status="Passed", last_tested="2026-10-01")
        c2 = ComplianceControl(id=str(uuid.uuid4()), org_id=org_id, framework="SOC2 Type II", control_code="CC6.2", name="Pre-Flight Identity Verification & Credential Issuance", status="Passed", last_tested="2026-10-01")
        c3 = ComplianceControl(id=str(uuid.uuid4()), org_id=org_id, framework="SOC2 Type II", control_code="CC6.3", name="Role-Based Privilege Least Authorization", status="Passed", last_tested="2026-10-01")
        c4 = ComplianceControl(id=str(uuid.uuid4()), org_id=org_id, framework="SOC2 Type II", control_code="CC7.1", name="Continuous Vulnerability & Threat Monitoring", status="Passed", last_tested="2026-10-01")
        c5 = ComplianceControl(id=str(uuid.uuid4()), org_id=org_id, framework="SOC2 Type II", control_code="CC8.1", name="Microservice Change Management & CI/CD Gating", status="Passed", last_tested="2026-10-01")
        session.add_all([c1, c2, c3, c4, c5])
        session.commit()
