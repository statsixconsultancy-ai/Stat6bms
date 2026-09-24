import os
import sys
import uuid
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.config import get_service_config
from common.database import create_db_manager
from common.models import Base
from common.security import get_user_context, UserContext
from common.middleware import setup_microservice_middleware
from common.event_bus import event_bus

from services.hr_service.models import Department, Employee, AttendanceLog, LeaveRequest, PayrollRun, Payslip
from services.hr_service.schemas import (
    DepartmentCreate, DepartmentResponse,
    EmployeeCreate, EmployeeUpdate, EmployeeResponse,
    ClockInRequest, ClockOutRequest, AttendanceLogResponse,
    LeaveRequestCreate, LeaveDecisionRequest, LeaveRequestResponse,
    PayrollRunRequest, PayrollRunResponse, PayslipResponse,
    HRHeadcountAnalyticsResponse
)
from services.hr_service.seed import seed_hr_data

config = get_service_config("hr-service", default_port=8005, db_filename="hr.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="BMS People Operations — HR & Payroll Microservice",
    description="Employee Directory, Attendance Clock-In, Leave Workflows, and Automated Payroll Engine",
    version="2.0.0"
)

setup_microservice_middleware(app, "hr-service", config.cors_origins)

@app.on_event("startup")
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_hr_data(session)
    finally:
        session.close()

def get_db():
    yield from db_mgr.get_session()

# ----------------------------------------------------
# 1. Health & Webhook Endpoints
# ----------------------------------------------------
@app.get("/health")
def health():
    return {"service": "hr-service", "status": "UP", "port": config.service_port}

@app.post("/webhooks/events")
async def handle_events(event: dict):
    return {"status": "received", "event_name": event.get("event_name")}

# ----------------------------------------------------
# 2. Departments Endpoints
# ----------------------------------------------------
@app.get("/hr/departments", response_model=List[DepartmentResponse])
def list_departments(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    depts = db.query(Department).filter_by(org_id=user_ctx.org_id).all()
    return [DepartmentResponse(**d.to_dict()) for d in depts]

@app.post("/hr/departments", response_model=DepartmentResponse)
def create_department(req: DepartmentCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    dept = Department(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        name=req.name,
        code=req.code,
        manager_name=req.manager_name or "Department Head"
    )
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return DepartmentResponse(**dept.to_dict())

# ----------------------------------------------------
# 3. Attendance & Leave Endpoints
# ----------------------------------------------------
@app.get("/hr/attendance", response_model=List[AttendanceLogResponse])
def list_attendance(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    logs = db.query(AttendanceLog).filter_by(org_id=user_ctx.org_id).order_by(AttendanceLog.date.desc()).all()
    return [AttendanceLogResponse(**l.to_dict()) for l in logs]

@app.post("/hr/attendance/clock-in", response_model=AttendanceLogResponse)
def clock_in(req: ClockInRequest, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    date_str = "2026-09-24"
    time_str = req.clock_in_time or "09:00 AM"

    log = db.query(AttendanceLog).filter_by(employee_id=req.employee_id, date=date_str, org_id=user_ctx.org_id).first()
    if log:
        log.clock_in = time_str
    else:
        log = AttendanceLog(
            id=str(uuid.uuid4()),
            org_id=user_ctx.org_id,
            employee_id=req.employee_id,
            date=date_str,
            clock_in=time_str,
            status="Present"
        )
        db.add(log)
    db.commit()
    db.refresh(log)
    return AttendanceLogResponse(**log.to_dict())

@app.post("/hr/attendance/clock-out", response_model=AttendanceLogResponse)
def clock_out(req: ClockOutRequest, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    date_str = "2026-09-24"
    time_str = req.clock_out_time or "05:00 PM"

    log = db.query(AttendanceLog).filter_by(employee_id=req.employee_id, date=date_str, org_id=user_ctx.org_id).first()
    if not log:
        raise HTTPException(status_code=400, detail="Cannot clock out without prior clock in record")

    log.clock_out = time_str
    log.work_hours = 8.0
    db.commit()
    db.refresh(log)
    return AttendanceLogResponse(**log.to_dict())

@app.get("/hr/leave", response_model=List[LeaveRequestResponse])
def list_leave_requests(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    leaves = db.query(LeaveRequest).filter_by(org_id=user_ctx.org_id).order_by(LeaveRequest.created_at.desc()).all()
    return [LeaveRequestResponse(**l.to_dict()) for l in leaves]

@app.post("/hr/leave", response_model=LeaveRequestResponse)
def request_leave(req: LeaveRequestCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    leave = LeaveRequest(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        employee_id=req.employee_id,
        leave_type=req.leave_type or "Annual",
        start_date=req.start_date,
        end_date=req.end_date,
        days_count=req.days_count,
        reason=req.reason,
        status="Pending"
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return LeaveRequestResponse(**leave.to_dict())

@app.post("/hr/leave/{id}/decision", response_model=LeaveRequestResponse)
def decide_leave_request(id: str, req: LeaveDecisionRequest, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    leave = db.query(LeaveRequest).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    leave.status = req.decision
    leave.reviewer_notes = req.reviewer_notes or f"Decision rendered by {user_ctx.email}"
    db.commit()
    db.refresh(leave)
    return LeaveRequestResponse(**leave.to_dict())

# ----------------------------------------------------
# 4. Payroll Engine Endpoints
# ----------------------------------------------------
@app.post("/hr/payroll/run", response_model=PayrollRunResponse)
async def execute_payroll_run(
    req: PayrollRunRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Executes automated monthly payroll run for all active employees:
    1. Basic = Annual Salary / 12
    2. Allowances = 10% of Basic
    3. Gross = Basic + Allowances
    4. Tax Deduction = 20%
    5. Net = Gross - Tax
    6. Generates individual Payslips and aggregates Run total.
    7. Emits 'payroll.executed' domain event.
    """
    employees = db.query(Employee).filter_by(org_id=user_ctx.org_id, status="Active").all()
    if not employees:
        raise HTTPException(status_code=400, detail="No active employees to process payroll")

    run_id = str(uuid.uuid4())
    total_gross = 0.0
    total_tax = 0.0
    total_net = 0.0
    payslips = []

    for emp in employees:
        basic = round(emp.salary_annual / 12.0, 2)
        allowances = round(basic * 0.10, 2)
        gross = round(basic + allowances, 2)
        tax = round(gross * 0.20, 2)
        net = round(gross - tax, 2)

        total_gross += gross
        total_tax += tax
        total_net += net

        slip = Payslip(
            id=str(uuid.uuid4()),
            org_id=user_ctx.org_id,
            payroll_run_id=run_id,
            employee_id=emp.id,
            basic_salary=basic,
            allowances=allowances,
            gross_pay=gross,
            tax_deduction=tax,
            net_pay=net,
            status="Paid"
        )
        db.add(slip)
        payslips.append(slip)

    payroll_run = PayrollRun(
        id=run_id,
        org_id=user_ctx.org_id,
        period_name=req.period_name,
        period_start=req.period_start,
        period_end=req.period_end,
        total_gross=round(total_gross, 2),
        total_tax=round(total_tax, 2),
        total_net=round(total_net, 2),
        employees_count=len(employees),
        status="Completed"
    )
    db.add(payroll_run)
    db.commit()

    # Emit distributed event across microservices
    await event_bus.publish("payroll.executed", {
        "payroll_run_id": run_id,
        "period_name": req.period_name,
        "total_gross": round(total_gross, 2),
        "total_net": round(total_net, 2),
        "employees_count": len(employees)
    }, org_id=user_ctx.org_id)

    res_slips = [PayslipResponse(**s.to_dict()) for s in payslips]
    p_dict = payroll_run.to_dict()
    p_dict["payslips"] = res_slips
    return PayrollRunResponse(**p_dict)

@app.get("/hr/payroll/payslips/{emp_id}", response_model=List[PayslipResponse])
def get_employee_payslips(emp_id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    slips = db.query(Payslip).filter_by(employee_id=emp_id, org_id=user_ctx.org_id).all()
    return [PayslipResponse(**s.to_dict()) for s in slips]

# ----------------------------------------------------
# 5. Employees & Analytics Endpoints (Defined before {id})
# ----------------------------------------------------
@app.get("/hr/analytics/headcount", response_model=HRHeadcountAnalyticsResponse)
def get_headcount_analytics(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    employees = db.query(Employee).filter_by(org_id=user_ctx.org_id).all()
    active_count = sum(1 for e in employees if e.status == "Active")
    depts_count = db.query(Department).filter_by(org_id=user_ctx.org_id).count()
    total_salary = sum(e.salary_annual for e in employees if e.status == "Active")
    avg_salary = (total_salary / active_count) if active_count > 0 else 0.0

    return HRHeadcountAnalyticsResponse(
        total_headcount=len(employees),
        active_employees=active_count,
        departments_count=depts_count,
        total_annual_payroll_commitment=round(total_salary, 2),
        average_salary=round(avg_salary, 2)
    )

@app.get("/hr/employees", response_model=List[EmployeeResponse])
def list_employees(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    employees = db.query(Employee).filter_by(org_id=user_ctx.org_id).all()
    return [EmployeeResponse(**e.to_dict()) for e in employees]

@app.post("/hr/employees", response_model=EmployeeResponse)
def create_employee(req: EmployeeCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    emp = Employee(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        user_id=req.user_id,
        first_name=req.first_name,
        last_name=req.last_name,
        email=req.email,
        phone=req.phone,
        department_id=req.department_id,
        job_title=req.job_title,
        hire_date=req.hire_date or "2026-09-24",
        employment_type=req.employment_type or "Full-Time",
        salary_annual=req.salary_annual,
        status="Active"
    )
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return EmployeeResponse(**emp.to_dict())

@app.get("/hr/employees/{id}", response_model=EmployeeResponse)
def get_employee(id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    emp = db.query(Employee).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return EmployeeResponse(**emp.to_dict())
