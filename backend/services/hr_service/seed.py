import uuid
from sqlalchemy.orm import Session
from services.hr_service.models import Department, Employee, AttendanceLog, LeaveRequest

def seed_hr_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds departments, executive team employees, attendance logs, and leave requests."""
    if session.query(Department).filter_by(org_id=org_id).first():
        return

    # 1. Departments
    d1 = Department(id=str(uuid.uuid4()), org_id=org_id, name="Engineering & Infrastructure", code="ENG", manager_name="Marcus Chen")
    d2 = Department(id=str(uuid.uuid4()), org_id=org_id, name="Product & AI Research", code="RND", manager_name="Dr. Eleanor Vance")
    d3 = Department(id=str(uuid.uuid4()), org_id=org_id, name="Global Commercial Sales", code="SALES", manager_name="Sarah Connor")
    d4 = Department(id=str(uuid.uuid4()), org_id=org_id, name="People Operations & Talent", code="OPS", manager_name="Elena Rostova")
    session.add_all([d1, d2, d3, d4])
    session.flush()

    # 2. Employees
    e1 = Employee(
        id=str(uuid.uuid4()),
        org_id=org_id,
        user_id="usr-dev-002",
        first_name="Marcus",
        last_name="Chen",
        email="marcus.chen@acroflow.enterprise",
        phone="+1 (555) 301-8811",
        department_id=d1.id,
        job_title="Principal Systems Architect",
        hire_date="2024-03-01",
        employment_type="Full-Time",
        salary_annual=180000.0,
        status="Active"
    )
    e2 = Employee(
        id=str(uuid.uuid4()),
        org_id=org_id,
        user_id="usr-dev-001",
        first_name="Eleanor",
        last_name="Vance",
        email="eleanor.vance@acroflow.enterprise",
        phone="+1 (555) 301-8822",
        department_id=d2.id,
        job_title="VP of Autonomous Intelligence",
        hire_date="2023-11-15",
        employment_type="Full-Time",
        salary_annual=210000.0,
        status="Active"
    )
    e3 = Employee(
        id=str(uuid.uuid4()),
        org_id=org_id,
        first_name="Sarah",
        last_name="Connor",
        email="sarah.connor@acroflow.enterprise",
        phone="+1 (555) 301-8833",
        department_id=d3.id,
        job_title="VP of Commercial Engagements",
        hire_date="2024-01-10",
        employment_type="Full-Time",
        salary_annual=165000.0,
        status="Active"
    )
    e4 = Employee(
        id=str(uuid.uuid4()),
        org_id=org_id,
        user_id="usr-dev-003",
        first_name="Elena",
        last_name="Rostova",
        email="elena.rostova@acroflow.enterprise",
        phone="+1 (555) 301-8844",
        department_id=d4.id,
        job_title="Head of Operations & Culture",
        hire_date="2024-02-01",
        employment_type="Full-Time",
        salary_annual=155000.0,
        status="Active"
    )
    session.add_all([e1, e2, e3, e4])
    session.flush()

    # 3. Attendance
    a1 = AttendanceLog(
        id=str(uuid.uuid4()),
        org_id=org_id,
        employee_id=e1.id,
        date="2026-09-24",
        clock_in="08:45 AM",
        clock_out="05:15 PM",
        work_hours=8.5,
        status="Present"
    )
    a2 = AttendanceLog(
        id=str(uuid.uuid4()),
        org_id=org_id,
        employee_id=e2.id,
        date="2026-09-24",
        clock_in="09:00 AM",
        clock_out="05:00 PM",
        work_hours=8.0,
        status="Present"
    )
    session.add_all([a1, a2])

    # 4. Leave Request
    lr = LeaveRequest(
        id=str(uuid.uuid4()),
        org_id=org_id,
        employee_id=e1.id,
        leave_type="Annual",
        start_date="2026-10-15",
        end_date="2026-10-16",
        days_count=2,
        reason="Family trip.",
        status="Approved",
        reviewer_notes="Approved by Elena Rostova."
    )
    session.add(lr)
    session.commit()
