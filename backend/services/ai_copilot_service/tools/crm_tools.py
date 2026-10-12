import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from common.config import get_service_config
from common.database import create_db_manager
from services.crm_service.models import Lead, Deal, Company
from services.ai_copilot_service.tools.base import (
    ToolDefinition, DataTier, SideEffect, ApprovalRequirement
)


# --- Schemas ---

class FindLeadsArgs(BaseModel):
    query: Optional[str] = Field(default=None, description="Search term matching lead name or company")
    status: Optional[str] = Field(default=None, description="Lead status: New, Contacted, Qualified, Converted")
    limit: int = Field(default=10, description="Max results to return")


class CreateLeadArgs(BaseModel):
    name: str = Field(description="Full name of lead contact e.g. 'Priya Nair'")
    company_name: str = Field(description="Organization or corporate account name")
    email: str = Field(description="Direct business email address")
    source: Optional[str] = Field(default="Website", description="Acquisition channel: Website, LinkedIn, Referral")
    notes: Optional[str] = Field(default=None, description="Contextual lead qualification notes")


class FindDealsArgs(BaseModel):
    stage: Optional[str] = Field(default=None, description="Deal stage: Prospecting, Proposal Sent, Negotiation, Won")
    min_amount: Optional[float] = Field(default=None, description="Minimum deal size filter")
    limit: int = Field(default=10, description="Max deals to return")


class CreateDealArgs(BaseModel):
    title: str = Field(description="Commercial engagement title e.g. 'Zenith Labs Global Enterprise'")
    company_name: str = Field(description="Company account name")
    amount: float = Field(gt=0, description="Deal contractual value in USD")
    stage: Optional[str] = Field(default="Prospecting", description="Initial pipeline stage")
    probability: Optional[int] = Field(default=25, ge=0, le=100, description="Confidence percentage")


class UpdateDealStageArgs(BaseModel):
    deal_id: str = Field(description="Unique deal ID or identifier")
    new_stage: str = Field(description="Target stage: Qualification, Proposal Sent, Negotiation, Won, Lost")


# --- Executors ---

def _get_crm_session():
    cfg = get_service_config("crm-service", 8002, "crm.db")
    mgr = create_db_manager(cfg.database_url)
    return next(mgr.get_session())


def execute_find_leads(args: FindLeadsArgs, user_ctx: Any) -> List[Dict[str, Any]]:
    session = _get_crm_session()
    try:
        q = session.query(Lead).filter_by(org_id=user_ctx.org_id)
        if args.status:
            q = q.filter(Lead.status.ilike(f"%{args.status}%"))
        if args.query:
            term = f"%{args.query}%"
            q = q.filter((Lead.first_name.ilike(term)) | (Lead.last_name.ilike(term)) | (Lead.company_name.ilike(term)))
        leads = q.limit(args.limit).all()
        return [
            {
                "id": l.id,
                "name": f"{l.first_name} {l.last_name}",
                "company": l.company_name,
                "email": l.email,
                "status": l.status,
                "source": l.source,
                "score": l.score,
                "assigned_to": l.assigned_to
            }
            for l in leads
        ]
    finally:
        session.close()


def execute_create_lead(args: CreateLeadArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_crm_session()
    try:
        parts = args.name.strip().split(" ", 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ""

        lead_id = str(uuid.uuid4())
        lead = Lead(
            id=lead_id,
            org_id=user_ctx.org_id,
            first_name=first_name,
            last_name=last_name,
            email=args.email,
            company_name=args.company_name,
            source=args.source or "Website",
            status="New",
            score=65,
            assigned_to=getattr(user_ctx, "email", "Marcus Chen"),
            notes=args.notes
        )
        session.add(lead)
        session.commit()
        return {
            "id": lead_id,
            "name": args.name,
            "company": args.company_name,
            "email": args.email,
            "status": "New",
            "message": f"Lead '{args.name}' ({args.company_name}) successfully created in CRM pipeline."
        }
    finally:
        session.close()


def execute_find_deals(args: FindDealsArgs, user_ctx: Any) -> List[Dict[str, Any]]:
    session = _get_crm_session()
    try:
        q = session.query(Deal).filter_by(org_id=user_ctx.org_id)
        if args.stage:
            q = q.filter(Deal.stage.ilike(f"%{args.stage}%"))
        if args.min_amount:
            q = q.filter(Deal.amount >= args.min_amount)
        deals = q.limit(args.limit).all()
        return [
            {
                "id": d.id,
                "title": d.title,
                "amount": d.amount,
                "stage": d.stage,
                "probability": d.probability,
                "owner": d.owner
            }
            for d in deals
        ]
    finally:
        session.close()


def execute_create_deal(args: CreateDealArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_crm_session()
    try:
        deal_id = str(uuid.uuid4())
        deal = Deal(
            id=deal_id,
            org_id=user_ctx.org_id,
            title=args.title,
            amount=args.amount,
            stage=args.stage or "Prospecting",
            probability=args.probability or 25,
            owner=getattr(user_ctx, "email", "Account Executive")
        )
        session.add(deal)
        session.commit()
        return {
            "id": deal_id,
            "title": args.title,
            "amount": args.amount,
            "stage": deal.stage,
            "message": f"Deal '{args.title}' (${args.amount:,.2f}) created in active pipeline."
        }
    finally:
        session.close()


def execute_update_deal_stage(args: UpdateDealStageArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_crm_session()
    try:
        deal = session.query(Deal).filter_by(id=args.deal_id, org_id=user_ctx.org_id).first()
        if not deal:
            # Try fuzzy match on title
            deal = session.query(Deal).filter(Deal.title.ilike(f"%{args.deal_id}%"), Deal.org_id == user_ctx.org_id).first()
        if not deal:
            return {"error": "DEAL_NOT_FOUND", "message": f"Deal '{args.deal_id}' not found."}

        old_stage = deal.stage
        deal.stage = args.new_stage
        session.commit()
        return {
            "id": deal.id,
            "title": deal.title,
            "previous_stage": old_stage,
            "new_stage": deal.stage,
            "message": f"Deal '{deal.title}' advanced from {old_stage} to {deal.stage}."
        }
    finally:
        session.close()


# --- Tool Registry Definitions ---

CRM_TOOLS = [
    ToolDefinition(
        name="find_leads",
        description="Search active sales leads by name, company, or qualification status.",
        category="crm",
        args_schema=FindLeadsArgs,
        side_effect=SideEffect.READ,
        required_permission="crm.leads.view",
        output_tier=DataTier.TIER_2_CONFIDENTIAL,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_find_leads
    ),
    ToolDefinition(
        name="create_lead",
        description="Register a new prospect lead in the sales pipeline with contact info and source attribution.",
        category="crm",
        args_schema=CreateLeadArgs,
        side_effect=SideEffect.WRITE,
        required_permission="crm.leads.create",
        output_tier=DataTier.TIER_2_CONFIDENTIAL,
        approval_requirement=ApprovalRequirement.USER_CONFIRM,
        executor=execute_create_lead
    ),
    ToolDefinition(
        name="find_deals",
        description="Query pipeline commercial deals by stage (Proposal, Negotiation, Won) or minimum revenue size.",
        category="crm",
        args_schema=FindDealsArgs,
        side_effect=SideEffect.READ,
        required_permission="crm.deals.view",
        output_tier=DataTier.TIER_2_CONFIDENTIAL,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_find_deals
    ),
    ToolDefinition(
        name="create_deal",
        description="Create a new high-value commercial sales deal opportunity in the revenue pipeline.",
        category="crm",
        args_schema=CreateDealArgs,
        side_effect=SideEffect.WRITE,
        required_permission="crm.deals.create",
        output_tier=DataTier.TIER_2_CONFIDENTIAL,
        approval_requirement=ApprovalRequirement.USER_CONFIRM,
        executor=execute_create_deal
    ),
    ToolDefinition(
        name="update_deal_stage",
        description="Advance or update a pipeline deal's current stage (e.g., to 'Negotiation' or 'Won').",
        category="crm",
        args_schema=UpdateDealStageArgs,
        side_effect=SideEffect.WRITE,
        required_permission="crm.deals.update",
        output_tier=DataTier.TIER_2_CONFIDENTIAL,
        approval_requirement=ApprovalRequirement.USER_CONFIRM,
        executor=execute_update_deal_stage
    ),
]
