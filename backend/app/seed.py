from datetime import datetime, timedelta
from app.database import SessionLocal, init_db
from app.models import (
    Organization, User, AuditLog, Company, Contact, Lead, Deal, Quote,
    Campaign, LandingPage, Project, Task, Department, Employee, LeaveRequest,
    Invoice, Expense, Product, AssetItem, Vendor, PurchaseOrder, SupportTicket,
    ChatMessage, WorkflowRule, AIInsight, ModuleConfig
)

def seed_database():
    init_db()
    db = SessionLocal()
    
    # Check if already seeded
    existing_org = db.query(Organization).first()
    if existing_org:
        print("Database already seeded.")
        db.close()
        return existing_org.id

    print("Seeding full BMS enterprise business graph...")

    # 0. Organization
    org = Organization(
        name="AcroFlow Global Systems",
        slug="acroflow",
        industry="Enterprise AI & Cloud Infrastructure",
        currency="USD",
        timezone="America/New_York"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    org_id = org.id

    # Users
    admin_user = User(
        org_id=org_id,
        email="prann@acroflow.io",
        full_name="Prann (Founder & CEO)",
        role="admin",
        avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
    )
    sales_vp = User(
        org_id=org_id,
        email="elena@acroflow.io",
        full_name="Elena Rostova (VP of Sales)",
        role="manager",
        avatar_url="https://images.unsplash.com/photo-1580489944761-15a19d654956?w=150"
    )
    tech_head = User(
        org_id=org_id,
        email="marcus@acroflow.io",
        full_name="Marcus Chen (Head of Product & Eng)",
        role="manager",
        avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
    )
    db.add_all([admin_user, sales_vp, tech_head])
    db.commit()

    # Module Toggles
    modules = ["crm", "marketing", "projects", "hr", "finance", "inventory", "procurement", "support", "collaboration", "compliance", "automation", "ai", "analytics", "settings"]
    for m in modules:
        db.add(ModuleConfig(org_id=org_id, module_key=m, is_enabled=True))
    db.commit()

    # 1. Companies & Contacts (CRM)
    c1 = Company(
        org_id=org_id,
        name="Nexus Robotics Corp",
        domain="nexusrobotics.ai",
        industry="Autonomous Robotics",
        annual_revenue=48000000.0,
        employee_count=280,
        city="San Francisco",
        country="USA"
    )
    c2 = Company(
        org_id=org_id,
        name="Starlight BioHealth",
        domain="starlightbio.com",
        industry="Biotech & Healthcare",
        annual_revenue=14500000.0,
        employee_count=95,
        city="Boston",
        country="USA"
    )
    c3 = Company(
        org_id=org_id,
        name="Vanguard Logistics",
        domain="vanguardlogistics.global",
        industry="Supply Chain",
        annual_revenue=120000000.0,
        employee_count=1200,
        city="Chicago",
        country="USA"
    )
    c4 = Company(
        org_id=org_id,
        name="Apex Cloud Infrastructure",
        domain="apexcloud.net",
        industry="Cloud Hosting & DevOps",
        annual_revenue=32000000.0,
        employee_count=190,
        city="Seattle",
        country="USA"
    )
    db.add_all([c1, c2, c3, c4])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)
    db.refresh(c3)
    db.refresh(c4)

    # Contacts
    ct1 = Contact(org_id=org_id, company_id=c1.id, first_name="Arthur", last_name="Pendelton", email="arthur@nexusrobotics.ai", phone="+1 (415) 882-9011", job_title="Chief Technology Officer")
    ct2 = Contact(org_id=org_id, company_id=c2.id, first_name="Dr. Aris", last_name="Thorne", email="athorne@starlightbio.com", phone="+1 (617) 554-1022", job_title="VP of Clinical Ops")
    ct3 = Contact(org_id=org_id, company_id=c3.id, first_name="Claire", last_name="Underwood", email="claire@vanguardlogistics.global", phone="+1 (312) 440-9831", job_title="Global Fleet Director")
    ct4 = Contact(org_id=org_id, company_id=c4.id, first_name="Sarah", last_name="Jenkins", email="sjenkins@apexcloud.net", phone="+1 (206) 779-3320", job_title="Head of SecOps")
    db.add_all([ct1, ct2, ct3, ct4])

    # Leads
    l1 = Lead(org_id=org_id, title="Enterprise AI Fleet Integration", company_name="CyberMotion Dynamics", contact_name="Evelyn Cross", email="evelyn@cybermotion.io", source="LinkedIn Ads", score=92, status="Qualified", estimated_value=85000.0)
    l2 = Lead(org_id=org_id, title="Multi-tenant ERP Migration", company_name="Orion Retail Group", contact_name="David Vance", email="vance@orionretail.com", source="Website Form", score=74, status="New", estimated_value=45000.0)
    l3 = Lead(org_id=org_id, title="Telemetry Data Pipeline Audit", company_name="Horizon Aerospace", contact_name="Garrison Croft", email="garrison@horizon-aero.com", source="Referral", score=88, status="Contacted", estimated_value=120000.0)
    db.add_all([l1, l2, l3])

    # Deals across Stages (Demonstrating Unified Business Graph continuity)
    d1 = Deal(org_id=org_id, title="Autonomous Warehouse AI Fleet", company_id=c1.id, contact_id=ct1.id, stage="Won", amount=145000.0, probability=100, expected_close_date=datetime.utcnow() - timedelta(days=5))
    d2 = Deal(org_id=org_id, title="Clinical Data Ingestion Pipeline", company_id=c2.id, contact_id=ct2.id, stage="Negotiation", amount=85000.0, probability=80, expected_close_date=datetime.utcnow() + timedelta(days=12))
    d3 = Deal(org_id=org_id, title="Global Route Optimization Engine", company_id=c3.id, contact_id=ct3.id, stage="Proposal", amount=210000.0, probability=60, expected_close_date=datetime.utcnow() + timedelta(days=25))
    d4 = Deal(org_id=org_id, title="Zero-Trust Security & Multi-Cloud Portal", company_id=c4.id, contact_id=ct4.id, stage="Qualified", amount=65000.0, probability=45, expected_close_date=datetime.utcnow() + timedelta(days=40))
    d5 = Deal(org_id=org_id, title="Predictive Maintenance Edge Sensor Pilot", company_id=c1.id, contact_id=ct1.id, stage="Contacted", amount=35000.0, probability=25, expected_close_date=datetime.utcnow() + timedelta(days=60))
    d6 = Deal(org_id=org_id, title="Automated Regulatory Compliance Dashboard", company_id=c2.id, contact_id=ct2.id, stage="New", amount=40000.0, probability=15, expected_close_date=datetime.utcnow() + timedelta(days=90))
    db.add_all([d1, d2, d3, d4, d5, d6])
    db.commit()
    db.refresh(d1)

    # Quotes
    q1 = Quote(org_id=org_id, deal_id=d1.id, quote_number="QUO-2026-081", client_name="Nexus Robotics Corp", total_amount=145000.0, status="Accepted", valid_until=datetime.utcnow() + timedelta(days=30))
    q2 = Quote(org_id=org_id, deal_id=d2.id, quote_number="QUO-2026-082", client_name="Starlight BioHealth", total_amount=85000.0, status="Sent", valid_until=datetime.utcnow() + timedelta(days=15))
    db.add_all([q1, q2])

    # 2. Marketing
    m1 = Campaign(org_id=org_id, name="Q1 Global Enterprise Cloud Summit", channel="Email & Social", status="Active", budget=25000.0, spent=16400.0, leads_generated=142, conversions=18, roi_percentage=340.5)
    m2 = Campaign(org_id=org_id, name="AI Workflow Automation Webinar", channel="Webinar & Ads", status="Active", budget=12000.0, spent=8900.0, leads_generated=98, conversions=11, roi_percentage=285.0)
    lp1 = LandingPage(org_id=org_id, title="Next-Gen Business Operating System", slug="bms-enterprise-platform", views=3840, submissions=412, is_published=True)
    db.add_all([m1, m2, lp1])

    # 3. Projects & Operations (Linked to Deal Won d1!)
    p1 = Project(org_id=org_id, deal_id=d1.id, company_id=c1.id, name="Warehouse AI Fleet Deployment", status="In Progress", health="Good", budget=145000.0, actual_cost=42000.0, start_date=datetime.utcnow() - timedelta(days=10), end_date=datetime.utcnow() + timedelta(days=50))
    p2 = Project(org_id=org_id, company_id=c4.id, name="Cloud Architecture Hardening & SOC2", status="Planning", health="Good", budget=65000.0, actual_cost=8500.0, start_date=datetime.utcnow() + timedelta(days=5), end_date=datetime.utcnow() + timedelta(days=45))
    db.add_all([p1, p2])
    db.commit()
    db.refresh(p1)

    t1 = Task(org_id=org_id, project_id=p1.id, title="Telemetry Ingestion Gateway & Broker Setup", priority="High", status="Done", estimated_hours=40, actual_hours=36)
    t2 = Task(org_id=org_id, project_id=p1.id, title="Computer Vision Sensor Fleet Calibration", priority="Urgent", status="In Progress", estimated_hours=60, actual_hours=28, due_date=datetime.utcnow() + timedelta(days=4))
    t3 = Task(org_id=org_id, project_id=p1.id, title="Integration testing with Nexus WMS API", priority="Medium", status="To Do", estimated_hours=32, actual_hours=0, due_date=datetime.utcnow() + timedelta(days=14))
    t4 = Task(org_id=org_id, project_id=p1.id, title="Security vulnerability & penetration testing", priority="High", status="Backlog", estimated_hours=24, actual_hours=0)
    db.add_all([t1, t2, t3, t4])

    # 4. HR & People
    dept1 = Department(org_id=org_id, name="Engineering")
    dept2 = Department(org_id=org_id, name="Sales & Solutions")
    dept3 = Department(org_id=org_id, name="Customer Operations")
    db.add_all([dept1, dept2, dept3])

    e1 = Employee(org_id=org_id, employee_code="EMP-1001", full_name="Marcus Chen", department="Engineering", role_title="Principal Architect", salary=175000.0, attendance_rate=98.8, status="Active")
    e2 = Employee(org_id=org_id, employee_code="EMP-1002", full_name="Elena Rostova", department="Sales & Solutions", role_title="VP Sales", salary=160000.0, attendance_rate=97.4, status="Active")
    e3 = Employee(org_id=org_id, employee_code="EMP-1003", full_name="Sophia Patel", department="Finance", role_title="Finance Director", salary=145000.0, attendance_rate=99.2, status="Active")
    e4 = Employee(org_id=org_id, employee_code="EMP-1004", full_name="David Kim", department="Customer Operations", role_title="Senior Support Engineer", salary=105000.0, attendance_rate=96.1, status="Active")
    e5 = Employee(org_id=org_id, employee_code="EMP-1005", full_name="Aaliyah Davis", department="Engineering", role_title="Fullstack React/Node Engineer", salary=130000.0, attendance_rate=97.9, status="Active")
    db.add_all([e1, e2, e3, e4, e5])
    db.commit()

    lr1 = LeaveRequest(org_id=org_id, employee_id=e5.id, employee_name="Aaliyah Davis", leave_type="Annual", start_date=datetime.utcnow() + timedelta(days=10), end_date=datetime.utcnow() + timedelta(days=14), days=4, status="Pending", reason="Family vacation")
    db.add(lr1)

    # 5. Finance & Accounting (Linked to Nexus Robotics d1!)
    inv1 = Invoice(org_id=org_id, invoice_number="INV-2026-001", company_id=c1.id, client_name="Nexus Robotics Corp", project_id=p1.id, amount=72500.0, tax_amount=7250.0, total_amount=79750.0, status="Paid", due_date=datetime.utcnow() - timedelta(days=2), paid_date=datetime.utcnow() - timedelta(days=1))
    inv2 = Invoice(org_id=org_id, invoice_number="INV-2026-002", company_id=c1.id, client_name="Nexus Robotics Corp", project_id=p1.id, amount=72500.0, tax_amount=7250.0, total_amount=79750.0, status="Sent", due_date=datetime.utcnow() + timedelta(days=28))
    inv3 = Invoice(org_id=org_id, invoice_number="INV-2026-003", company_id=c2.id, client_name="Starlight BioHealth", amount=25000.0, tax_amount=2500.0, total_amount=27500.0, status="Overdue", due_date=datetime.utcnow() - timedelta(days=6))
    db.add_all([inv1, inv2, inv3])

    exp1 = Expense(org_id=org_id, category="Software & Cloud", title="AWS Multi-Region Dedicated GPU Cluster", amount=8450.0, spent_by="Marcus Chen", status="Approved")
    exp2 = Expense(org_id=org_id, category="Travel & Client", title="Executive Client Onsite - Nexus Robotics SF", amount=1820.0, spent_by="Elena Rostova", status="Approved")
    exp3 = Expense(org_id=org_id, category="Hardware Dev", title="Precision Telemetry Sensor Prototyping Kits", amount=3150.0, spent_by="Aaliyah Davis", status="Pending")
    db.add_all([exp1, exp2, exp3])

    # 6. Inventory & Assets
    prod1 = Product(org_id=org_id, sku="HW-EDGE-900", name="Autonomous Edge AI Compute Server", category="Edge Hardware", price=4500.0, cost=2800.0, stock_quantity=48, reorder_level=12, warehouse="San Francisco Facility")
    prod2 = Product(org_id=org_id, sku="IOT-HUB-v2", name="Industrial Optical Sensor Node (Sub-mm)", category="IoT Sensors", price=620.0, cost=340.0, stock_quantity=7, reorder_level=20, warehouse="Chicago Logistics Hub", barcode="793847291032") # Low stock alert!
    prod3 = Product(org_id=org_id, sku="CAB-OPT-100", name="Armored Fiber Patch Cable 100m", category="Cabling", price=85.0, cost=35.0, stock_quantity=240, reorder_level=30, warehouse="Main Warehouse")
    db.add_all([prod1, prod2, prod3])

    ast1 = AssetItem(org_id=org_id, asset_tag="AST-2026-01", name="Apple MacBook Pro 16\" M3 Max (64GB)", category="IT Equipment", assigned_to="Marcus Chen", purchase_cost=3999.0, status="In Use")
    ast2 = AssetItem(org_id=org_id, asset_tag="AST-2026-02", name="Tektronix High-Bandwidth Digital Oscilloscope", category="Laboratory Equipment", assigned_to="Hardware Lab", purchase_cost=12500.0, status="In Use")
    db.add_all([ast1, ast2])

    # 7. Procurement & Vendors
    v1 = Vendor(org_id=org_id, name="NVIDIA Enterprise Solutions", contact_email="orders@nvidia.com", phone="+1 (408) 486-2000", rating=4.9, category="Compute & Silicon", payment_terms="Net 45")
    v2 = Vendor(org_id=org_id, name="Arrow Electronics Distribution", contact_email="sales@arrow.com", phone="+1 (800) 777-2776", rating=4.6, category="Passive Components", payment_terms="Net 30")
    db.add_all([v1, v2])

    po1 = PurchaseOrder(org_id=org_id, po_number="PO-2026-019", vendor_name="NVIDIA Enterprise Solutions", total_amount=38400.0, status="Approved", delivery_date=datetime.utcnow() + timedelta(days=18))
    po2 = PurchaseOrder(org_id=org_id, po_number="PO-2026-020", vendor_name="Arrow Electronics Distribution", total_amount=6800.0, status="Draft", delivery_date=datetime.utcnow() + timedelta(days=10))
    db.add_all([po1, po2])

    # 8. Customer Support
    st1 = SupportTicket(org_id=org_id, ticket_number="TK-1082", company_id=c4.id, customer_name="Sarah Jenkins", customer_email="sjenkins@apexcloud.net", subject="Latency degradation on EU-Central gateway cluster", priority="High", status="Investigation", assigned_agent="David Kim", sla_hours_remaining=3.2)
    st2 = SupportTicket(org_id=org_id, ticket_number="TK-1083", company_id=c1.id, customer_name="Arthur Pendelton", customer_email="arthur@nexusrobotics.ai", subject="Request for additional staging API rate-limit allocation", priority="Medium", status="Assigned", assigned_agent="David Kim", sla_hours_remaining=6.5)
    st3 = SupportTicket(org_id=org_id, ticket_number="TK-1084", company_id=c2.id, customer_name="Dr. Aris Thorne", customer_email="athorne@starlightbio.com", subject="Exported audit reports missing secondary timestamp column", priority="Low", status="Resolved", assigned_agent="David Kim", sla_hours_remaining=0.0)
    db.add_all([st1, st2, st3])

    # 10. Collaboration
    cm1 = ChatMessage(org_id=org_id, channel="general", sender_name="Prann (Founder)", sender_role="CEO", message="Fantastic execution team! We just officially marked the Nexus Robotics $145k enterprise agreement as WON. Invoicing and deployment are synchronized!")
    cm2 = ChatMessage(org_id=org_id, channel="general", sender_name="Elena Rostova", sender_role="VP Sales", message="Kudos to the solutions engineering crew for turning around the telemetry architecture proof in record time.")
    cm3 = ChatMessage(org_id=org_id, channel="engineering", sender_name="Marcus Chen", sender_role="Head of Eng", message="Sprint 44 telemetry gateway deployed with sub-5ms P99 latency. Ready for Nexus sensor fleet integration.")
    db.add_all([cm1, cm2, cm3])

    # 12. Automation Rules (Visual WHEN-IF-DO)
    ar1 = WorkflowRule(org_id=org_id, name="Deal Won -> Auto-Provision Deployment Project & 50% Deposit Invoice", trigger_event="deal.won", condition_expr="amount >= 50000", action_type="create_project_and_invoice", action_target="Finance & Projects", is_active=True, executions_count=14)
    ar2 = WorkflowRule(org_id=org_id, name="Overdue Invoice > 5 Days Escalation", trigger_event="invoice.overdue", condition_expr="days_overdue >= 5", action_type="send_whatsapp_and_slack_alert", action_target="Account Executive", is_active=True, executions_count=3)
    ar3 = WorkflowRule(org_id=org_id, name="Low Inventory Auto-Purchase Requisition", trigger_event="inventory.stock_low", condition_expr="stock_quantity <= reorder_level", action_type="create_purchase_requisition", action_target="Procurement", is_active=True, executions_count=8)
    db.add_all([ar1, ar2, ar3])

    # 13. AI Insights
    ai1 = AIInsight(org_id=org_id, category="Revenue", title="Cash Collection Anomaly: Starlight BioHealth", recommendation="Invoice #INV-2026-003 ($27,500) is 6 days overdue. Starlight typically pays within 2 days of receiving their clinical grant disbursement on the 28th. Recommended action: Trigger payment reminder with automated reconciliation link.", impact_score="High")
    ai2 = AIInsight(org_id=org_id, category="Sales Velocity", title="Deal Acceleration Opportunity: Vanguard Logistics", recommendation="Vanguard Logistics deal ($210,000) has spent 8 days in 'Proposal'. Deals of this size with logistics firms close 3.2x faster when an interactive SLA calculator is included. Auto-generated quote appendix ready for review.", impact_score="High")
    ai3 = AIInsight(org_id=org_id, category="Inventory Risk", title="Critical Stockout Warning: Industrial Optical Sensor Hubs", recommendation="SKU IOT-HUB-v2 has only 7 units remaining (reorder threshold is 20). With 2 pending deals requiring 25 units total, stockout projected in 9 days. Supplier lead time is 6 days. Recommended action: 1-Click PO generation with Arrow Electronics.", impact_score="Critical")
    db.add_all([ai1, ai2, ai3])

    # Audit Log
    db.add(AuditLog(org_id=org_id, actor_name="Prann", action="DEAL_STAGE_CHANGE", resource_type="Deal", resource_id=d1.id, details={"from": "Negotiation", "to": "Won", "amount": 145000.0}))
    db.add(AuditLog(org_id=org_id, actor_name="System Automation", action="INVOICE_GENERATED", resource_type="Invoice", resource_id=inv1.id, details={"rule": "Deal Won -> Auto-Provision", "invoice_number": "INV-2026-001"}))

    db.commit()
    print("Database seeding completed successfully.")
    db.close()
    return org_id

if __name__ == "__main__":
    seed_database()
