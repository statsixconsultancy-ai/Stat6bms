import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

# ----------------------------------------------------
# 00. Multi-Tenancy & Identity
# ----------------------------------------------------
class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    industry = Column(String(100), default="Technology")
    currency = Column(String(10), default="USD")
    timezone = Column(String(50), default="UTC")
    created_at = Column(DateTime, default=datetime.utcnow)

class User(Base):
    __tablename__ = "users"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="admin") # admin, manager, employee, customer, vendor
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    actor_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    actor_name = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(36), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# ----------------------------------------------------
# 01. Sales & CRM
# ----------------------------------------------------
class Company(Base):
    __tablename__ = "companies"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True)
    industry = Column(String(100), nullable=True)
    annual_revenue = Column(Float, default=0.0)
    employee_count = Column(Integer, default=0)
    city = Column(String(100), nullable=True)
    country = Column(String(100), default="USA")
    created_at = Column(DateTime, default=datetime.utcnow)

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    job_title = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Lead(Base):
    __tablename__ = "leads"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    title = Column(String(255), nullable=False)
    company_name = Column(String(255), nullable=True)
    contact_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    source = Column(String(100), default="Website") # Website, Referral, Ads, LinkedIn
    score = Column(Integer, default=50) # 0-100 lead score
    status = Column(String(50), default="New") # New, Contacted, Qualified, Disqualified, Converted
    estimated_value = Column(Float, default=0.0)
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Deal(Base):
    __tablename__ = "deals"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    title = Column(String(255), nullable=False)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=True)
    stage = Column(String(50), default="Qualified") # New, Contacted, Qualified, Proposal, Negotiation, Won, Lost
    amount = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    probability = Column(Integer, default=50) # 0-100%
    expected_close_date = Column(DateTime, nullable=True)
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Quote(Base):
    __tablename__ = "quotes"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    deal_id = Column(String(36), ForeignKey("deals.id"), nullable=True)
    quote_number = Column(String(50), nullable=False)
    client_name = Column(String(255), nullable=False)
    total_amount = Column(Float, default=0.0)
    status = Column(String(50), default="Draft") # Draft, Sent, Accepted, Rejected
    valid_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ----------------------------------------------------
# 02. Marketing
# ----------------------------------------------------
class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    channel = Column(String(50), default="Email") # Email, SMS, WhatsApp, Social, Ads
    status = Column(String(50), default="Active") # Draft, Scheduled, Active, Completed
    budget = Column(Float, default=0.0)
    spent = Column(Float, default=0.0)
    leads_generated = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    roi_percentage = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class LandingPage(Base):
    __tablename__ = "landing_pages"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    title = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False)
    views = Column(Integer, default=0)
    submissions = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ----------------------------------------------------
# 03. Projects & Operations
# ----------------------------------------------------
class Project(Base):
    __tablename__ = "projects"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    deal_id = Column(String(36), ForeignKey("deals.id"), nullable=True)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="In Progress") # Planning, In Progress, On Hold, Completed
    health = Column(String(20), default="Good") # Good, At Risk, Critical
    budget = Column(Float, default=0.0)
    actual_cost = Column(Float, default=0.0)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    manager_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String(20), default="Medium") # Low, Medium, High, Urgent
    status = Column(String(50), default="To Do") # Backlog, To Do, In Progress, Review, Done
    estimated_hours = Column(Float, default=0.0)
    actual_hours = Column(Float, default=0.0)
    due_date = Column(DateTime, nullable=True)
    assignee_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ----------------------------------------------------
# 04. HR & People Management
# ----------------------------------------------------
class Department(Base):
    __tablename__ = "departments"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)
    head_id = Column(String(36), nullable=True)

class Employee(Base):
    __tablename__ = "employees"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    employee_code = Column(String(50), unique=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    department = Column(String(100), default="Engineering")
    role_title = Column(String(100), nullable=False)
    salary = Column(Float, default=0.0)
    join_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="Active") # Active, On Leave, Resigned
    attendance_rate = Column(Float, default=96.5)

class LeaveRequest(Base):
    __tablename__ = "leave_requests"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    employee_id = Column(String(36), ForeignKey("employees.id"), nullable=False)
    employee_name = Column(String(255), nullable=False)
    leave_type = Column(String(50), default="Annual") # Annual, Sick, Casual, Unpaid
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    days = Column(Integer, default=1)
    status = Column(String(50), default="Pending") # Pending, Approved, Rejected
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ----------------------------------------------------
# 05. Finance & Accounting
# ----------------------------------------------------
class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    invoice_number = Column(String(50), nullable=False)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    client_name = Column(String(255), nullable=False)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)
    amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    status = Column(String(50), default="Draft") # Draft, Sent, Paid, Overdue, Cancelled
    due_date = Column(DateTime, nullable=False)
    paid_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Expense(Base):
    __tablename__ = "expenses"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    category = Column(String(100), default="Software") # Software, Travel, Office, Marketing, Legal
    title = Column(String(255), nullable=False)
    amount = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    spent_by = Column(String(255), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="Approved") # Pending, Approved, Reimbursed

# ----------------------------------------------------
# 06. Inventory & Asset Management
# ----------------------------------------------------
class Product(Base):
    __tablename__ = "products"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    sku = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default="Hardware")
    price = Column(Float, default=0.0)
    cost = Column(Float, default=0.0)
    stock_quantity = Column(Integer, default=0)
    reorder_level = Column(Integer, default=10)
    warehouse = Column(String(100), default="Main Warehouse")
    barcode = Column(String(100), nullable=True)

class AssetItem(Base):
    __tablename__ = "assets"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    asset_tag = Column(String(100), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), default="IT Equipment") # Laptop, Server, Vehicle, Furniture
    assigned_to = Column(String(255), nullable=True)
    purchase_cost = Column(Float, default=0.0)
    status = Column(String(50), default="In Use") # Purchased, In Use, Maintenance, Retired

# ----------------------------------------------------
# 07. Procurement & Vendor Management
# ----------------------------------------------------
class Vendor(Base):
    __tablename__ = "vendors"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    contact_email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    rating = Column(Float, default=4.5) # 1.0 - 5.0
    category = Column(String(100), default="Cloud Infrastructure")
    payment_terms = Column(String(50), default="Net 30")

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    po_number = Column(String(50), nullable=False)
    vendor_name = Column(String(255), nullable=False)
    total_amount = Column(Float, default=0.0)
    status = Column(String(50), default="Draft") # Draft, Awaiting Approval, Approved, Received, Paid
    delivery_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ----------------------------------------------------
# 08. Customer Support
# ----------------------------------------------------
class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    ticket_number = Column(String(50), nullable=False)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    priority = Column(String(20), default="Medium") # Low, Medium, High, Urgent
    status = Column(String(50), default="New") # New, Assigned, Investigation, Resolved, Closed
    assigned_agent = Column(String(255), default="Support Team")
    sla_hours_remaining = Column(Float, default=8.0)
    created_at = Column(DateTime, default=datetime.utcnow)

# ----------------------------------------------------
# 10. Collaboration & Communication
# ----------------------------------------------------
class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    channel = Column(String(50), default="general") # general, sales, tech, random
    sender_name = Column(String(100), nullable=False)
    sender_role = Column(String(50), default="Team")
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# ----------------------------------------------------
# 12. Automation & Workflow
# ----------------------------------------------------
class WorkflowRule(Base):
    __tablename__ = "workflow_rules"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(255), nullable=False)
    trigger_event = Column(String(100), nullable=False) # deal.won, invoice.overdue, task.completed, ticket.created
    condition_expr = Column(String(255), default="always")
    action_type = Column(String(100), nullable=False) # send_email, create_project, notify_slack, webhook
    action_target = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    executions_count = Column(Integer, default=0)

# ----------------------------------------------------
# 13. AI & Business Intelligence
# ----------------------------------------------------
class AIInsight(Base):
    __tablename__ = "ai_insights"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    category = Column(String(50), default="Revenue") # Revenue, Churn, Cost, Productivity
    title = Column(String(255), nullable=False)
    recommendation = Column(Text, nullable=False)
    impact_score = Column(String(20), default="High") # Low, Medium, High
    created_at = Column(DateTime, default=datetime.utcnow)

# ----------------------------------------------------
# 14. Settings & Module Toggles
# ----------------------------------------------------
class ModuleConfig(Base):
    __tablename__ = "module_configs"
    id = Column(String(36), primary_key=True, default=generate_uuid)
    org_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    module_key = Column(String(50), nullable=False) # crm, marketing, projects, hr, finance, inventory, procurement, support, automation, ai
    is_enabled = Column(Boolean, default=True)
