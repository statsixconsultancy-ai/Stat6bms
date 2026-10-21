import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class Department(TenantModel):
    __tablename__ = "hr_departments"

    name = Column(String(100), nullable=False, unique=True, index=True)
    code = Column(String(50), nullable=False, unique=True)
    manager_name = Column(String(255), default="Department Head")

    employees = relationship("Employee", back_populates="department")

class Employee(TenantModel):
    __tablename__ = "hr_employees"

    user_id = Column(String(255), nullable=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=True)
    department_id = Column(String(36), ForeignKey("hr_departments.id"), nullable=True, index=True)
    job_title = Column(String(100), nullable=False)
    hire_date = Column(String(50), nullable=True)
    employment_type = Column(String(50), default="Full-Time")  # Full-Time, Contract, Part-Time
    salary_annual = Column(Float, default=120000.0)
    status = Column(String(50), default="Active", index=True)  # Active, On Leave, Terminated
    manager_id = Column(String(36), nullable=True)

    department = relationship("Department", back_populates="employees")
    attendance_logs = relationship("AttendanceLog", back_populates="employee", cascade="all, delete-orphan")
    leave_requests = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan")
    payslips = relationship("Payslip", back_populates="employee", cascade="all, delete-orphan")

class AttendanceLog(TenantModel):
    __tablename__ = "hr_attendance_logs"

    employee_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=False, index=True)
    date = Column(String(50), nullable=False, index=True)
    clock_in = Column(String(50), nullable=True)
    clock_out = Column(String(50), nullable=True)
    work_hours = Column(Float, default=0.0)
    status = Column(String(50), default="Present")  # Present, Late, Half-Day
    ip_address = Column(String(50), default="127.0.0.1")
    geofence_verified = Column(Boolean, default=True)

    employee = relationship("Employee", back_populates="attendance_logs")

class LeaveRequest(TenantModel):
    __tablename__ = "hr_leave_requests"

    employee_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=False, index=True)
    leave_type = Column(String(50), default="Annual")  # Annual, Sick, Maternity, Unpaid
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=False)
    days_count = Column(Integer, default=1)
    reason = Column(Text, nullable=True)
    status = Column(String(50), default="Pending", index=True)  # Pending, Approved, Rejected
    reviewer_notes = Column(Text, nullable=True)

    employee = relationship("Employee", back_populates="leave_requests")

class PayrollRun(TenantModel):
    __tablename__ = "hr_payroll_runs"

    period_name = Column(String(100), nullable=False)  # e.g., "September 2026"
    period_start = Column(String(50), nullable=True)
    period_end = Column(String(50), nullable=True)
    total_gross = Column(Float, default=0.0)
    total_tax = Column(Float, default=0.0)
    total_net = Column(Float, default=0.0)
    employees_count = Column(Integer, default=0)
    status = Column(String(50), default="Completed")  # Completed, Processing

    payslips = relationship("Payslip", back_populates="payroll_run", cascade="all, delete-orphan")

class Payslip(TenantModel):
    __tablename__ = "hr_payslips"

    payroll_run_id = Column(String(36), ForeignKey("hr_payroll_runs.id"), nullable=False, index=True)
    employee_id = Column(String(36), ForeignKey("hr_employees.id"), nullable=False, index=True)
    basic_salary = Column(Float, nullable=False)
    allowances = Column(Float, default=0.0)
    gross_pay = Column(Float, nullable=False)
    pf_deduction = Column(Float, default=0.0)
    esi_deduction = Column(Float, default=0.0)
    professional_tax = Column(Float, default=200.0)
    tds_tax = Column(Float, default=0.0)
    tax_deduction = Column(Float, default=0.0)
    net_pay = Column(Float, nullable=False)
    status = Column(String(50), default="Paid")

    payroll_run = relationship("PayrollRun", back_populates="payslips")
    employee = relationship("Employee", back_populates="payslips")

class OKR(TenantModel):
    __tablename__ = "hr_okrs"

    title = Column(String(255), nullable=False, index=True)
    owner_id = Column(String(255), nullable=False, index=True)
    quarter = Column(String(50), default="Q4-2026", index=True)
    progress_percent = Column(Float, default=0.0)
    status = Column(String(50), default="On_Track", index=True)  # On_Track, At_Risk, Completed
    key_results = Column(Text, default="[]")  # JSON string of KRs

class JobOpening(TenantModel):
    __tablename__ = "hr_job_openings"

    title = Column(String(255), nullable=False, index=True)
    department_id = Column(String(36), nullable=True, index=True)
    positions_count = Column(Integer, default=1)
    status = Column(String(50), default="Active", index=True)  # Active, Closed, Draft
    min_experience_years = Column(Integer, default=3)

class Candidate(TenantModel):
    __tablename__ = "hr_candidates"

    job_opening_id = Column(String(36), nullable=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    stage = Column(String(50), default="Screening", index=True)  # Screening, Interview, Offer, Hired
    rating = Column(Float, default=4.0)
    resume_url = Column(String(255), nullable=True)
    converted_employee_id = Column(String(36), nullable=True)

