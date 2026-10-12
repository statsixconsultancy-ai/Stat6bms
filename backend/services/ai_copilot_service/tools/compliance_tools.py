from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from common.config import get_service_config
from common.database import create_db_manager
from services.compliance_service.models import AuditLog, ComplianceControl
from services.ai_copilot_service.tools.base import (
    ToolDefinition, DataTier, SideEffect, ApprovalRequirement
)


class GetAuditLogsArgs(BaseModel):
    action_filter: Optional[str] = Field(default=None, description="Filter: LOGIN, USER_CREATED, INVOICE_PAID, AGENT_ACTION")
    limit: int = Field(default=10, description="Max logs to return")


class GetComplianceStatusArgs(BaseModel):
    framework: Optional[str] = Field(default="SOC2 Type II", description="Compliance framework e.g. 'SOC2 Type II', 'GDPR'")


def _get_compliance_session():
    cfg = get_service_config("compliance-service", 8011, "compliance.db")
    mgr = create_db_manager(cfg.database_url)
    return next(mgr.get_session())


def execute_get_audit_logs(args: GetAuditLogsArgs, user_ctx: Any) -> List[Dict[str, Any]]:
    session = _get_compliance_session()
    try:
        q = session.query(AuditLog).filter_by(org_id=user_ctx.org_id)
        if args.action_filter:
            q = q.filter(AuditLog.action.ilike(f"%{args.action_filter}%"))
        logs = q.order_by(AuditLog.created_at.desc()).limit(args.limit).all()
        return [
            {
                "id": l.id,
                "actor": l.actor_email,
                "action": l.action,
                "resource": f"{l.resource_type}:{l.resource_id}",
                "timestamp": l.created_at.isoformat() if hasattr(l.created_at, "isoformat") else str(l.created_at)
            }
            for l in logs
        ]
    finally:
        session.close()


def execute_get_compliance_status(args: GetComplianceStatusArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_compliance_session()
    try:
        controls = session.query(ComplianceControl).all()
        passed_count = sum(1 for c in controls if c.status.lower() == "passed")
        total = len(controls) or 5
        pct = round((passed_count / total * 100), 1) if total > 0 else 100.0
        return {
            "framework": args.framework or "SOC2 Type II",
            "compliance_percentage": pct,
            "status": "COMPLIANT" if pct >= 90.0 else "IN_REVIEW",
            "total_controls_audited": total,
            "controls_passed": passed_count,
            "controls": [
                {
                    "code": c.control_code,
                    "name": c.name,
                    "status": c.status,
                    "last_tested": c.last_tested
                }
                for c in controls
            ]
        }
    finally:
        session.close()


COMPLIANCE_TOOLS = [
    ToolDefinition(
        name="get_audit_logs",
        description="Inspect cryptographic, tamper-evident security audit logs and administrative event history.",
        category="compliance",
        args_schema=GetAuditLogsArgs,
        side_effect=SideEffect.READ,
        required_permission="compliance.audit.view",
        output_tier=DataTier.TIER_1_INTERNAL,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_get_audit_logs
    ),
    ToolDefinition(
        name="get_compliance_status",
        description="Check current enterprise regulatory posture across SOC 2 Type II and GDPR controls.",
        category="compliance",
        args_schema=GetComplianceStatusArgs,
        side_effect=SideEffect.READ,
        required_permission="compliance.status.view",
        output_tier=DataTier.TIER_1_INTERNAL,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_get_compliance_status
    ),
]
