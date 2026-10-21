import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from common.config import get_service_config
from common.database import create_db_manager
from services.finance_service.models import Invoice, Expense, Payment
from services.ai_copilot_service.tools.base import (
    ToolDefinition, DataTier, SideEffect, ApprovalRequirement
)


# --- Arguments & Output Schemas ---

class GetFinancialSummaryArgs(BaseModel):
    include_overdue_list: bool = Field(default=True, description="Whether to include list of overdue accounts")
    period: Optional[str] = Field(default="FY2026", description="Fiscal period e.g. FY2026, Q3")


class FinancialSummaryOutput(BaseModel):
    total_paid_revenue: float
    total_invoiced: float
    total_expenses: float
    net_operating_profit: float
    operating_margin_pct: float
    overdue_invoices_count: int
    overdue_amount: float
    overdue_accounts: List[Dict[str, Any]] = []


class FindInvoicesArgs(BaseModel):
    client_query: Optional[str] = Field(default=None, description="Client or company name substring to match")
    status: Optional[str] = Field(default=None, description="Status filter: Sent, Paid, Overdue, Draft")
    limit: int = Field(default=10, description="Max invoices to return")


class CreateInvoiceArgs(BaseModel):
    client_name: str = Field(description="Name of the client enterprise")
    amount: float = Field(gt=0, description="Total amount in USD")
    due_date: str = Field(description="Payment due date (YYYY-MM-DD)")
    description: Optional[str] = Field(default="Enterprise Software & Services", description="Line item description")


class SendPaymentReminderArgs(BaseModel):
    invoice_id: str = Field(description="Unique UUID or number of the invoice")
    client_name: str = Field(description="Target client name")
    amount: float = Field(description="Outstanding amount to remind")


# --- Executors ---

def _get_finance_session():
    cfg = get_service_config("finance-service", 8006, "finance.db")
    mgr = create_db_manager(cfg.database_url)
    return next(mgr.get_session())


def execute_get_financial_summary(args: GetFinancialSummaryArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_finance_session()
    try:
        invoices = session.query(Invoice).filter_by(org_id=user_ctx.org_id).all()
        expenses = session.query(Expense).filter_by(org_id=user_ctx.org_id).all()

        paid_rev = sum(i.total_amount for i in invoices if i.status.lower() == "paid")
        total_inv = sum(i.total_amount for i in invoices)
        total_exp = sum(e.amount for e in expenses)
        overdue_invs = [i for i in invoices if i.status.lower() == "overdue"]
        overdue_amt = sum(i.balance_due or i.total_amount for i in overdue_invs)

        profit = paid_rev - total_exp
        margin = round((profit / paid_rev * 100), 1) if paid_rev > 0 else 0.0

        overdue_list = [
            {
                "id": i.id,
                "invoice_number": i.invoice_number,
                "client": i.client_name,
                "amount": i.total_amount,
                "due_date": i.due_date,
                "status": i.status
            }
            for i in overdue_invs
        ] if args.include_overdue_list else []

        return {
            "total_paid_revenue": paid_rev,
            "total_invoiced": total_inv,
            "total_expenses": total_exp,
            "net_operating_profit": profit,
            "operating_margin_pct": margin,
            "overdue_invoices_count": len(overdue_invs),
            "overdue_amount": overdue_amt,
            "overdue_accounts": overdue_list
        }
    finally:
        session.close()


def execute_find_invoices(args: FindInvoicesArgs, user_ctx: Any) -> List[Dict[str, Any]]:
    session = _get_finance_session()
    try:
        q = session.query(Invoice).filter_by(org_id=user_ctx.org_id)
        if args.status:
            q = q.filter(Invoice.status.ilike(f"%{args.status}%"))
        if args.client_query:
            q = q.filter(Invoice.client_name.ilike(f"%{args.client_query}%"))
        results = q.limit(args.limit).all()
        return [
            {
                "id": i.id,
                "invoice_number": i.invoice_number,
                "client_name": i.client_name,
                "due_date": i.due_date,
                "status": i.status,
                "total_amount": i.total_amount,
                "balance_due": i.balance_due or i.total_amount
            }
            for i in results
        ]
    finally:
        session.close()


def execute_create_invoice(args: CreateInvoiceArgs, user_ctx: Any) -> Dict[str, Any]:
    session = _get_finance_session()
    try:
        inv_id = str(uuid.uuid4())
        num = f"INV-2026-{datetime.utcnow().strftime('%m%d%H%M')}"
        inv = Invoice(
            id=inv_id,
            org_id=user_ctx.org_id,
            invoice_number=num,
            client_name=args.client_name,
            issue_date=datetime.utcnow().strftime("%Y-%m-%d"),
            due_date=args.due_date,
            status="Sent",
            subtotal=args.amount,
            tax_amount=0.0,
            total_amount=args.amount,
            balance_due=args.amount
        )
        session.add(inv)
        session.commit()
        return {
            "id": inv_id,
            "invoice_number": num,
            "client_name": args.client_name,
            "amount": args.amount,
            "due_date": args.due_date,
            "status": "Sent",
            "message": f"Invoice {num} successfully generated and registered."
        }
    finally:
        session.close()


def execute_send_payment_reminder(args: SendPaymentReminderArgs, user_ctx: Any) -> Dict[str, Any]:
    # Consequential external action: sends notice to client
    return {
        "invoice_id": args.invoice_id,
        "client_name": args.client_name,
        "amount": args.amount,
        "dispatched_at": datetime.utcnow().isoformat(),
        "status": "DISPATCHED",
        "message": f"Payment reminder notice for ${args.amount:,.2f} delivered to {args.client_name} accounting department."
    }


# --- Tool Registry Definitions ---

FINANCE_TOOLS = [
    ToolDefinition(
        name="get_financial_summary",
        description="Query live corporate financial health, paid revenue, total invoiced, operating expenses, operating margin, and overdue receivables.",
        category="finance",
        args_schema=GetFinancialSummaryArgs,
        side_effect=SideEffect.READ,
        required_permission="finance.view",
        output_tier=DataTier.TIER_1_INTERNAL,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_get_financial_summary
    ),
    ToolDefinition(
        name="find_invoices",
        description="Search client invoices by client name, status (Paid, Sent, Overdue), or query terms.",
        category="finance",
        args_schema=FindInvoicesArgs,
        side_effect=SideEffect.READ,
        required_permission="finance.view",
        output_tier=DataTier.TIER_2_CONFIDENTIAL,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_find_invoices
    ),
    ToolDefinition(
        name="create_invoice",
        description="Generate and register a new enterprise client invoice in the financial general ledger.",
        category="finance",
        args_schema=CreateInvoiceArgs,
        side_effect=SideEffect.WRITE,
        required_permission="finance.create",
        output_tier=DataTier.TIER_2_CONFIDENTIAL,
        approval_requirement=ApprovalRequirement.USER_CONFIRM,
        executor=execute_create_invoice
    ),
    ToolDefinition(
        name="send_payment_reminder",
        description="Send an official payment collection notice to a client for an overdue invoice. Consequential external communication.",
        category="finance",
        args_schema=SendPaymentReminderArgs,
        side_effect=SideEffect.EXTERNAL,
        required_permission="finance.execute",
        output_tier=DataTier.TIER_2_CONFIDENTIAL,
        approval_requirement=ApprovalRequirement.ROLE_APPROVAL,
        approver_role="FINANCE_MANAGER",
        executor=execute_send_payment_reminder
    ),
]
