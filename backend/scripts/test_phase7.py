#!/usr/bin/env python3
"""
Test Suite for Phase 7: People Operations — HR & Payroll Microservice
Validates departments, employee directory, attendance clock-ins,
leave approvals, and monthly automated payroll run with payslip generation.
"""
import os
import sys
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.hr_service.main import app as hr_app, on_startup

# Ensure tables and seed data
on_startup()
client = TestClient(hr_app)

def test_hr_health():
    print("[1/6] Testing HR Microservice Health Endpoint...")
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "hr-service"
    assert data["status"] == "UP"
    assert data["port"] == 8005
    print("  [OK] HR Service /health endpoint validated successfully.")

def test_headcount_analytics():
    print("[2/6] Testing Headcount & Compensation Analytics (/hr/analytics/headcount)...")
    depts_resp = client.get("/hr/departments")
    depts = depts_resp.json() if depts_resp.status_code == 200 else []
    if len(depts) < 4:
        dept_names = ["Engineering", "Product & Operations", "Sales & Marketing", "Finance & Legal"]
        for idx, dname in enumerate(dept_names):
            if idx >= len(depts):
                client.post("/hr/departments", json={"name": dname, "code": f"DPT-0{idx+1}", "manager_name": "Executive Head"})
        depts_resp = client.get("/hr/departments")
        depts = depts_resp.json()

    emps_resp = client.get("/hr/employees")
    emps = emps_resp.json() if emps_resp.status_code == 200 else []
    if len(emps) < 4:
        for idx in range(len(emps), 4):
            dept_id = depts[idx % len(depts)]["id"] if depts else None
            client.post("/hr/employees", json={
                "first_name": f"Staff{idx+1}",
                "last_name": "Member",
                "email": f"staff{idx+1}.test@acroflow.enterprise",
                "job_title": "Enterprise Specialist",
                "department_id": dept_id,
                "salary_annual": 125000.0
            })

    resp = client.get("/hr/analytics/headcount")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_headcount"] >= 4
    assert data["active_employees"] >= 4
    assert data["departments_count"] >= 4
    assert data["average_salary"] > 100000.0
    print(f"  [OK] Headcount: {data['total_headcount']} active employees | Avg Salary: ${data['average_salary']:,.2f} | Annual Payroll: ${data['total_annual_payroll_commitment']:,.2f}")

def test_departments_and_employees():
    print("[3/6] Testing Employee Directory & Department Mapping...")
    # List departments
    depts_resp = client.get("/hr/departments")
    assert depts_resp.status_code == 200
    depts = depts_resp.json()
    assert len(depts) >= 4
    dept_id = depts[0]["id"]

    # Provision new employee
    import uuid
    emp_email = f"tariq.mansoor.{uuid.uuid4().hex[:6]}@acroflow.enterprise"
    new_emp_payload = {
        "first_name": "Tariq",
        "last_name": "Al-Mansoor",
        "email": emp_email,
        "phone": "+1 (555) 301-9988",
        "department_id": dept_id,
        "job_title": "Senior Security Researcher",
        "salary_annual": 170000.0
    }
    create_resp = client.post("/hr/employees", json=new_emp_payload)
    assert create_resp.status_code == 200
    emp = create_resp.json()
    assert emp["email"] == emp_email
    assert emp["status"] == "Active"
    print(f"  [OK] Created employee {emp['first_name']} {emp['last_name']} in department {depts[0]['name']}.")
    return emp["id"]

def test_attendance_clock_in_out(emp_id: str):
    print("[4/6] Testing Attendance Clock-In & Clock-Out Workflow...")
    # Clock in
    cin_resp = client.post("/hr/attendance/clock-in", json={
        "employee_id": emp_id,
        "clock_in_time": "08:50 AM"
    })
    assert cin_resp.status_code == 200
    assert cin_resp.json()["clock_in"] == "08:50 AM"

    # Clock out
    cout_resp = client.post("/hr/attendance/clock-out", json={
        "employee_id": emp_id,
        "clock_out_time": "05:20 PM"
    })
    assert cout_resp.status_code == 200
    assert cout_resp.json()["work_hours"] == 8.0
    print("  [OK] Clock-in and clock-out cycles recorded successfully.")

def test_leave_request_workflow(emp_id: str):
    print("[5/6] Testing Leave Request Submission & Executive Approval...")
    leave_payload = {
        "employee_id": emp_id,
        "leave_type": "Sick",
        "start_date": "2026-10-01",
        "end_date": "2026-10-02",
        "days_count": 2,
        "reason": "Medical appointment and recovery."
    }
    req_resp = client.post("/hr/leave", json=leave_payload)
    assert req_resp.status_code == 200
    leave_data = req_resp.json()
    leave_id = leave_data["id"]
    assert leave_data["status"] == "Pending"

    # Decision approve
    dec_resp = client.post(f"/hr/leave/{leave_id}/decision", json={
        "decision": "Approved",
        "reviewer_notes": "Approved by Operations Leadership."
    })
    assert dec_resp.status_code == 200
    assert dec_resp.json()["status"] == "Approved"
    print("  [OK] Leave request approved with reviewer audit notes.")

def test_payroll_run_execution():
    print("[6/6] Testing Monthly Automated Payroll Run & Payslip Calculations...")
    run_payload = {
        "period_name": "September 2026",
        "period_start": "2026-09-01",
        "period_end": "2026-09-30"
    }
    resp = client.post("/hr/payroll/run", json=run_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["period_name"] == "September 2026"
    assert data["status"] == "Completed"
    assert data["employees_count"] >= 4
    assert data["total_gross"] > 0
    assert data["total_tax"] > 0
    assert data["total_net"] > 0
    assert round(data["total_gross"] - data["total_tax"], 2) == data["total_net"]
    assert len(data["payslips"]) == data["employees_count"]

    # Verify individual payslip formula: gross = basic + allowances, tax = gross * 0.20, net = gross - tax
    sample = data["payslips"][0]
    assert round(sample["basic_salary"] + sample["allowances"], 2) == sample["gross_pay"]
    assert round(sample["gross_pay"] * 0.20, 2) == sample["tax_deduction"]
    assert round(sample["gross_pay"] - sample["tax_deduction"], 2) == sample["net_pay"]

    print(f"  [OK] Payroll Run Completed: Gross ${data['total_gross']:,.2f} | Tax Withheld ${data['total_tax']:,.2f} | Net Disbursed ${data['total_net']:,.2f} ({data['employees_count']} payslips).")

def main():
    print("=" * 65)
    print("  BMS PHASE 7: HR & PAYROLL MICROSERVICE TEST SUITE")
    print("=" * 65)
    test_hr_health()
    test_headcount_analytics()
    emp_id = test_departments_and_employees()
    test_attendance_clock_in_out(emp_id)
    test_leave_request_workflow(emp_id)
    test_payroll_run_execution()
    print("=" * 65)
    print("  ALL PHASE 7 AUTOMATED TESTS PASSED SUCCESSFULLY! (6/6)")
    print("=" * 65)

if __name__ == "__main__":
    main()
