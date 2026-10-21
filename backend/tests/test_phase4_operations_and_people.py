import os
import sys
import unittest
import json
import uuid
from datetime import datetime
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.projects_service.main import app as projects_app
from services.hr_service.main import app as hr_app

class TestPhase4OperationsAndPeople(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prj_client = TestClient(projects_app)
        cls.hr_client = TestClient(hr_app)
        cls.headers = {
            "x-user-id": "usr-ops-001",
            "x-org-id": "org-stat6-ops-test",
            "x-user-role": "admin",
            "x-user-email": "ops-lead@stat6.enterprise"
        }

    # =========================================================================
    # 1. Projects & Professional Services Automation (PSA) Tests
    # =========================================================================
    def test_01_project_and_sprint_creation(self):
        p_code = f"PRJ-{uuid.uuid4().hex[:6].upper()}"
        proj_resp = self.prj_client.post("/projects", json={
            "name": "Cloud Native Data Modernization",
            "code": p_code,
            "client_name": "Apex Global Bank",
            "budget": 150000.0,
            "start_date": "2026-10-01",
            "target_end_date": "2026-12-31",
            "manager": "Lead Architect Alex"
        }, headers=self.headers)
        self.assertEqual(proj_resp.status_code, 200)
        proj = proj_resp.json()
        proj_id = proj["id"]
        self.assertEqual(proj["code"], p_code)

        # Create Sprint
        sprint_resp = self.prj_client.post("/projects/sprints", json={
            "project_id": proj_id,
            "name": "Sprint 1 - Foundation & Schema Design",
            "goal": "Finalize multi-tenant PostgreSQL schemas and identity federation"
        }, headers=self.headers)
        self.assertEqual(sprint_resp.status_code, 200)
        sprint = sprint_resp.json()
        self.assertEqual(sprint["status"], "Active")

    def test_02_task_creation_and_dependencies(self):
        # Create Project
        p_code = f"PRJ-{uuid.uuid4().hex[:6].upper()}"
        proj_resp = self.prj_client.post("/projects", json={
            "name": "Core Platform Refactoring",
            "code": p_code,
            "budget": 75000.0
        }, headers=self.headers)
        self.assertEqual(proj_resp.status_code, 200)
        proj = proj_resp.json()
        proj_id = proj["id"]

        # Task 1: API Design
        t1_key = f"{p_code}-01"
        t1_resp = self.prj_client.post("/projects/tasks", json={
            "project_id": proj_id,
            "task_key": t1_key,
            "title": "Design REST & Event Schemas",
            "estimate_hours": 16.0,
            "assignee": "Lead Engineer"
        }, headers=self.headers)
        self.assertEqual(t1_resp.status_code, 200)

        # Task 2: Service Implementation (depends on Task 1)
        t2_key = f"{p_code}-02"
        t2_resp = self.prj_client.post("/projects/tasks", json={
            "project_id": proj_id,
            "task_key": t2_key,
            "title": "Implement Microservice Business Logic",
            "estimate_hours": 32.0,
            "assignee": "Backend Developer"
        }, headers=self.headers)
        self.assertEqual(t2_resp.status_code, 200)
        t2 = t2_resp.json()
        self.assertEqual(t2["task_key"], t2_key)

    def test_03_critical_path_method_calculation(self):
        # Create Project with sequential tasks
        p_code = f"PRJ-CPM-{uuid.uuid4().hex[:6].upper()}"
        proj = self.prj_client.post("/projects", json={
            "name": "Critical Infrastructure Deployment",
            "code": p_code
        }, headers=self.headers).json()
        proj_id = proj["id"]

        self.prj_client.post("/projects/tasks", json={
            "project_id": proj_id,
            "task_key": f"{p_code}-10",
            "title": "Hardware Provisioning",
            "estimate_hours": 24.0
        }, headers=self.headers)

        self.prj_client.post("/projects/tasks", json={
            "project_id": proj_id,
            "task_key": f"{p_code}-20",
            "title": "OS & Kubernetes Bootstrap",
            "estimate_hours": 16.0
        }, headers=self.headers)

        # Calculate Critical Path
        cpm_resp = self.prj_client.get(f"/projects/{proj_id}/critical-path", headers=self.headers)
        self.assertEqual(cpm_resp.status_code, 200)
        cpm = cpm_resp.json()
        self.assertEqual(cpm["project_id"], proj_id)
        self.assertGreater(cpm["project_duration_days"], 0)
        self.assertGreater(len(cpm["critical_path_tasks"]), 0)

    def test_04_sprint_burndown_and_story_points(self):
        p_code = f"PRJ-BD-{uuid.uuid4().hex[:6].upper()}"
        proj = self.prj_client.post("/projects", json={
            "name": "Agile Sprint Delivery",
            "code": p_code
        }, headers=self.headers).json()
        proj_id = proj["id"]

        t_resp = self.prj_client.post("/projects/tasks", json={
            "project_id": proj_id,
            "task_key": f"{p_code}-1",
            "title": "Authentication Microservice Integration",
            "estimate_hours": 12.0
        }, headers=self.headers)
        task_id = t_resp.json()["id"]

        # Move task to Done
        self.prj_client.post(f"/projects/tasks/{task_id}/move", json={"status": "Done"}, headers=self.headers)

        # Check Burndown
        bd_resp = self.prj_client.get(f"/projects/{proj_id}/burndown", headers=self.headers)
        self.assertEqual(bd_resp.status_code, 200)
        bd = bd_resp.json()
        self.assertEqual(bd["done_tasks"], 1)
        self.assertEqual(bd["completion_rate_percent"], 100.0)

    def test_05_psa_real_time_project_costing_and_margin(self):
        p_code = f"PRJ-PSA-{uuid.uuid4().hex[:6].upper()}"
        proj = self.prj_client.post("/projects", json={
            "name": "Cloud Transformation Advisory",
            "code": p_code,
            "budget": 100000.0
        }, headers=self.headers).json()
        proj_id = proj["id"]

        task = self.prj_client.post("/projects/tasks", json={
            "project_id": proj_id,
            "task_key": f"{p_code}-BILL",
            "title": "Architecture Assessment",
            "estimate_hours": 40.0
        }, headers=self.headers).json()

        # Log 40 billable hours
        self.prj_client.post(f"/projects/tasks/{task['id']}/worklog", json={
            "hours": 40.0,
            "date": "2026-10-14",
            "is_billable": True,
            "notes": "Completed initial high-level system analysis"
        }, headers=self.headers)

        # Get Financials
        fin_resp = self.prj_client.get(f"/projects/{proj_id}/financials", headers=self.headers)
        self.assertEqual(fin_resp.status_code, 200)
        fin = fin_resp.json()
        self.assertEqual(fin["total_billable_revenue"], 7000.0) # 40 hrs * $175
        self.assertEqual(fin["total_labor_cost"], 3400.0)      # 40 hrs * $85
        self.assertEqual(fin["net_profit"], 3600.0)
        self.assertAlmostEqual(fin["profit_margin_percent"], 51.4, places=1)

    def test_06_milestone_creation_and_completion_trigger(self):
        p_code = f"PRJ-MS-{uuid.uuid4().hex[:6].upper()}"
        proj = self.prj_client.post("/projects", json={
            "name": "Multi-Phase Core Banking Integration",
            "code": p_code
        }, headers=self.headers).json()
        proj_id = proj["id"]

        # Create Milestone
        ms_resp = self.prj_client.post(f"/projects/{proj_id}/milestones", json={
            "name": "Phase 1 - UAT Sign-off",
            "due_date": "2026-11-15",
            "amount": 45000.0
        }, headers=self.headers)
        self.assertEqual(ms_resp.status_code, 200)
        ms = ms_resp.json()
        ms_id = ms["id"]
        self.assertEqual(ms["status"], "Pending")

        # Complete Milestone
        comp_resp = self.prj_client.post(f"/projects/{proj_id}/milestones/{ms_id}/complete", headers=self.headers)
        self.assertEqual(comp_resp.status_code, 200)
        self.assertEqual(comp_resp.json()["status"], "Completed")

    # =========================================================================
    # 2. Human Resources & Payroll Engine Tests
    # =========================================================================
    def test_07_department_and_employee_onboarding(self):
        d_code = f"ENG-{int(datetime.utcnow().timestamp()) % 10000}"
        dept_resp = self.hr_client.post("/hr/departments", json={
            "name": f"Cloud Platforms {d_code}",
            "code": d_code,
            "manager_name": "CTO Robert Vance"
        }, headers=self.headers)
        self.assertEqual(dept_resp.status_code, 200)
        dept_id = dept_resp.json()["id"]

        # Onboard Employee
        emp_email = f"emp.{int(datetime.utcnow().timestamp()) % 10000}@stat6.test"
        emp_resp = self.hr_client.post("/hr/employees", json={
            "first_name": "Grace",
            "last_name": "Hopper",
            "email": emp_email,
            "department_id": dept_id,
            "job_title": "Principal Distributed Systems Engineer",
            "salary_annual": 185000.0,
            "employment_type": "Full-Time"
        }, headers=self.headers)
        self.assertEqual(emp_resp.status_code, 200)
        emp = emp_resp.json()
        self.assertEqual(emp["status"], "Active")
        self.assertEqual(emp["salary_annual"], 185000.0)

    def test_08_attendance_geofenced_clock_in_out(self):
        # Create employee
        emp = self.hr_client.post("/hr/employees", json={
            "first_name": "Nikola",
            "last_name": "Tesla",
            "email": f"tesla.{int(datetime.utcnow().timestamp()) % 10000}@stat6.test",
            "job_title": "Electrical Hardware Specialist",
            "salary_annual": 130000.0
        }, headers=self.headers).json()

        # Clock In with Geofence & IP
        cin_resp = self.hr_client.post("/hr/attendance/clock-in", json={
            "employee_id": emp["id"],
            "clock_in_time": "08:45 AM",
            "ip_address": "198.51.100.12",
            "latitude": 37.7749,
            "longitude": -122.4194
        }, headers=self.headers)
        self.assertEqual(cin_resp.status_code, 200)
        cin = cin_resp.json()
        self.assertEqual(cin["status"], "Present")
        self.assertEqual(cin["geofence_verified"], True)

        # Clock Out
        cout_resp = self.hr_client.post("/hr/attendance/clock-out", json={
            "employee_id": emp["id"],
            "clock_out_time": "05:15 PM"
        }, headers=self.headers)
        self.assertEqual(cout_resp.status_code, 200)
        self.assertEqual(cout_resp.json()["work_hours"], 8.0)

    def test_09_statutory_payroll_formula_engine(self):
        calc_req = {
            "basic_salary": 50000.0,
            "allowances": 25000.0
        }
        calc_resp = self.hr_client.post("/hr/payroll/calculate-statutory", json=calc_req)
        self.assertEqual(calc_resp.status_code, 200)
        calc = calc_resp.json()
        self.assertEqual(calc["gross_pay"], 75000.0)
        self.assertEqual(calc["pf_deduction"], 6000.0)      # 12% of 50000
        self.assertEqual(calc["professional_tax"], 200.0)   # 200 flat PT
        self.assertEqual(calc["tds_tax"], 7500.0)           # 10% of 75000 (> 50k)
        self.assertEqual(calc["total_deductions"], 13700.0) # 6000 + 200 + 7500
        self.assertEqual(calc["net_pay"], 61300.0)          # 75000 - 13700

    def test_10_leave_request_and_approval_workflow(self):
        emp = self.hr_client.post("/hr/employees", json={
            "first_name": "Katherine",
            "last_name": "Johnson",
            "email": f"katherine.{int(datetime.utcnow().timestamp()) % 10000}@stat6.test",
            "job_title": "Orbital Trajectory Analyst"
        }, headers=self.headers).json()

        # Submit Leave
        leave_resp = self.hr_client.post("/hr/leave", json={
            "employee_id": emp["id"],
            "leave_type": "Annual",
            "start_date": "2026-11-20",
            "end_date": "2026-11-25",
            "days_count": 5,
            "reason": "Family vacation"
        }, headers=self.headers)
        self.assertEqual(leave_resp.status_code, 200)
        leave = leave_resp.json()
        leave_id = leave["id"]
        self.assertEqual(leave["status"], "Pending")

        # Approve Leave
        dec_resp = self.hr_client.post(f"/hr/leave/{leave_id}/decision", json={
            "decision": "Approved",
            "reviewer_notes": "Approved by VP Engineering"
        }, headers=self.headers)
        self.assertEqual(dec_resp.status_code, 200)
        self.assertEqual(dec_resp.json()["status"], "Approved")

    def test_11_okr_objective_tracking_and_progress(self):
        # Create OKR
        okr_payload = {
            "title": "Achieve 99.999% SLA Uptime Across All 14 Microservices",
            "owner_id": "usr-infra-lead",
            "quarter": "Q4-2026",
            "key_results": '[{"kr": "Zero single-point-of-failure clusters", "target": 100}, {"kr": "Sub-50ms p99 latency", "target": 50}]'
        }
        create_resp = self.hr_client.post("/hr/okrs", json=okr_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        okr = create_resp.json()
        okr_id = okr["id"]
        self.assertEqual(okr["progress_percent"], 0.0)
        self.assertEqual(okr["status"], "On_Track")

        # Update Progress to 100%
        update_resp = self.hr_client.patch(f"/hr/okrs/{okr_id}", json={
            "progress_percent": 100.0
        }, headers=self.headers)
        self.assertEqual(update_resp.status_code, 200)
        self.assertEqual(update_resp.json()["status"], "Completed")

    def test_12_ats_recruitment_pipeline_and_conversion(self):
        # 1. Create Job Opening
        job_resp = self.hr_client.post("/hr/ats/openings", json={
            "title": "Senior Rust & Distributed Systems Engineer",
            "positions_count": 2,
            "min_experience_years": 5
        }, headers=self.headers)
        self.assertEqual(job_resp.status_code, 200)
        job_id = job_resp.json()["id"]

        # 2. Ingest Candidate
        cand_email = f"linus.{int(datetime.utcnow().timestamp()) % 10000}@kernel.test"
        cand_resp = self.hr_client.post("/hr/ats/candidates", json={
            "job_opening_id": job_id,
            "first_name": "Linus",
            "last_name": "Torvalds",
            "email": cand_email,
            "phone": "+1-555-019-9922",
            "resume_url": "https://storage.stat6.cloud/resumes/linus_cv.pdf"
        }, headers=self.headers)
        self.assertEqual(cand_resp.status_code, 200)
        cand = cand_resp.json()
        cand_id = cand["id"]
        self.assertEqual(cand["stage"], "Screening")

        # 3. Advance to Offer
        stage_resp = self.hr_client.patch(f"/hr/ats/candidates/{cand_id}/stage", json={
            "stage": "Offer"
        }, headers=self.headers)
        self.assertEqual(stage_resp.status_code, 200)
        self.assertEqual(stage_resp.json()["stage"], "Offer")

        # 4. 1-Click Convert Candidate to Employee
        conv_resp = self.hr_client.post(f"/hr/ats/candidates/{cand_id}/convert-to-employee", headers=self.headers)
        self.assertEqual(conv_resp.status_code, 200)
        emp = conv_resp.json()
        self.assertEqual(emp["email"], cand_email)
        self.assertEqual(emp["status"], "Active")

        # Check candidate record is marked Hired
        cand_check = self.hr_client.get("/hr/ats/candidates", headers=self.headers)
        c_item = [c for c in cand_check.json() if c["id"] == cand_id][0]
        self.assertEqual(c_item["stage"], "Hired")
        self.assertEqual(c_item["converted_employee_id"], emp["id"])

if __name__ == "__main__":
    unittest.main()
