import uuid
from sqlalchemy.orm import Session
from services.projects_service.models import Project, Sprint, Task, TimeEntry

def seed_projects_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds active client delivery projects, sprints, tasks, and agile boards."""
    if session.query(Project).filter_by(org_id=org_id).first():
        return

    # 1. Projects
    p1 = Project(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Nexus Robotics Fleet Navigation OS",
        code="ROBO-01",
        client_name="Nexus Robotics Systems",
        description="Autonomous mission control and real-time obstacle avoidance software stack.",
        status="Active",
        budget=450000.0,
        spent_amount=112000.0,
        start_date="2026-09-01",
        target_end_date="2027-03-31",
        manager="Marcus Chen"
    )
    p2 = Project(
        id=str(uuid.uuid4()),
        org_id=org_id,
        name="Quantum Cloud Security Gateway",
        code="QSC-02",
        client_name="Quantum Dynamics Corp",
        description="Zero-trust post-quantum cryptographic protocol layer for cloud microservices.",
        status="Active",
        budget=250000.0,
        spent_amount=45000.0,
        start_date="2026-08-15",
        target_end_date="2027-01-30",
        manager="Elena Rostova"
    )
    session.add_all([p1, p2])
    session.flush()

    # 2. Sprints
    s1 = Sprint(
        id=str(uuid.uuid4()),
        org_id=org_id,
        project_id=p1.id,
        name="Sprint 14 — Core Telemetry Integration",
        goal="Deliver resilient WebSocket telemetry and sub-second fleet routing.",
        status="Active",
        start_date="2026-09-15",
        end_date="2026-09-29"
    )
    s2 = Sprint(
        id=str(uuid.uuid4()),
        org_id=org_id,
        project_id=p1.id,
        name="Sprint 15 — Mission Control Webhooks",
        goal="Integrate event dispatch for battery health and geofence alerts.",
        status="Planned",
        start_date="2026-09-30",
        end_date="2026-10-14"
    )
    session.add_all([s1, s2])
    session.flush()

    # 3. Tasks
    t1 = Task(
        id=str(uuid.uuid4()),
        org_id=org_id,
        project_id=p1.id,
        sprint_id=s1.id,
        task_key="ROBO-101",
        title="Implement failover heartbeat daemon",
        description="Keep-alive ping with 200ms threshold for fleet rovers.",
        status="In progress",
        priority="High",
        issue_type="Task",
        estimate_hours=16.0,
        logged_hours=10.0,
        assignee="Marcus Chen"
    )
    t2 = Task(
        id=str(uuid.uuid4()),
        org_id=org_id,
        project_id=p1.id,
        sprint_id=s1.id,
        task_key="ROBO-102",
        title="Fix LiDAR point cloud memory buffer leak",
        description="Profile circular buffer allocator under 60fps sensor feeds.",
        status="Blocked",
        priority="Critical",
        issue_type="Bug",
        estimate_hours=8.0,
        logged_hours=4.0,
        assignee="Elena Rostova"
    )
    t3 = Task(
        id=str(uuid.uuid4()),
        org_id=org_id,
        project_id=p1.id,
        sprint_id=s1.id,
        task_key="ROBO-103",
        title="End-to-end telemetry encryption audit",
        description="Verify TLS 1.3 mutual auth between rovers and edge relays.",
        status="Ready for review",
        priority="Medium",
        issue_type="Story",
        estimate_hours=12.0,
        logged_hours=12.0,
        assignee="Sarah Connor"
    )
    t4 = Task(
        id=str(uuid.uuid4()),
        org_id=org_id,
        project_id=p1.id,
        sprint_id=s1.id,
        task_key="ROBO-104",
        title="Sub-millisecond ROS2 bridge benchmarks",
        description="Validate publish/subscribe latency under high network jitter.",
        status="Done",
        priority="High",
        issue_type="Task",
        estimate_hours=20.0,
        logged_hours=18.0,
        assignee="Marcus Chen"
    )
    session.add_all([t1, t2, t3, t4])
    session.flush()

    # 4. Time Entry
    te1 = TimeEntry(
        id=str(uuid.uuid4()),
        org_id=org_id,
        task_id=t1.id,
        user_id="usr-dev-002",
        user_name="Marcus Chen",
        hours=5.0,
        date="2026-09-23",
        notes="Configured UDP socket retry loop for rover telemetry.",
        is_billable=True
    )
    session.add(te1)
    session.commit()
