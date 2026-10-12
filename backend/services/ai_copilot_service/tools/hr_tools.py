from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

from common.config import get_service_config
from common.database import create_db_manager
from services.hr_service.models import Employee, Department
from services.ai_copilot_service.tools.base import (
    ToolDefinition, DataTier, SideEffect, ApprovalRequirement
)


# --- Schemas ---

class GetPayrollSummaryArgs(BaseModel):
    department: Optional[str] = Field(default=None, description="Filter summary by specific department name")


class GetEmployeeCompensationArgs(BaseModel):
    department: Optional[str] = Field(default=None, description="Department filter for compensation breakdown")


class ListEmployeesArgs(BaseModel):
    department: Optional[str] = Field(default=None, description="Department filter")
    status: Optional[str] = Field(default="Active", description="Employment status: Active, On Leave")
    limit: int = Field(default=25, description="Max records to return")


# --- Executors ---

def _get_hr_session():
    cfg = get_service_config("hr-service", 8005, "hr.db")
    mgr = create_db_manager(cfg.database_url)
    return next(mgr.get_session())


def execute_get_payroll_summary(args: GetPayrollSummaryArgs, user_ctx: Any) -> Dict[str, Any]:
    # RBAC gate: Only Founder / Admin or HR Manager can view payroll summary
    user_role = str(getattr(user_ctx, "role", "")).lower()
    if user_role not in ["admin", "super_admin", "founder", "hr_manager"]:
        return {
            "error": "ACCESS_DENIED",
            "message": "Payroll aggregation access is restricted to Founder, Super Admin, and HR Managers."
        }

    session = _get_hr_session()
    try:
        employees = session.query(Employee).filter_by(org_id=user_ctx.org_id, status="Active").all()
        departments = session.query(Department).filter_by(org_id=user_ctx.org_id).all()
        dept_map = {d.id: d.name for d in departments}

        by_dept: Dict[str, Dict[str, Any]] = {}
        total_payroll = 0.0

        for emp in employees:
            dept_name = dept_map.get(emp.department_id, "General Operations")
            if args.department and args.department.lower() not in dept_name.lower():
                continue
            if dept_name not in by_dept:
                by_dept[dept_name] = {"headcount": 0, "annual_total": 0.0, "monthly_run": 0.0}
            sal = emp.salary_annual or 120000.0
            by_dept[dept_name]["headcount"] += 1
            by_dept[dept_name]["annual_total"] += sal
            by_dept[dept_name]["monthly_run"] += sal / 12.0
            total_payroll += sal

        return {
            "tier": "TIER_3_RESTRICTED",
            "total_active_headcount": len(employees),
            "total_annual_payroll": total_payroll,
            "monthly_payroll_run": total_payroll / 12.0,
            "department_breakdown": [
                {
                    "department": d_name,
                    "headcount": data["headcount"],
                    "annual_payroll": data["annual_total"],
                    "monthly_payroll": round(data["monthly_run"], 2),
                    "avg_salary": round(data["annual_total"] / data["headcount"], 2) if data["headcount"] > 0 else 0
                }
                for d_name, data in by_dept.items()
            ]
        }
    finally:
        session.close()


def execute_get_employee_compensation(args: GetEmployeeCompensationArgs, user_ctx: Any) -> Dict[str, Any]:
    # Executive Founder Gate: individual salaries are Tier 3 Restricted
    user_role = str(getattr(user_ctx, "role", "")).lower()
    if user_role not in ["admin", "super_admin", "founder"]:
        return {
            "error": "ACCESS_DENIED",
            "message": "Individual employee compensation logs are restricted strictly to the Founder and Super Admin."
        }

    session = _get_hr_session()
    try:
        employees = session.query(Employee).filter_by(org_id=user_ctx.org_id).all()
        departments = session.query(Department).filter_by(org_id=user_ctx.org_id).all()
        dept_map = {d.id: d.name for d in departments}

        records = []
        for emp in employees:
            dept_name = dept_map.get(emp.department_id, "Engineering")
            if args.department and args.department.lower() not in dept_name.lower():
                continue
            records.append({
                "employee_id": emp.id,
                "name": f"{emp.first_name} {emp.last_name}",
                "job_title": emp.job_title,
                "department": dept_name,
                "employment_type": emp.employment_type or "Full-Time",
                "annual_salary": emp.salary_annual or 120000.0,
                "monthly_gross": round((emp.salary_annual or 120000.0) / 12.0, 2),
                "status": emp.status
            })

        return {
            "tier": "TIER_3_RESTRICTED",
            "total_employees": len(records),
            "total_annual_expenditure": sum(r["annual_salary"] for r in records),
            "compensation_registry": records
        }
    finally:
        session.close()


def execute_list_employees(args: ListEmployeesArgs, user_ctx: Any) -> List[Dict[str, Any]]:
    session = _get_hr_session()
    try:
        q = session.query(Employee).filter_by(org_id=user_ctx.org_id)
        if args.status:
            q = q.filter_by(status=args.status)
        employees = q.limit(args.limit).all()
        departments = session.query(Department).filter_by(org_id=user_ctx.org_id).all()
        dept_map = {d.id: d.name for d in departments}

        return [
            {
                "id": emp.id,
                "name": f"{emp.first_name} {emp.last_name}",
                "job_title": emp.job_title,
                "email": emp.email,
                "department": dept_map.get(emp.department_id, "General"),
                "status": emp.status,
                "hire_date": emp.hire_date
            }
            for emp in employees
        ]
    finally:
        session.close()


# --- Tool Registry Definitions ---

HR_TOOLS = [
    ToolDefinition(
        name="get_payroll_summary",
        description="Calculate department-level aggregate payroll, total annual wage expenditure, and monthly disbursement budgets (Tier 3 data).",
        category="hr",
        args_schema=GetPayrollSummaryArgs,
        side_effect=SideEffect.READ,
        required_permission="hr.payroll.view",
        output_tier=DataTier.TIER_3_RESTRICTED,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_get_payroll_summary
    ),
    ToolDefinition(
        name="get_employee_compensation",
        description="Query individual employee salary, compensation, and wage ledger. STRICTLY RESTRICTED to Founder / Super Admin.",
        category="hr",
        args_schema=GetEmployeeCompensationArgs,
        side_effect=SideEffect.READ,
        required_permission="hr.compensation.view",
        output_tier=DataTier.TIER_3_RESTRICTED,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_get_employee_compensation
    ),
    ToolDefinition(
        name="list_employees",
        description="Browse the company staff directory, job titles, departments, and active statuses (without sensitive compensation).",
        category="hr",
        args_schema=ListEmployeesArgs,
        side_effect=SideEffect.READ,
        required_permission="hr.view",
        output_tier=DataTier.TIER_1_INTERNAL,
        approval_requirement=ApprovalRequirement.NONE,
        executor=execute_list_employees
    ),
]
