from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database import get_db, init_db
from app.seed import seed_database
from app.models import (
    Organization, User, Company, Contact, Lead, Deal, Quote,
    Campaign, LandingPage, Project, Task, Employee, LeaveRequest,
    Invoice, Expense, Product, AssetItem, Vendor, PurchaseOrder,
    SupportTicket, ChatMessage, WorkflowRule, AIInsight, ModuleConfig, AuditLog
)

app = FastAPI(
    title="BMS Platform API - Business Management System",
    description="Unified API for the Next-Gen Business Operating System competing with Zoho One",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    seed_database()

# ----------------------------------------------------
# 00. Overview & Metrics Cockpit
# ----------------------------------------------------
@app.get("/api/v1/overview")
def get_executive_overview(db: Session = Depends(get_db)):
    deals = db.query(Deal).all()
    invoices = db.query(Invoice).all()
    projects = db.query(Project).all()
    tickets = db.query(SupportTicket).all()
    employees = db.query(Employee).all()
    
    total_pipeline = sum(d.amount for d in deals if d.stage != "Lost")
    total_revenue_paid = sum(i.total_amount for i in invoices if i.status == "Paid")
    overdue_receivables = sum(i.total_amount for i in invoices if i.status == "Overdue")
    open_tickets = len([t for t in tickets if t.status not in ["Resolved", "Closed"]])
    active_projects = len([p for p in projects if p.status == "In Progress"])
    
    return {
        "kpis": {
            "total_revenue_paid": total_revenue_paid,
            "total_pipeline": total_pipeline,
            "overdue_receivables": overdue_receivables,
            "active_projects": active_projects,
            "open_tickets": open_tickets,
            "total_employees": len(employees),
            "customer_count": db.query(Company).count()
        },
        "recent_audit": [
            {
                "id": a.id,
                "actor": a.actor_name,
                "action": a.action,
                "resource": a.resource_type,
                "timestamp": a.timestamp.isoformat() if a.timestamp else ""
            }
            for a in db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(5).all()
        ]
    }

# ----------------------------------------------------
# 01. Sales & CRM
# ----------------------------------------------------
@app.get("/api/v1/crm/deals")
def get_deals(db: Session = Depends(get_db)):
    deals = db.query(Deal).all()
    companies = {c.id: c.name for c in db.query(Company).all()}
    return [
        {
            "id": d.id,
            "title": d.title,
            "company_name": companies.get(d.company_id, "Unknown"),
            "stage": d.stage,
            "amount": d.amount,
            "currency": d.currency,
            "probability": d.probability,
            "expected_close_date": d.expected_close_date.isoformat() if d.expected_close_date else None
        }
        for d in deals
    ]

@app.get("/api/v1/crm/leads")
def get_leads(db: Session = Depends(get_db)):
    return [
        {
            "id": l.id,
            "title": l.title,
            "company": l.company_name,
            "contact": l.contact_name,
            "email": l.email,
            "source": l.source,
            "score": l.score,
            "status": l.status,
            "estimated_value": l.estimated_value
        }
        for l in db.query(Lead).all()
    ]

@app.get("/api/v1/crm/companies")
def get_companies(db: Session = Depends(get_db)):
    return [
        {
            "id": c.id,
            "name": c.name,
            "domain": c.domain,
            "industry": c.industry,
            "annual_revenue": c.annual_revenue,
            "employee_count": c.employee_count,
            "city": c.city
        }
        for c in db.query(Company).all()
    ]

@app.get("/api/v1/crm/contacts")
def get_contacts(db: Session = Depends(get_db)):
    companies = {c.id: c.name for c in db.query(Company).all()}
    return [
        {
            "id": ct.id,
            "name": f"{ct.first_name} {ct.last_name}",
            "email": ct.email,
            "phone": ct.phone,
            "job_title": ct.job_title,
            "company_name": companies.get(ct.company_id, "Direct Client")
        }
        for ct in db.query(Contact).all()
    ]

# ----------------------------------------------------
# 02. Marketing
# ----------------------------------------------------
@app.get("/api/v1/marketing")
def get_marketing(db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).all()
    landing_pages = db.query(LandingPage).all()
    return {
        "campaigns": [
            {
                "id": c.id,
                "name": c.name,
                "channel": c.channel,
                "status": c.status,
                "budget": c.budget,
                "spent": c.spent,
                "leads": c.leads_generated,
                "conversions": c.conversions,
                "roi": c.roi_percentage
            }
            for c in campaigns
        ],
        "landing_pages": [
            {
                "id": lp.id,
                "title": lp.title,
                "slug": lp.slug,
                "views": lp.views,
                "submissions": lp.submissions,
                "conversion_rate": round((lp.submissions / lp.views * 100), 1) if lp.views else 0
            }
            for lp in landing_pages
        ]
    }

# ----------------------------------------------------
# 03. Projects & Operations
# ----------------------------------------------------
@app.get("/api/v1/projects")
def get_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    tasks = db.query(Task).all()
    companies = {c.id: c.name for c in db.query(Company).all()}
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "client": companies.get(p.company_id, "Internal"),
            "status": p.status,
            "health": p.health,
            "budget": p.budget,
            "actual_cost": p.actual_cost,
            "task_count": len([t for t in tasks if t.project_id == p.id]),
            "tasks_completed": len([t for t in tasks if t.project_id == p.id and t.status == "Done"])
        }
        for p in projects
    ]

@app.get("/api/v1/projects/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(Task).all()
    projects = {p.id: p.name for p in db.query(Project).all()}
    return [
        {
            "id": t.id,
            "title": t.title,
            "project_name": projects.get(t.project_id, "General"),
            "priority": t.priority,
            "status": t.status,
            "estimated_hours": t.estimated_hours,
            "actual_hours": t.actual_hours,
            "due_date": t.due_date.isoformat() if t.due_date else None
        }
        for t in tasks
    ]

# ----------------------------------------------------
# 04. HR & People Management
# ----------------------------------------------------
@app.get("/api/v1/hr")
def get_hr(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    leaves = db.query(LeaveRequest).all()
    return {
        "employees": [
            {
                "id": e.id,
                "code": e.employee_code,
                "name": e.full_name,
                "department": e.department,
                "role": e.role_title,
                "salary": e.salary,
                "attendance": e.attendance_rate,
                "status": e.status
            }
            for e in employees
        ],
        "leave_requests": [
            {
                "id": l.id,
                "employee": l.employee_name,
                "type": l.leave_type,
                "days": l.days,
                "status": l.status,
                "reason": l.reason,
                "start_date": l.start_date.strftime("%b %d, %Y")
            }
            for l in leaves
        ]
    }

# ----------------------------------------------------
# 05. Finance & Accounting
# ----------------------------------------------------
@app.get("/api/v1/finance")
def get_finance(db: Session = Depends(get_db)):
    invoices = db.query(Invoice).all()
    expenses = db.query(Expense).all()
    
    total_invoiced = sum(i.total_amount for i in invoices)
    total_expenses = sum(e.amount for e in expenses)
    net_profit = sum(i.total_amount for i in invoices if i.status == "Paid") - total_expenses
    
    return {
        "summary": {
            "total_invoiced": total_invoiced,
            "total_expenses": total_expenses,
            "net_profit": net_profit
        },
        "invoices": [
            {
                "id": i.id,
                "number": i.invoice_number,
                "client": i.client_name,
                "amount": i.amount,
                "tax": i.tax_amount,
                "total": i.total_amount,
                "status": i.status,
                "due_date": i.due_date.strftime("%b %d, %Y")
            }
            for i in invoices
        ],
        "expenses": [
            {
                "id": e.id,
                "title": e.title,
                "category": e.category,
                "amount": e.amount,
                "spent_by": e.spent_by,
                "status": e.status
            }
            for e in expenses
        ]
    }

# ----------------------------------------------------
# 06. Inventory & Assets
# ----------------------------------------------------
@app.get("/api/v1/inventory")
def get_inventory(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    assets = db.query(AssetItem).all()
    return {
        "products": [
            {
                "id": p.id,
                "sku": p.sku,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "stock": p.stock_quantity,
                "reorder_level": p.reorder_level,
                "warehouse": p.warehouse,
                "is_low_stock": p.stock_quantity <= p.reorder_level
            }
            for p in products
        ],
        "assets": [
            {
                "id": a.id,
                "tag": a.asset_tag,
                "name": a.name,
                "category": a.category,
                "assigned_to": a.assigned_to,
                "cost": a.purchase_cost,
                "status": a.status
            }
            for a in assets
        ]
    }

# ----------------------------------------------------
# 07. Procurement & Vendors
# ----------------------------------------------------
@app.get("/api/v1/procurement")
def get_procurement(db: Session = Depends(get_db)):
    vendors = db.query(Vendor).all()
    pos = db.query(PurchaseOrder).all()
    return {
        "vendors": [
            {
                "id": v.id,
                "name": v.name,
                "email": v.contact_email,
                "phone": v.phone,
                "category": v.category,
                "rating": v.rating,
                "terms": v.payment_terms
            }
            for v in vendors
        ],
        "purchase_orders": [
            {
                "id": po.id,
                "po_number": po.po_number,
                "vendor": po.vendor_name,
                "total": po.total_amount,
                "status": po.status,
                "delivery_date": po.delivery_date.strftime("%b %d, %Y") if po.delivery_date else "TBD"
            }
            for po in pos
        ]
    }

# ----------------------------------------------------
# 08. Customer Support
# ----------------------------------------------------
@app.get("/api/v1/support")
def get_support(db: Session = Depends(get_db)):
    tickets = db.query(SupportTicket).all()
    return [
        {
            "id": t.id,
            "number": t.ticket_number,
            "customer": t.customer_name,
            "email": t.customer_email,
            "subject": t.subject,
            "priority": t.priority,
            "status": t.status,
            "agent": t.assigned_agent,
            "sla_hours": t.sla_hours_remaining
        }
        for t in tickets
    ]

# ----------------------------------------------------
# 10. Collaboration & Chat
# ----------------------------------------------------
@app.get("/api/v1/collaboration/messages")
def get_chat_messages(channel: str = "general", db: Session = Depends(get_db)):
    messages = db.query(ChatMessage).filter(ChatMessage.channel == channel).all()
    return [
        {
            "id": m.id,
            "sender": m.sender_name,
            "role": m.sender_role,
            "message": m.message,
            "timestamp": m.created_at.strftime("%I:%M %p")
        }
        for m in messages
    ]

# ----------------------------------------------------
# 12. Automation & Workflow
# ----------------------------------------------------
@app.get("/api/v1/automation")
def get_automations(db: Session = Depends(get_db)):
    rules = db.query(WorkflowRule).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "trigger": r.trigger_event,
            "condition": r.condition_expr,
            "action": r.action_type,
            "target": r.action_target,
            "is_active": r.is_active,
            "executions": r.executions_count
        }
        for r in rules
    ]

# ----------------------------------------------------
# 13. AI & Insights
# ----------------------------------------------------
@app.get("/api/v1/ai/insights")
def get_ai_insights(db: Session = Depends(get_db)):
    insights = db.query(AIInsight).all()
    return [
        {
            "id": i.id,
            "category": i.category,
            "title": i.title,
            "recommendation": i.recommendation,
            "impact": i.impact_score
        }
        for i in insights
    ]

@app.post("/api/v1/ai/copilot")
def query_copilot(query: dict, db: Session = Depends(get_db)):
    user_prompt = query.get("prompt", "").lower()
    
    # Cross-domain tool-calling intelligence simulation across the unified business graph:
    if "overdue" in user_prompt or "invoice" in user_prompt:
        overdue_invoices = db.query(Invoice).filter(Invoice.status == "Overdue").all()
        details = [f"{i.invoice_number} ({i.client_name}: ${i.total_amount:,.2f})" for i in overdue_invoices]
        return {
            "response": f"I analyzed our unified financial graph. Found {len(overdue_invoices)} overdue invoice(s):\n• " + "\n• ".join(details) + "\n\nStarlight BioHealth's invoice is 6 days overdue. Because Starlight has an active support ticket (#TK-1084), I recommend sending our automated polite reconciliation link rather than a stern notice.",
            "actions": [{"label": "Send 1-Click Reminder", "action": "send_reminder", "target": "INV-2026-003"}]
        }
    elif "deal" in user_prompt or "pipeline" in user_prompt or "sales" in user_prompt:
        deals = db.query(Deal).all()
        won = [d for d in deals if d.stage == "Won"]
        active = [d for d in deals if d.stage not in ["Won", "Lost"]]
        return {
            "response": f"Current Sales Pipeline status:\n• Active Deals: {len(active)} totaling ${sum(d.amount for d in active):,.2f}\n• Recently Closed (Won): {len(won)} totaling ${sum(d.amount for d in won):,.2f}\n• Largest in flight: 'Global Route Optimization Engine' ($210,000.00 with Vanguard Logistics at 60% probability).",
            "actions": [{"label": "View Sales Board", "action": "navigate_crm"}]
        }
    elif "stock" in user_prompt or "inventory" in user_prompt:
        low_stock = db.query(Product).filter(Product.stock_quantity <= Product.reorder_level).all()
        return {
            "response": f"Inventory Telemetry Alert: Found {len(low_stock)} product below threshold:\n• {low_stock[0].name} (SKU: {low_stock[0].sku}) has only {low_stock[0].stock_quantity} units remaining (Minimum threshold: {low_stock[0].reorder_level}).\nWith current order velocity, stockout projected in 9 days.",
            "actions": [{"label": "Generate PO to Arrow Electronics", "action": "create_po", "sku": "IOT-HUB-v2"}]
        }
    else:
        return {
            "response": "I am the BMS Autonomous Copilot. I have full unified visibility across CRM, Finance, Projects, HR, Inventory, Support, and Operations. You can ask me cross-departmental questions like:\n- 'Show me overdue invoices for clients with open tickets'\n- 'What is our current pipeline velocity?'\n- 'Which inventory items are at risk of stockout?'",
            "actions": []
        }

# ----------------------------------------------------
# Universal Global Omnisearch (Ctrl+K)
# ----------------------------------------------------
@app.get("/api/v1/search")
def universal_search(q: str = Query("", min_length=1), db: Session = Depends(get_db)):
    results = []
    query_str = f"%{q}%"
    
    # Search Deals
    for d in db.query(Deal).filter(Deal.title.like(query_str)).limit(3).all():
        results.append({"type": "Deal", "title": d.title, "subtitle": f"${d.amount:,.0f} • {d.stage}", "category": "Sales & CRM"})
        
    # Search Companies
    for c in db.query(Company).filter(Company.name.like(query_str)).limit(3).all():
        results.append({"type": "Company", "title": c.name, "subtitle": f"{c.industry} • {c.city}", "category": "Accounts"})
        
    # Search Invoices
    for i in db.query(Invoice).filter(Invoice.invoice_number.like(query_str) | Invoice.client_name.like(query_str)).limit(3).all():
        results.append({"type": "Invoice", "title": i.invoice_number, "subtitle": f"{i.client_name} • ${i.total_amount:,.2f} ({i.status})", "category": "Finance"})
        
    # Search Projects
    for p in db.query(Project).filter(Project.name.like(query_str)).limit(3).all():
        results.append({"type": "Project", "title": p.name, "subtitle": f"Status: {p.status} • Health: {p.health}", "category": "Projects"})
        
    # Search Employees
    for e in db.query(Employee).filter(Employee.full_name.like(query_str) | Employee.department.like(query_str)).limit(3).all():
        results.append({"type": "Employee", "title": e.full_name, "subtitle": f"{e.role_title} • {e.department}", "category": "HR & People"})

    # Search Support Tickets
    for t in db.query(SupportTicket).filter(SupportTicket.subject.like(query_str) | SupportTicket.ticket_number.like(query_str)).limit(3).all():
        results.append({"type": "Ticket", "title": t.ticket_number, "subtitle": f"{t.subject} ({t.priority})", "category": "Support"})
        
    return results
