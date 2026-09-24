from typing import Optional, List
from pydantic import BaseModel

# --- Department Schemas ---
class DepartmentCreate(BaseModel):
    name: str
    code: str
    manager_name: Optional[str] = "Department Head"

class DepartmentResponse(BaseModel):
    id: str
    org_id: str
    name: str
    code: str
    manager_name: str

# --- Employee Schemas ---
class EmployeeCreate(BaseModel):
    user_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    department_id: Optional[str] = None
    job_title: str
    hire_date: Optional[str] = None
    employment_type: Optional[str] = "Full-Time"
    salary_annual: float = 120000.0

class EmployeeUpdate(BaseModel):
    department_id: Optional[str] = None
    job_title: Optional[str] = None
    salary_annual: Optional[float] = None
    status: Optional[str] = None

class EmployeeResponse(BaseModel):
    id: str
    org_id: str
    user_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    department_id: Optional[str] = None
    job_title: str
    hire_date: Optional[str] = None
    employment_type: str
    salary_annual: float
    status: str

# --- Attendance Schemas ---
class ClockInRequest(BaseModel):
    employee_id: str
    clock_in_time: Optional[str] = None

class ClockOutRequest(BaseModel):
    employee_id: str
    clock_out_time: Optional[str] = None

class AttendanceLogResponse(BaseModel):
    id: str
    org_id: str
    employee_id: str
    date: str
    clock_in: Optional[str] = None
    clock_out: Optional[str] = None
    work_hours: float
    status: str

# --- Leave Schemas ---
class LeaveRequestCreate(BaseModel):
    employee_id: str
    leave_type: Optional[str] = "Annual"
    start_date: str
    end_date: str
    days_count: int = 1
    reason: Optional[str] = None

class LeaveDecisionRequest(BaseModel):
    decision: str  # "Approved" or "Rejected"
    reviewer_notes: Optional[str] = None

class LeaveRequestResponse(BaseModel):
    id: str
    org_id: str
    employee_id: str
    leave_type: str
    start_date: str
    end_date: str
    days_count: int
    reason: Optional[str] = None
    status: str
    reviewer_notes: Optional[str] = None

# --- Payroll Schemas ---
class PayrollRunRequest(BaseModel):
    period_name: str  # e.g., "September 2026"
    period_start: Optional[str] = "2026-09-01"
    period_end: Optional[str] = "2026-09-30"

class PayslipResponse(BaseModel):
    id: str
    org_id: str
    payroll_run_id: str
    employee_id: str
    basic_salary: float
    allowances: float
    gross_pay: float
    tax_deduction: float
    net_pay: float
    status: str

class PayrollRunResponse(BaseModel):
    id: str
    org_id: str
    period_name: str
    total_gross: float
    total_tax: float
    total_net: float
    employees_count: int
    status: str
    payslips: List[PayslipResponse] = []

# --- Analytics ---
class HRHeadcountAnalyticsResponse(BaseModel):
    total_headcount: int
    active_employees: int
    departments_count: int
    total_annual_payroll_commitment: float
    average_salary: float
