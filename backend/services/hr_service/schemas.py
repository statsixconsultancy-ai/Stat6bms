from typing import Optional, List, Dict, Any
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
    manager_id: Optional[str] = None

class EmployeeUpdate(BaseModel):
    department_id: Optional[str] = None
    job_title: Optional[str] = None
    salary_annual: Optional[float] = None
    status: Optional[str] = None
    manager_id: Optional[str] = None

class EmployeeResponse(BaseModel):
    id: str
    org_id: str
    user_id: Optional[str] = None
    employee_code: Optional[str] = None
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
    manager_id: Optional[str] = None

# --- Attendance Schemas ---
class ClockInRequest(BaseModel):
    employee_id: str
    date: Optional[str] = None
    clock_in: Optional[str] = None
    clock_in_time: Optional[str] = None
    work_mode: Optional[str] = "Office (Geofence Verified)"
    ip_address: Optional[str] = "127.0.0.1"
    latitude: Optional[float] = None
    longitude: Optional[float] = None

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
    hours_logged: float = 8.0
    work_mode: str = "Office (Geofence Verified)"
    status: str
    ip_address: Optional[str] = "127.0.0.1"
    geofence_verified: Optional[bool] = True

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
    pf_deduction: float = 0.0
    esi_deduction: float = 0.0
    professional_tax: float = 200.0
    tds_tax: float = 0.0
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

# --- Statutory Payroll Calculation Engine ---
class StatutoryPayrollCalculationRequest(BaseModel):
    basic_salary: Optional[float] = None
    allowances: Optional[float] = 0.0
    employee_id: Optional[str] = None
    pay_period: Optional[str] = "2026-10"
    regime: Optional[str] = "IN_STATUTORY"
    bonus: Optional[float] = 0.0

class StatutoryPayrollCalculationResponse(BaseModel):
    employee_name: Optional[str] = None
    basic_salary: float
    allowances: float
    gross_pay: float
    pf_deduction: float
    esi_deduction: float
    professional_tax: float
    tds_tax: float
    total_deductions: float
    net_pay: float
    components: Optional[Dict[str, float]] = None
    deductions: Optional[Dict[str, float]] = None

# --- OKRs & Performance Reviews ---
class OKRCreate(BaseModel):
    title: Optional[str] = None
    objective: Optional[str] = None
    key_result: Optional[str] = None
    owner_id: Optional[str] = None
    employee_id: Optional[str] = None
    quarter: Optional[str] = "Q4-2026"
    target_value: Optional[float] = 100.0
    current_value: Optional[float] = 0.0
    key_results: Optional[str] = "[]"

class OKRUpdate(BaseModel):
    progress_percent: Optional[float] = None
    status: Optional[str] = None

class OKRResponse(BaseModel):
    id: str
    org_id: str
    title: str
    owner_id: str
    quarter: str
    progress_percent: float
    target_value: float = 100.0
    current_value: float = 0.0
    status: str
    key_results: str

# --- ATS Recruitment Pipeline ---
class JobOpeningCreate(BaseModel):
    title: str
    department_id: Optional[str] = None
    department_name: Optional[str] = None
    positions_count: Optional[int] = 1
    headcount_target: Optional[int] = None
    salary_band_min: Optional[float] = None
    salary_band_max: Optional[float] = None
    min_experience_years: Optional[int] = 3

class JobOpeningResponse(BaseModel):
    id: str
    org_id: str
    title: str
    department_id: Optional[str] = None
    department_name: Optional[str] = "Engineering"
    positions_count: int
    headcount_target: int = 1
    salary_band_min: float = 120000.0
    salary_band_max: float = 165000.0
    status: str
    min_experience_years: int

class CandidateCreate(BaseModel):
    job_opening_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    resume_url: Optional[str] = None
    resume_score: Optional[int] = 92
    stage: Optional[str] = "Screening"

class CandidateStageUpdateRequest(BaseModel):
    stage: str  # Screening, Interview, Offer, Hired

class CandidateResponse(BaseModel):
    id: str
    org_id: str
    job_opening_id: Optional[str] = None
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    stage: str
    rating: float
    resume_score: int = 92
    resume_url: Optional[str] = None
    converted_employee_id: Optional[str] = None

# --- Analytics ---
class HRHeadcountAnalyticsResponse(BaseModel):
    total_headcount: int
    active_employees: int
    departments_count: int
    total_annual_payroll_commitment: float
    average_salary: float

