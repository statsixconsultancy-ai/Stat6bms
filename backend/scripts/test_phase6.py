#!/usr/bin/env python3
"""
Test Suite for Phase 6: Project Operations & Jira Agile Microservice
Validates project delivery, sprints, Jira-style Kanban task moves,
worklogs with budget tracking, burndown metrics, and automated provisioning on 'deal.won'.
"""
import os
import sys
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.projects_service.main import app as projects_app, on_startup

# Ensure tables and seed data
on_startup()
client = TestClient(projects_app)

def test_projects_health():
    print("[1/6] Testing Projects Microservice Health Endpoint...")
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "projects-service"
    assert data["status"] == "UP"
    assert data["port"] == 8004
    print("  [OK] Projects Service /health endpoint validated successfully.")

def test_list_projects():
    print("[2/6] Testing Projects Directory Listing...")
    resp = client.get("/projects")
    assert resp.status_code == 200
    projects = resp.json()
    assert len(projects) >= 2
    codes = [p["code"] for p in projects]
    assert "ROBO-01" in codes
    print(f"  [OK] Listed {len(projects)} active projects, verified code 'ROBO-01'.")
    return projects[0]["id"]

def test_kanban_task_move():
    print("[3/6] Testing Jira Agile Board Kanban Transitions (/projects/tasks/{id}/move)...")
    # 1. Fetch existing tasks
    tasks_resp = client.get("/projects/tasks")
    assert tasks_resp.status_code == 200
    tasks = tasks_resp.json()
    assert len(tasks) >= 1
    
    # Ensure at least one task is in 'Ready for review'
    matching = [t for t in tasks if t["status"] == "Ready for review"]
    if matching:
        task_to_move = matching[0]
    else:
        # Reset the first task to 'Ready for review'
        client.patch(f"/projects/tasks/{tasks[0]['id']}/move", json={"status": "Ready for review"})
        tasks = client.get("/projects/tasks").json()
        task_to_move = [t for t in tasks if t["status"] == "Ready for review"][0]
    task_id = task_to_move["id"]

    # 2. Transition to 'Done'
    move_resp = client.patch(f"/projects/tasks/{task_id}/move", json={"status": "Done"})
    assert move_resp.status_code == 200
    updated = move_resp.json()
    assert updated["status"] == "Done"

    # 3. Test invalid status rejection
    bad_resp = client.patch(f"/projects/tasks/{task_id}/move", json={"status": "Floating"})
    assert bad_resp.status_code == 400
    print("  [OK] Task moved to 'Done' on Kanban board, invalid transitions strictly rejected.")
    return task_id, task_to_move["project_id"]

def test_worklog_hours_and_budget_impact(task_id: str, project_id: str):
    print("[4/6] Testing Worklog Logging & Dynamic Project Budget Spend...")
    # Get project spend before logging
    prj_before = client.get(f"/projects/{project_id}").json()
    spend_before = prj_before["spent_amount"]

    # Log 4.0 billable hours
    log_payload = {
        "hours": 4.0,
        "date": "2026-09-24",
        "notes": "Benchmarked UDP socket packet loss at 10,000 req/sec.",
        "is_billable": True
    }
    log_resp = client.post(f"/projects/tasks/{task_id}/worklog", json=log_payload)
    assert log_resp.status_code == 200
    entry = log_resp.json()
    assert entry["hours"] == 4.0

    # Verify project spend incremented by 4.0 * 150 = $600
    prj_after = client.get(f"/projects/{project_id}").json()
    spend_after = prj_after["spent_amount"]
    assert spend_after == spend_before + 600.0
    print(f"  [OK] 4.0 hours logged. Project budget spend updated: ${spend_before:,.2f} -> ${spend_after:,.2f}.")

def test_sprint_burndown(project_id: str):
    print("[5/6] Testing Sprint Burndown Analytics & Agile Velocity...")
    resp = client.get(f"/projects/{project_id}/burndown")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_tasks"] >= 4
    assert data["completion_rate_percent"] > 0
    assert data["total_estimate_hours"] > 0
    assert data["total_logged_hours"] > 0
    print(f"  [OK] Burndown calculated: {data['done_tasks']}/{data['total_tasks']} tasks completed ({data['completion_rate_percent']}%), {data['total_logged_hours']} hrs logged.")

def test_deal_won_auto_provisioning():
    print("[6/6] Testing Automated Project Provisioning on 'deal.won' Event...")
    deal_event = {
        "event_name": "deal.won",
        "payload": {
            "deal_id": "DEAL-TITAN-88",
            "title": "Titan AI Server Fleet Integration",
            "amount": 550000.0,
            "company_name": "Titan Supercomputing Inc"
        },
        "org_id": "org-acroflow-main"
    }
    resp = client.post("/webhooks/events", json=deal_event)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "project_provisioned"
    new_project_id = data["project_id"]

    # Verify project exists
    p_resp = client.get(f"/projects/{new_project_id}")
    assert p_resp.status_code == 200
    proj = p_resp.json()
    assert proj["budget"] == 550000.0
    assert proj["client_name"] == "Titan Supercomputing Inc"

    # Verify Sprint 1 was auto-provisioned
    sprint_resp = client.get(f"/projects/{new_project_id}/sprints")
    assert sprint_resp.status_code == 200
    sprints = sprint_resp.json()
    assert len(sprints) >= 1
    assert "Sprint 1" in sprints[0]["name"]
    print("  [OK] 'deal.won' event automatically provisioned client project workspace and initial sprint.")

def main():
    print("=" * 65)
    print("  BMS PHASE 6: PROJECTS & JIRA AGILE MICROSERVICE TEST SUITE")
    print("=" * 65)
    test_projects_health()
    _ = test_list_projects()
    task_id, project_id = test_kanban_task_move()
    test_worklog_hours_and_budget_impact(task_id, project_id)
    test_sprint_burndown(project_id)
    test_deal_won_auto_provisioning()
    print("=" * 65)
    print("  ALL PHASE 6 AUTOMATED TESTS PASSED SUCCESSFULLY! (6/6)")
    print("=" * 65)

if __name__ == "__main__":
    main()
