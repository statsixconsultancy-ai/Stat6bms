import os
import sys
import asyncio
from typing import Dict, List, Any, Optional
import httpx
from fastapi import FastAPI, Request, Response, HTTPException, Query, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.config import ServiceConfig, get_service_config
from common.security import (
    get_user_context,
    generate_gateway_signature,
    GATEWAY_SECRET
)
from common.middleware import setup_microservice_middleware

config = get_service_config("gateway", default_port=8000, db_filename="gateway.db")

app = FastAPI(
    title="BMS Unified API Gateway",
    description="Central Reverse Proxy, Auth Verifier, Event Broker & KPI Aggregator for all 14 BMS Microservices",
    version="2.0.0"
)

setup_microservice_middleware(app, "gateway", config.cors_origins)

# ----------------------------------------------------
# 1. Routing Table: Prefix -> Target Microservice Base URL
# ----------------------------------------------------
SERVICE_ROUTES: Dict[str, str] = {
    "auth": "http://127.0.0.1:8001",
    "crm": "http://127.0.0.1:8002",
    "marketing": "http://127.0.0.1:8003",
    "projects": "http://127.0.0.1:8004",
    "hr": "http://127.0.0.1:8005",
    "finance": "http://127.0.0.1:8006",
    "inventory": "http://127.0.0.1:8007",
    "procurement": "http://127.0.0.1:8008",
    "support": "http://127.0.0.1:8009",
    "chat": "http://127.0.0.1:8010",
    "collaboration": "http://127.0.0.1:8010",
    "compliance": "http://127.0.0.1:8011",
    "automation": "http://127.0.0.1:8012",
    "ai": "http://127.0.0.1:8013",
}

SERVICE_MODULE_PATHS: Dict[str, str] = {
    "auth": "services.auth_service.main",
    "crm": "services.crm_service.main",
    "marketing": "services.marketing_service.main",
    "projects": "services.projects_service.main",
    "hr": "services.hr_service.main",
    "finance": "services.finance_service.main",
    "inventory": "services.inventory_service.main",
    "procurement": "services.procurement_service.main",
    "support": "services.support_service.main",
    "chat": "services.collaboration_service.main",
    "collaboration": "services.collaboration_service.main",
    "compliance": "services.compliance_service.main",
    "automation": "services.automation_service.main",
    "ai": "services.ai_copilot_service.main",
}

_LOCAL_ASGI_APPS: Dict[str, Any] = {}
_TCP_OFFLINE_UNTIL: Dict[str, float] = {}


async def _get_local_asgi_app(module: str):
    if module in _LOCAL_ASGI_APPS:
        return _LOCAL_ASGI_APPS[module]
    mod_path = SERVICE_MODULE_PATHS.get(module)
    if not mod_path:
        return None
    import importlib
    mod = importlib.import_module(mod_path)
    target_app = getattr(mod, "app", None)
    if target_app is not None:
        for handler in getattr(target_app.router, "on_startup", []):
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception:
                pass
        _LOCAL_ASGI_APPS[module] = target_app
    return target_app


async def _call_service(
    module: str,
    method: str,
    path: str,
    headers: Dict[str, str],
    content: bytes = b"",
    timeout: float = 5.0
) -> httpx.Response:
    import time
    base_url = SERVICE_ROUTES[module]
    url = f"{base_url}{path}"
    now = time.time()
    if now >= _TCP_OFFLINE_UNTIL.get(module, 0.0):
        try:
            tcp_timeout = httpx.Timeout(timeout, connect=0.2)
            async with httpx.AsyncClient(timeout=tcp_timeout) as client:
                return await client.request(method=method, url=url, headers=headers, content=content)
        except (httpx.ConnectError, httpx.ConnectTimeout):
            _TCP_OFFLINE_UNTIL[module] = now + 15.0

    target_app = await _get_local_asgi_app(module)
    if target_app is None:
        raise httpx.ConnectError(f"Service {module} unavailable")
    transport = httpx.ASGITransport(app=target_app)
    async with httpx.AsyncClient(transport=transport, base_url=base_url, timeout=timeout) as local_client:
        return await local_client.request(method=method, url=path, headers=headers, content=content)


def _build_signed_headers(request: Request) -> Dict[str, str]:
    user_ctx = get_user_context(request)
    gateway_sig = generate_gateway_signature(user_ctx.user_id, user_ctx.org_id, GATEWAY_SECRET)
    headers = {
        "x-user-id": user_ctx.user_id,
        "x-org-id": user_ctx.org_id,
        "x-user-role": user_ctx.role,
        "x-gateway-signature": gateway_sig,
    }
    if user_ctx.email:
        headers["x-user-email"] = user_ctx.email
    return headers


# ----------------------------------------------------
# 2. Distributed Event Broker Registry
# ----------------------------------------------------
event_subscriptions: Dict[str, List[str]] = {}
event_history: List[Dict[str, Any]] = []

class EventSubscribeRequest(BaseModel):
    event_name: str
    webhook_url: str

class EventPublishRequest(BaseModel):
    event_name: str
    payload: Dict[str, Any]
    org_id: str = "org-acroflow-main"
    event_id: Optional[str] = None
    timestamp: Optional[str] = None

@app.post("/events/subscribe")
def subscribe_event(req: EventSubscribeRequest):
    """Microservices register their webhook URL to receive distributed events."""
    if req.event_name not in event_subscriptions:
        event_subscriptions[req.event_name] = []
    if req.webhook_url not in event_subscriptions[req.event_name]:
        event_subscriptions[req.event_name].append(req.webhook_url)
    return {"status": "subscribed", "event": req.event_name, "webhook": req.webhook_url}

@app.post("/events/publish")
async def publish_event(event: EventPublishRequest):
    """Broadcasts a domain event published by one microservice to all registered subscriber webhooks."""
    event_dict = event.model_dump()
    event_history.append(event_dict)
    if len(event_history) > 500:
        event_history.pop(0)

    targets = set(event_subscriptions.get(event.event_name, []) + event_subscriptions.get("*", []))
    
    async def dispatch_webhook(url: str):
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                await client.post(url, json=event_dict)
        except Exception:
            pass

    for target_url in targets:
        asyncio.create_task(dispatch_webhook(target_url))

    return {"status": "published", "event_name": event.event_name, "subscribers_notified": len(targets)}

@app.get("/events/history")
def get_events_history():
    return {"count": len(event_history), "recent": event_history[-30:]}

# ----------------------------------------------------
# 3. Health & Gateway Observability
# ----------------------------------------------------
@app.get("/health")
async def health_check():
    """Pings all downstream services in parallel and returns overall cluster health."""
    results = {}
    unique_routes = {k: v for k, v in SERVICE_ROUTES.items() if k != "collaboration"}

    async def check_service(name: str):
        try:
            resp = await _call_service(name, "GET", "/health", headers={}, timeout=1.0)
            return name, {"status": "UP" if resp.status_code == 200 else "DEGRADED", "code": resp.status_code}
        except Exception:
            return name, {"status": "DOWN", "error": "unreachable"}

    tasks = [check_service(name) for name in unique_routes.keys()]
    service_statuses = await asyncio.gather(*tasks)
    for name, status_info in service_statuses:
        results[name] = status_info

    return {
        "gateway": "HEALTHY",
        "port": config.service_port,
        "services": results
    }

# ----------------------------------------------------
# 4. Aggregated Executive Cockpit (/api/v1/overview)
# ----------------------------------------------------
@app.get("/api/v1/overview")
async def get_overview(request: Request):
    """
    Aggregates real, unpadded KPIs across CRM, Finance, Projects, HR, Support,
    Companies, and Compliance microservices using parallel async fan-out requests.
    """
    headers = _build_signed_headers(request)
    tasks = [
        _call_service("crm", "GET", "/crm/deals", headers, timeout=3.0),
        _call_service("finance", "GET", "/finance/invoices", headers, timeout=3.0),
        _call_service("projects", "GET", "/projects", headers, timeout=3.0),
        _call_service("hr", "GET", "/hr/employees", headers, timeout=3.0),
        _call_service("support", "GET", "/support/tickets", headers, timeout=3.0),
        _call_service("crm", "GET", "/crm/companies", headers, timeout=3.0),
        _call_service("compliance", "GET", "/compliance/audit-logs", headers, timeout=3.0),
        _call_service("finance", "GET", "/finance/expenses", headers, timeout=3.0),
        _call_service("automation", "GET", "/automation/approvals", headers, timeout=3.0),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    def _safe_list(idx: int) -> List[Dict[str, Any]]:
        r = results[idx]
        if not isinstance(r, Exception) and getattr(r, "status_code", 500) == 200:
            data = r.json()
            return data if isinstance(data, list) else []
        return []

    deals_data = _safe_list(0)
    invoices_data = _safe_list(1)
    projects_data = _safe_list(2)
    hr_data = _safe_list(3)
    tickets_data = _safe_list(4)
    companies_data = _safe_list(5)
    audit_data = _safe_list(6)
    expenses_data = _safe_list(7)
    approvals_data = _safe_list(8)

    total_pipeline = sum(float(d.get("amount", 0.0) or 0.0) for d in deals_data if d.get("stage") != "Lost")
    total_revenue_paid = sum(float(i.get("total_amount", 0.0) or 0.0) for i in invoices_data if i.get("status") == "Paid")
    overdue_receivables = sum(float(i.get("balance_due", i.get("total_amount", 0.0)) or 0.0) for i in invoices_data if i.get("status") in ["Overdue", "Sent", "Unpaid"])
    total_expenses = sum(float(e.get("amount", 0.0) or 0.0) for e in expenses_data)
    active_projects = len(projects_data)
    total_employees = len(hr_data)
    open_tickets = len([t for t in tickets_data if t.get("status") not in ["Resolved", "Closed"]])
    pending_approvals = len([a for a in approvals_data if a.get("status") == "PENDING"])

    recent_audit = [
        {
            "id": a.get("id"),
            "actor": a.get("actor_email") or a.get("actor_id") or "system",
            "action": a.get("action"),
            "resource": f"{a.get('resource_type')}:{a.get('resource_id') or 'global'}",
            "timestamp": a.get("created_at")
        }
        for a in audit_data[:10]
    ]

    return {
        "kpis": {
            "total_revenue_paid": round(total_revenue_paid, 2),
            "total_pipeline": round(total_pipeline, 2),
            "overdue_receivables": round(overdue_receivables, 2),
            "total_expenses": round(total_expenses, 2),
            "net_profit": round(total_revenue_paid - total_expenses, 2),
            "active_projects": active_projects,
            "open_tickets": open_tickets,
            "total_employees": total_employees,
            "customer_count": len(companies_data),
            "pending_approvals": pending_approvals
        },
        "recent_audit": recent_audit
    }

# ----------------------------------------------------
# 5. Distributed Omnisearch (/api/v1/search)
# ----------------------------------------------------
@app.get("/api/v1/search")
async def global_omnisearch(request: Request, q: str = Query("", min_length=1)):
    """
    Queries CRM (deals, leads, companies), Finance (invoices), Projects (tasks),
    HR (employees), Inventory (products), Procurement (POs), and Support (tickets)
    in parallel to deliver instant, real global search across all microservices.
    """
    headers = _build_signed_headers(request)
    ql = q.lower().strip()
    tasks = [
        _call_service("crm", "GET", "/crm/deals", headers, timeout=2.5),
        _call_service("finance", "GET", "/finance/invoices", headers, timeout=2.5),
        _call_service("projects", "GET", "/projects/tasks", headers, timeout=2.5),
        _call_service("crm", "GET", "/crm/leads", headers, timeout=2.5),
        _call_service("crm", "GET", "/crm/companies", headers, timeout=2.5),
        _call_service("hr", "GET", "/hr/employees", headers, timeout=2.5),
        _call_service("inventory", "GET", "/inventory/products", headers, timeout=2.5),
        _call_service("procurement", "GET", "/procurement/orders", headers, timeout=2.5),
        _call_service("support", "GET", "/support/tickets", headers, timeout=2.5),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    def _safe_list(idx: int) -> List[Dict[str, Any]]:
        r = results[idx]
        if not isinstance(r, Exception) and getattr(r, "status_code", 500) == 200:
            data = r.json()
            return data if isinstance(data, list) else []
        return []

    aggregated = []

    for d in _safe_list(0):
        if ql in str(d.get("title", "")).lower() or ql in str(d.get("company_name", "")).lower():
            aggregated.append({
                "id": d.get("id"),
                "title": d.get("title"),
                "subtitle": f"{d.get('company_name')} • ${float(d.get('amount', 0) or 0):,.0f} ({d.get('stage')})",
                "type": "Deal",
                "tab": "deals",
                "category": "Sales & CRM"
            })

    for inv in _safe_list(1):
        if ql in str(inv.get("invoice_number", "")).lower() or ql in str(inv.get("client_name", "")).lower():
            aggregated.append({
                "id": inv.get("id"),
                "title": f"Invoice {inv.get('invoice_number')}",
                "subtitle": f"{inv.get('client_name')} • ${float(inv.get('total_amount', 0) or 0):,.0f} ({inv.get('status')})",
                "type": "Invoice",
                "tab": "finance",
                "category": "Finance & Accounting"
            })

    for t in _safe_list(2):
        if ql in str(t.get("title", "")).lower() or ql in str(t.get("issue_key", "")).lower():
            aggregated.append({
                "id": t.get("id"),
                "title": f"[{t.get('issue_key')}] {t.get('title')}",
                "subtitle": f"{t.get('status')} • {t.get('priority')} Priority",
                "type": "Task",
                "tab": "projects",
                "category": "Projects & Operations"
            })

    for l in _safe_list(3):
        full_name = f"{l.get('first_name', '')} {l.get('last_name', '')}".strip()
        if ql in full_name.lower() or ql in str(l.get("company_name", "")).lower() or ql in str(l.get("email", "")).lower():
            aggregated.append({
                "id": l.get("id"),
                "title": full_name or l.get("email"),
                "subtitle": f"{l.get('company_name')} • {l.get('status')}",
                "type": "Lead",
                "tab": "leads",
                "category": "Sales & CRM"
            })

    for c in _safe_list(4):
        if ql in str(c.get("name", "")).lower() or ql in str(c.get("industry", "")).lower():
            aggregated.append({
                "id": c.get("id"),
                "title": c.get("name"),
                "subtitle": f"{c.get('industry')} • {c.get('tier', 'Enterprise')}",
                "type": "Company",
                "tab": "contacts",
                "category": "Sales & CRM"
            })

    for emp in _safe_list(5):
        ename = f"{emp.get('first_name', '')} {emp.get('last_name', '')}".strip()
        if ql in ename.lower() or ql in str(emp.get("job_title", "")).lower() or ql in str(emp.get("email", "")).lower():
            aggregated.append({
                "id": emp.get("id"),
                "title": ename,
                "subtitle": f"{emp.get('job_title')} • {emp.get('email')}",
                "type": "Employee",
                "tab": "hr",
                "category": "HR & People"
            })

    for prod in _safe_list(6):
        if ql in str(prod.get("name", "")).lower() or ql in str(prod.get("sku", "")).lower():
            aggregated.append({
                "id": prod.get("id"),
                "title": f"[{prod.get('sku')}] {prod.get('name')}",
                "subtitle": f"${float(prod.get('unit_price', 0) or 0):,.2f} • {prod.get('stock_quantity', 0)} in stock",
                "type": "Product",
                "tab": "inventory",
                "category": "Inventory & Assets"
            })

    for po in _safe_list(7):
        if ql in str(po.get("po_number", "")).lower() or ql in str(po.get("vendor_name", "")).lower():
            aggregated.append({
                "id": po.get("id"),
                "title": f"PO {po.get('po_number')}",
                "subtitle": f"{po.get('vendor_name')} • ${float(po.get('total_amount', 0) or 0):,.2f} ({po.get('status')})",
                "type": "PO",
                "tab": "procurement",
                "category": "Procurement"
            })

    for tkt in _safe_list(8):
        if (
            ql in str(tkt.get("ticket_number", "")).lower()
            or ql in str(tkt.get("subject", "")).lower()
            or ql in str(tkt.get("customer_name", "")).lower()
            or ql in str(tkt.get("customer_email", "")).lower()
        ):
            aggregated.append({
                "id": tkt.get("id"),
                "title": f"[{tkt.get('ticket_number')}] {tkt.get('subject')}",
                "subtitle": f"{tkt.get('customer_name')} • {tkt.get('status')} ({tkt.get('priority')})",
                "type": "Ticket",
                "tab": "support",
                "category": "Customer Support"
            })

    return aggregated


# ----------------------------------------------------
# 6. Module 9: Cross-Module BI & Custom Report Builder
# ----------------------------------------------------
class CustomReportRequest(BaseModel):
    primary_module: str = "finance"
    join_module: Optional[str] = "crm"
    group_by: str = "status"
    metric: str = "sum"  # sum, count, avg
    status_filter: Optional[str] = None


@app.get("/api/v1/analytics/dashboard")
@app.get("/api/v1/analytics/bi-dashboard")
async def get_bi_dashboard(request: Request):
    """
    Module 9: Real-time Cross-Module Business Intelligence Dashboard.
    Joins CRM, Marketing, Finance, Inventory, Procurement, Projects, HR, and Support
    without ETL delays, and calculates predictive revenue & cash-flow projections.
    """
    headers = _build_signed_headers(request)
    tasks = [
        _call_service("crm", "GET", "/crm/deals", headers, timeout=4.0),
        _call_service("crm", "GET", "/crm/companies", headers, timeout=4.0),
        _call_service("marketing", "GET", "/marketing/campaigns", headers, timeout=4.0),
        _call_service("finance", "GET", "/finance/invoices", headers, timeout=4.0),
        _call_service("finance", "GET", "/finance/expenses", headers, timeout=4.0),
        _call_service("finance", "GET", "/finance/subscriptions", headers, timeout=4.0),
        _call_service("inventory", "GET", "/inventory/products", headers, timeout=4.0),
        _call_service("procurement", "GET", "/procurement/orders", headers, timeout=4.0),
        _call_service("projects", "GET", "/projects", headers, timeout=4.0),
        _call_service("hr", "GET", "/hr/employees", headers, timeout=4.0),
        _call_service("hr", "GET", "/hr/departments", headers, timeout=4.0),
        _call_service("support", "GET", "/support/tickets", headers, timeout=4.0),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    def _safe_list(idx: int) -> List[Dict[str, Any]]:
        r = results[idx]
        if not isinstance(r, Exception) and getattr(r, "status_code", 500) == 200:
            data = r.json()
            return data if isinstance(data, list) else []
        return []

    deals = _safe_list(0)
    companies = _safe_list(1)
    campaigns = _safe_list(2)
    invoices = _safe_list(3)
    expenses = _safe_list(4)
    subscriptions = _safe_list(5)
    products = _safe_list(6)
    pos = _safe_list(7)
    projects = _safe_list(8)
    employees = _safe_list(9)
    departments = _safe_list(10)
    tickets = _safe_list(11)

    paid_revenue = sum(float(i.get("total_amount", 0.0) or 0.0) for i in invoices if i.get("status") == "Paid")
    total_billed = sum(float(i.get("total_amount", 0.0) or 0.0) for i in invoices)
    total_expenses = sum(float(e.get("amount", 0.0) or 0.0) for e in expenses)
    net_profit = paid_revenue - total_expenses
    headcount = len(employees)
    rev_per_employee = round(paid_revenue / headcount, 2) if headcount > 0 else 0.0
    profit_per_employee = round(net_profit / headcount, 2) if headcount > 0 else 0.0

    # Cross-Module Join 1: Client 360 Revenue & Pipeline & Support Matrix
    client_map: Dict[str, Dict[str, Any]] = {}
    for c in companies:
        cname = c.get("name") or "Unknown"
        client_map[cname] = {"client": cname, "industry": c.get("industry", "Tech"), "pipeline": 0.0, "billed": 0.0, "paid": 0.0, "tickets": 0}
    for d in deals:
        cname = d.get("company_name") or "Unknown"
        client_map.setdefault(cname, {"client": cname, "industry": "Enterprise", "pipeline": 0.0, "billed": 0.0, "paid": 0.0, "tickets": 0})
        if d.get("stage") != "Lost":
            client_map[cname]["pipeline"] += float(d.get("amount", 0.0) or 0.0)
    for inv in invoices:
        cname = inv.get("client_name") or "Unknown"
        client_map.setdefault(cname, {"client": cname, "industry": "Enterprise", "pipeline": 0.0, "billed": 0.0, "paid": 0.0, "tickets": 0})
        amt = float(inv.get("total_amount", 0.0) or 0.0)
        client_map[cname]["billed"] += amt
        if inv.get("status") == "Paid":
            client_map[cname]["paid"] += amt
    for t in tickets:
        cname = t.get("customer_name") or "Unknown"
        if cname in client_map:
            client_map[cname]["tickets"] += 1

    # Cross-Module Join 2: Marketing Channel ROI Matrix
    marketing_roi = []
    for cmp in campaigns:
        spent = float(cmp.get("spent", 0.0) or 0.0)
        rev = float(cmp.get("revenue_attributed", 0.0) or 0.0)
        roi_pct = round(((rev - spent) / spent) * 100.0, 1) if spent > 0 else 0.0
        marketing_roi.append({
            "id": cmp.get("id"),
            "name": cmp.get("name"),
            "channel": cmp.get("type"),
            "status": cmp.get("status"),
            "budget": float(cmp.get("budget", 0.0) or 0.0),
            "spent": spent,
            "leads": int(cmp.get("leads_generated", 0) or 0),
            "conversions": int(cmp.get("conversions", 0) or 0),
            "revenue_attributed": rev,
            "roi_pct": roi_pct
        })

    # Cross-Module Join 3: HR Department Payroll & Headcount Allocation
    dept_lookup = {d.get("id"): d.get("name") for d in departments}
    dept_stats: Dict[str, Dict[str, Any]] = {}
    for emp in employees:
        dname = dept_lookup.get(emp.get("department_id")) or "General Operations"
        dept_stats.setdefault(dname, {"department": dname, "headcount": 0, "annual_payroll": 0.0})
        dept_stats[dname]["headcount"] += 1
        dept_stats[dname]["annual_payroll"] += float(emp.get("salary_annual", 0.0) or 0.0)

    # Predictive Analytics: Weighted Pipeline + Active MRR Forecast
    weighted_pipeline = sum(
        float(d.get("amount", 0.0) or 0.0) * (float(d.get("probability", 50) or 50) / 100.0)
        for d in deals if d.get("stage") not in ["Won", "Lost"]
    )
    monthly_recurring = sum(
        float(s.get("amount", 0.0) or 0.0)
        for s in subscriptions if s.get("status") == "Active"
    )
    baseline_monthly = round((paid_revenue / 3.0) if paid_revenue > 0 else monthly_recurring, 2)
    forecast_series = [
        {"period": "Current Actual", "revenue": round(paid_revenue, 2), "projected": round(paid_revenue, 2), "confidence_low": round(paid_revenue, 2), "confidence_high": round(paid_revenue, 2)},
        {"period": "Month +1 (Forecast)", "revenue": 0.0, "projected": round(baseline_monthly + weighted_pipeline * 0.35 + monthly_recurring, 2), "confidence_low": round((baseline_monthly + weighted_pipeline * 0.25) * 0.9, 2), "confidence_high": round((baseline_monthly + weighted_pipeline * 0.45) * 1.1, 2)},
        {"period": "Month +2 (Forecast)", "revenue": 0.0, "projected": round(baseline_monthly * 1.08 + weighted_pipeline * 0.40 + monthly_recurring, 2), "confidence_low": round((baseline_monthly + weighted_pipeline * 0.30) * 0.88, 2), "confidence_high": round((baseline_monthly + weighted_pipeline * 0.50) * 1.15, 2)},
        {"period": "Month +3 (Forecast)", "revenue": 0.0, "projected": round(baseline_monthly * 1.15 + weighted_pipeline * 0.25 + monthly_recurring, 2), "confidence_low": round((baseline_monthly + weighted_pipeline * 0.20) * 0.85, 2), "confidence_high": round((baseline_monthly + weighted_pipeline * 0.35) * 1.2, 2)},
    ]

    inventory_value = sum(float(p.get("unit_price", 0.0) or 0.0) * int(p.get("stock_quantity", 0) or 0) for p in products)
    po_committed = sum(float(p.get("total_amount", 0.0) or 0.0) for p in pos)

    return {
        "executive_summary": {
            "paid_revenue": round(paid_revenue, 2),
            "total_billed": round(total_billed, 2),
            "total_expenses": round(total_expenses, 2),
            "net_profit": round(net_profit, 2),
            "weighted_pipeline": round(weighted_pipeline, 2),
            "monthly_recurring_revenue": round(monthly_recurring, 2),
            "headcount": headcount,
            "revenue_per_employee": rev_per_employee,
            "profit_per_employee": profit_per_employee,
            "inventory_valuation": round(inventory_value, 2),
            "procurement_committed": round(po_committed, 2),
            "active_projects": len(projects),
            "open_tickets": len([t for t in tickets if t.get("status") not in ["Resolved", "Closed"]])
        },
        "client_360_matrix": list(client_map.values()),
        "marketing_roi_matrix": marketing_roi,
        "department_allocation": list(dept_stats.values()),
        "predictive_forecast": forecast_series
    }


@app.post("/api/v1/analytics/custom-report")
async def build_custom_report(req: CustomReportRequest, request: Request):
    """
    Module 9: Custom Report Builder translating user selections into live RBAC-scoped
    queries across any module with grouping, aggregation, and CSV export generation.
    """
    headers = _build_signed_headers(request)
    endpoint_map = {
        "crm": ("crm", "/crm/deals", "amount", ["title", "company_name", "stage", "amount", "probability"]),
        "leads": ("crm", "/crm/leads", "score", ["first_name", "last_name", "company_name", "source", "status", "score"]),
        "finance": ("finance", "/finance/invoices", "total_amount", ["invoice_number", "client_name", "status", "total_amount", "due_date"]),
        "expenses": ("finance", "/finance/expenses", "amount", ["category", "merchant", "status", "amount", "expense_date"]),
        "hr": ("hr", "/hr/employees", "salary_annual", ["first_name", "last_name", "job_title", "employment_type", "status", "salary_annual"]),
        "projects": ("projects", "/projects/tasks", "story_points", ["issue_key", "title", "status", "priority", "story_points"]),
        "inventory": ("inventory", "/inventory/products", "unit_price", ["sku", "name", "category", "unit_price", "stock_quantity"]),
        "procurement": ("procurement", "/procurement/orders", "total_amount", ["po_number", "vendor_name", "status", "total_amount", "expected_delivery_date"]),
        "marketing": ("marketing", "/marketing/campaigns", "revenue_attributed", ["name", "type", "status", "budget", "spent", "revenue_attributed"]),
        "support": ("support", "/support/tickets", "csat_score", ["ticket_number", "customer_name", "priority", "status", "sla_status"]),
    }

    svc_mod, svc_path, numeric_field, cols = endpoint_map.get(req.primary_module, endpoint_map["finance"])
    resp = await _call_service(svc_mod, "GET", svc_path, headers, timeout=3.0)
    records = resp.json() if resp.status_code == 200 and isinstance(resp.json(), list) else []

    if req.status_filter:
        records = [r for r in records if str(r.get("status", "")).lower() == req.status_filter.lower()]

    groups: Dict[str, List[float]] = {}
    for r in records:
        g_val = str(r.get(req.group_by) or "Uncategorized")
        val = float(r.get(numeric_field, 0.0) or 0.0)
        groups.setdefault(g_val, []).append(val)

    summary_groups = []
    for g_key, vals in groups.items():
        if req.metric == "count":
            agg = float(len(vals))
        elif req.metric == "avg":
            agg = round(sum(vals) / len(vals), 2) if vals else 0.0
        else:
            agg = round(sum(vals), 2)
        summary_groups.append({
            "group": g_key,
            "count": len(vals),
            "metric_value": agg
        })

    rows = [[r.get(c, "") for c in cols] for r in records]
    csv_lines = [",".join(cols)] + [",".join(f'"{str(cell)}"' for cell in row) for row in rows]

    return {
        "primary_module": req.primary_module,
        "group_by": req.group_by,
        "metric": req.metric,
        "numeric_field": numeric_field,
        "total_records": len(records),
        "columns": cols,
        "rows": rows,
        "summary_groups": summary_groups,
        "csv_export": "\n".join(csv_lines)
    }


# ----------------------------------------------------
# 7. Dynamic Reverse Proxy Forwarder
# ----------------------------------------------------
@app.api_route("/api/v1/{module}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.api_route("/api/v1/{module}/{rest_of_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def reverse_proxy_handler(module: str, request: Request, rest_of_path: str = ""):
    """
    Dynamically routes HTTP traffic to target microservice:
    1. Inspects JWT token and validates user context.
    2. Generates HMAC gateway signature.
    3. Streams request to target microservice port (or in-process ASGITransport fallback).
    """
    target_base = SERVICE_ROUTES.get(module)
    if not target_base:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Microservice domain '{module}' not registered in STAT6 Gateway"
        )

    downstream_prefix = "chat" if module == "collaboration" else module
    target_path = f"/{downstream_prefix}/{rest_of_path}" if rest_of_path else f"/{downstream_prefix}"
    if request.url.query:
        target_path = f"{target_path}?{request.url.query}"

    user_ctx = get_user_context(request)
    gateway_sig = generate_gateway_signature(user_ctx.user_id, user_ctx.org_id, GATEWAY_SECRET)

    forward_headers = dict(request.headers)
    forward_headers["x-user-id"] = user_ctx.user_id
    forward_headers["x-org-id"] = user_ctx.org_id
    forward_headers["x-user-role"] = user_ctx.role
    forward_headers["x-user-persona"] = user_ctx.persona
    if user_ctx.email:
        forward_headers["x-user-email"] = user_ctx.email
    forward_headers["x-gateway-signature"] = gateway_sig
    forward_headers.pop("host", None)

    body = await request.body()

    try:
        timeout = 60.0 if module == "ai" else 15.0
        downstream_resp = await _call_service(
            module=module,
            method=request.method,
            path=target_path,
            headers=forward_headers,
            content=body,
            timeout=timeout
        )

        excluded_headers = ["content-encoding", "content-length", "transfer-encoding", "connection"]
        response_headers = {
            k: v for k, v in downstream_resp.headers.items()
            if k.lower() not in excluded_headers
        }

        return Response(
            content=downstream_resp.content,
            status_code=downstream_resp.status_code,
            headers=response_headers,
            media_type=downstream_resp.headers.get("content-type")
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Downstream microservice '{module}' at {target_base} is offline or unreachable."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gateway routing error to '{module}': {str(e)}"
        )

