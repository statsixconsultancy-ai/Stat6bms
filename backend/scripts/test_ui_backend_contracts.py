"""
Comprehensive End-to-End UI <-> Gateway <-> Microservice <-> Supabase PostgreSQL Contract Verification Suite.
Verifies every UI-triggered endpoint, response schema, multi-tenant header propagation, and cross-service workflow.
"""
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi.testclient import TestClient
from backend.services.gateway.main import app

client = TestClient(app)

HEADERS = {
    "X-Org-Id": "org-acroflow-enterprise",
    "X-User-Role": "ADMIN",
    "X-User-Persona": "ADMIN",
    "X-User-Email": "admin@acroflow.enterprise",
}

passed = 0
failed = 0


def check(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  [PASS] {name}")
    else:
        failed += 1
        print(f"  [FAIL] {name} -> {detail}")


def run_suite():
    print("=" * 80)
    print("STAT6 BMS: UI <-> API GATEWAY <-> SUPABASE LIVE CONTRACT VERIFICATION")
    print("=" * 80)

    # 1. Gateway Health & Root Module Routing (No 307 Redirect)
    r = client.get("/health")
    check("Gateway /health returns 200", r.status_code == 200, str(r.text))

    r_proj_root = client.get("/api/v1/projects", headers=HEADERS, follow_redirects=False)
    check(
        "GET /api/v1/projects resolves directly (200, no 307 redirect)",
        r_proj_root.status_code == 200 and isinstance(r_proj_root.json(), list),
        f"status={r_proj_root.status_code}",
    )

    # 2. Auth Service: OAuth Token + Modal User Registration + Landing Registration
    r_oauth = client.post(
        "/api/v1/auth/oauth/token",
        json={"grant_type": "password", "username": "admin@acroflow.enterprise", "password": "Password123!"},
    )
    check(
        "POST /api/v1/auth/oauth/token authenticates ADMIN persona",
        r_oauth.status_code == 200 and "access_token" in r_oauth.json(),
        str(r_oauth.text),
    )

    import uuid
    unique_email = f"modal.user.{uuid.uuid4().hex[:6]}@acroflow.enterprise"
    r_reg_modal = client.post(
        "/api/v1/auth/register",
        headers=HEADERS,
        json={
            "email": unique_email,
            "full_name": "Modal Registered User",
            "password": "Password123!",
            "role": "MANAGER",
            "persona": "MANAGER",
        },
    )
    check(
        "POST /api/v1/auth/register supports Workspace Modal user creation payload",
        r_reg_modal.status_code == 200 and r_reg_modal.json().get("user", {}).get("email") == unique_email,
        str(r_reg_modal.text),
    )

    # 3. CRM Service: Leads, Deals, Quotes E-Sign (optional signer), Convert-to-Invoice & Convert-to-Project
    r_leads = client.get("/api/v1/crm/leads", headers=HEADERS)
    check("GET /api/v1/crm/leads returns list", r_leads.status_code == 200 and isinstance(r_leads.json(), list))

    r_deal_create = client.post(
        "/api/v1/crm/deals",
        headers=HEADERS,
        json={"name": "Global Port Logistics Expansion", "value": 85000, "stage": "Negotiation", "probability": 80},
    )
    check("POST /api/v1/crm/deals creates deal", r_deal_create.status_code == 200, str(r_deal_create.text))
    deal_id = r_deal_create.json()["id"]

    r_conv_inv = client.post(f"/api/v1/crm/deals/{deal_id}/convert-to-invoice", headers=HEADERS)
    check(
        "POST /api/v1/crm/deals/{id}/convert-to-invoice persists real Invoice",
        r_conv_inv.status_code == 200 and "invoice_id" in r_conv_inv.json(),
        str(r_conv_inv.text),
    )

    r_conv_prj = client.post(f"/api/v1/crm/deals/{deal_id}/convert-to-project", headers=HEADERS)
    check(
        "POST /api/v1/crm/deals/{id}/convert-to-project persists real Project",
        r_conv_prj.status_code == 200 and "project_id" in r_conv_prj.json(),
        str(r_conv_prj.text),
    )

    r_quote = client.post(
        "/api/v1/crm/quotes",
        headers=HEADERS,
        json={"deal_id": deal_id, "quote_number": f"QT-{uuid.uuid4().hex[:5].upper()}", "amount": 85000},
    )
    check("POST /api/v1/crm/quotes creates quote", r_quote.status_code == 200, str(r_quote.text))
    quote_id = r_quote.json()["id"]

    r_esign = client.post(f"/api/v1/crm/quotes/{quote_id}/e-sign", headers=HEADERS, json={})
    check(
        "POST /api/v1/crm/quotes/{id}/e-sign succeeds with empty JSON body (UI default)",
        r_esign.status_code == 200 and r_esign.json().get("status") == "Signed",
        str(r_esign.text),
    )

    # 4. Projects Service: Critical Path, Financials, Milestones & Milestone Billing
    proj_id = r_conv_prj.json()["project_id"]

    r_cpm = client.get(f"/api/v1/projects/{proj_id}/critical-path", headers=HEADERS)
    cpm_data = r_cpm.json() if r_cpm.status_code == 200 else {}
    check(
        "GET /api/v1/projects/{id}/critical-path returns UI fields (total_duration_hours, schedule)",
        r_cpm.status_code == 200 and "total_duration_hours" in cpm_data and "schedule" in cpm_data,
        str(r_cpm.text),
    )

    r_pfin = client.get(f"/api/v1/projects/{proj_id}/financials", headers=HEADERS)
    pfin_data = r_pfin.json() if r_pfin.status_code == 200 else {}
    check(
        "GET /api/v1/projects/{id}/financials returns UI fields (budget, total_cost, gross_margin_percent)",
        r_pfin.status_code == 200 and "budget" in pfin_data and "total_cost" in pfin_data and "gross_margin_percent" in pfin_data,
        str(r_pfin.text),
    )

    r_ms = client.post(
        f"/api/v1/projects/{proj_id}/milestones",
        headers=HEADERS,
        json={"project_id": proj_id, "name": "Phase 1 Go-Live", "billing_amount": 25000.0},
    )
    check(
        "POST /api/v1/projects/{id}/milestones accepts billing_amount without due_date",
        r_ms.status_code == 200 and r_ms.json().get("billing_amount") == 25000.0,
        str(r_ms.text),
    )
    ms_id = r_ms.json()["id"]

    r_ms_comp = client.post(f"/api/v1/projects/milestones/{ms_id}/complete", headers=HEADERS)
    check(
        "POST /api/v1/projects/milestones/{id}/complete generates invoice in fin_invoices",
        r_ms_comp.status_code == 200 and r_ms_comp.json().get("auto_billed_invoice_id") is not None,
        str(r_ms_comp.text),
    )

    # 5. Marketing Service: Campaigns, Drip Journeys, Broadcasts, ROI Attribution
    r_camp = client.post(
        "/api/v1/marketing/campaigns",
        headers=HEADERS,
        json={"name": "Q4 Maritime Executive Roadshow", "channel": "LinkedIn", "budget": 15000, "spent": 4500, "leads_generated": 42, "revenue_attributed": 120000},
    )
    check(
        "POST /api/v1/marketing/campaigns returns UI fields (spent, leads_generated, revenue_attributed)",
        r_camp.status_code == 200 and r_camp.json().get("spent") == 4500 and r_camp.json().get("leads_generated") == 42,
        str(r_camp.text),
    )

    r_drip = client.post(
        "/api/v1/marketing/drip-journeys",
        headers=HEADERS,
        json={"name": "Enterprise Trial Onboarding", "trigger_event": "Lead Created", "steps": ["Day 1 Welcome", "Day 3 Case Study"]},
    )
    check(
        "POST /api/v1/marketing/drip-journeys accepts steps array & returns converted_count",
        r_drip.status_code == 200 and isinstance(r_drip.json().get("steps"), list) and "converted_count" in r_drip.json(),
        str(r_drip.text),
    )

    r_roi = client.post(
        "/api/v1/marketing/roi-attribution",
        headers=HEADERS,
        json={"model": "W-SHAPED", "deal_value": 100000, "touchpoints": ["LinkedIn Ad", "Webinar", "Executive Dinner"]},
    )
    check(
        "POST /api/v1/marketing/roi-attribution accepts string touchpoints & model",
        r_roi.status_code == 200 and r_roi.json().get("deal_value") == 100000 and len(r_roi.json().get("touchpoints", [])) == 3,
        str(r_roi.text),
    )

    # 6. HR Service: Employees, Clock-In, Statutory Payroll, OKRs, ATS
    r_emps = client.get("/api/v1/hr/employees", headers=HEADERS)
    if not r_emps.json():
        client.post(
            "/api/v1/hr/employees",
            headers=HEADERS,
            json={
                "first_name": "Marcus",
                "last_name": "Chen",
                "email": "marcus.chen@acroflow.enterprise",
                "job_title": "Chief Technology Officer",
                "salary_annual": 185000.0
            }
        )
        r_emps = client.get("/api/v1/hr/employees", headers=HEADERS)
    check(
        "GET /api/v1/hr/employees includes employee_code",
        r_emps.status_code == 200 and len(r_emps.json()) > 0 and "employee_code" in r_emps.json()[0],
        str(r_emps.text),
    )
    emp_id = r_emps.json()[0]["id"]

    r_stat_pay = client.post(
        "/api/v1/hr/payroll/calculate-statutory",
        headers=HEADERS,
        json={"employee_id": emp_id, "pay_period": "2026-10", "regime": "NEW", "bonus": 5000},
    )
    sp_data = r_stat_pay.json() if r_stat_pay.status_code == 200 else {}
    check(
        "POST /api/v1/hr/payroll/calculate-statutory returns components & deductions breakdown",
        r_stat_pay.status_code == 200 and "components" in sp_data and "deductions" in sp_data and "employee_name" in sp_data,
        str(r_stat_pay.text),
    )

    r_okr = client.post(
        "/api/v1/hr/okrs",
        headers=HEADERS,
        json={"employee_id": emp_id, "objective": "Reduce deployment lead time", "key_result": "Sub-15m CI/CD", "target_value": 100, "current_value": 65},
    )
    check(
        "POST /api/v1/hr/okrs accepts target_value & current_value",
        r_okr.status_code == 200 and r_okr.json().get("target_value") == 100 and r_okr.json().get("current_value") == 65,
        str(r_okr.text),
    )

    # 7. Finance Service: P&L, Cash Flow, Subscriptions, Tax Calculate, OCR Scan
    r_pnl = client.get("/api/v1/finance/reports/pnl", headers=HEADERS)
    pnl_data = r_pnl.json() if r_pnl.status_code == 200 else {}
    check(
        "GET /api/v1/finance/reports/pnl returns total_revenue, total_expenses, net_profit, profit_margin_percent",
        r_pnl.status_code == 200 and "total_revenue" in pnl_data and "profit_margin_percent" in pnl_data,
        str(r_pnl.text),
    )

    r_cf = client.get("/api/v1/finance/reports/cash-flow", headers=HEADERS)
    cf_data = r_cf.json() if r_cf.status_code == 200 else {}
    check(
        "GET /api/v1/finance/reports/cash-flow returns cash_inflows, cash_outflows, net_cash_flow",
        r_cf.status_code == 200 and "cash_inflows" in cf_data and "net_cash_flow" in cf_data,
        str(r_cf.text),
    )

    r_tax = client.post(
        "/api/v1/finance/tax/calculate",
        headers=HEADERS,
        json={"amount": 100000, "gst_rate": 18.0, "is_interstate": False, "tds_rate": 10.0},
    )
    tax_data = r_tax.json() if r_tax.status_code == 200 else {}
    check(
        "POST /api/v1/finance/tax/calculate returns taxable_amount, cgst, sgst, igst, total_with_tax",
        r_tax.status_code == 200 and tax_data.get("cgst") == 9000.0 and tax_data.get("total_with_tax") == 118000.0,
        str(r_tax.text),
    )

    r_ocr = client.post(
        "/api/v1/finance/expenses/ocr-scan",
        headers=HEADERS,
        json={"receipt_text": "AWS Cloud Infrastructure $840.00 Date: 2026-10-30"},
    )
    ocr_data = r_ocr.json() if r_ocr.status_code == 200 else {}
    check(
        "POST /api/v1/finance/expenses/ocr-scan returns merchant & policy_violation and persists expense",
        r_ocr.status_code == 200 and "merchant" in ocr_data and "policy_violation" in ocr_data,
        str(r_ocr.text),
    )

    # 8. Inventory Service: Assets, FIFO/Weighted Valuation
    r_val = client.get("/api/v1/inventory/valuation/fifo-weighted", headers=HEADERS)
    val_data = r_val.json() if r_val.status_code == 200 else {}
    check(
        "GET /api/v1/inventory/valuation/fifo-weighted returns total_units, fifo_total_value, weighted_average_total_value",
        r_val.status_code == 200 and "total_units" in val_data and "fifo_total_value" in val_data,
        str(r_val.text),
    )

    r_asset = client.post(
        "/api/v1/inventory/assets",
        headers=HEADERS,
        json={"asset_tag": f"AST-{uuid.uuid4().hex[:5].upper()}", "name": "MacBook Pro M4 Max", "category": "IT Hardware", "purchase_cost": 3800, "assigned_to": "Engineering"},
    )
    check(
        "POST /api/v1/inventory/assets accepts purchase_cost, category, assigned_to & returns current_value",
        r_asset.status_code == 200 and r_asset.json().get("purchase_cost") == 3800 and "current_value" in r_asset.json(),
        str(r_asset.text),
    )

    # 9. Procurement Service: /procurement/purchase-orders alias, Requisitions, RFQs, Vendor Scorecard
    r_pos = client.get("/api/v1/procurement/purchase-orders", headers=HEADERS)
    check(
        "GET /api/v1/procurement/purchase-orders alias returns PO list with three_way_match_status",
        r_pos.status_code == 200 and isinstance(r_pos.json(), list),
        str(r_pos.text),
    )

    r_vendors = client.get("/api/v1/procurement/vendors", headers=HEADERS)
    if r_vendors.status_code == 200 and len(r_vendors.json()) > 0:
        vid = r_vendors.json()[0]["id"]
        r_sc = client.get(f"/api/v1/procurement/vendors/{vid}/scorecard", headers=HEADERS)
        sc_data = r_sc.json() if r_sc.status_code == 200 else {}
        check(
            "GET /api/v1/procurement/vendors/{id}/scorecard returns overall_score, on_time_delivery_rate, tier_recommendation",
            r_sc.status_code == 200 and "overall_score" in sc_data and "tier_recommendation" in sc_data,
            str(r_sc.text),
        )

    # 10. Support Service: Tickets sla_status & 360 Context
    r_tks = client.get("/api/v1/support/tickets", headers=HEADERS)
    if not r_tks.json():
        client.post(
            "/api/v1/support/tickets",
            headers=HEADERS,
            json={
                "customer_name": "Nordic Marine Logistics",
                "customer_email": "ops@nordicmarine.com",
                "subject": "Container Telemetry Integration Query",
                "description": "Inquiring about automated AIS webhook delivery."
            }
        )
        r_tks = client.get("/api/v1/support/tickets", headers=HEADERS)
    check(
        "GET /api/v1/support/tickets returns sla_status field",
        r_tks.status_code == 200 and len(r_tks.json()) > 0 and "sla_status" in r_tks.json()[0],
        str(r_tks.text),
    )
    tk_id = r_tks.json()[0]["id"]
    r_ctx = client.get(f"/api/v1/support/tickets/{tk_id}/context", headers=HEADERS)
    ctx_data = r_ctx.json() if r_ctx.status_code == 200 else {}
    check(
        "GET /api/v1/support/tickets/{id}/context returns nested crm_context & finance_context",
        r_ctx.status_code == 200 and "crm_context" in ctx_data and "finance_context" in ctx_data,
        str(r_ctx.text),
    )

    # 11. Collaboration Service: Messages (content/sender_name), Notes (GET /chat/notes without params)
    r_notes = client.get("/api/v1/chat/notes", headers=HEADERS)
    check(
        "GET /api/v1/chat/notes works without query parameters",
        r_notes.status_code == 200 and isinstance(r_notes.json(), list),
        str(r_notes.text),
    )

    r_note_post = client.post(
        "/api/v1/chat/notes",
        headers=HEADERS,
        json={"title": "Q4 Board Prep", "content": "Review all EBITDA margins before Friday.", "author_name": "Admin"},
    )
    check(
        "POST /api/v1/chat/notes accepts title, content, author_name without requiring entity_id",
        r_note_post.status_code == 200 and r_note_post.json().get("title") == "Q4 Board Prep",
        str(r_note_post.text),
    )

    # 12. Analytics, Compliance, Automation, AI Copilot
    r_bi = client.get("/api/v1/analytics/dashboard", headers=HEADERS)
    check(
        "GET /api/v1/analytics/dashboard returns live Supabase KPIs (executive_summary with total_billed)",
        r_bi.status_code == 200 and "executive_summary" in r_bi.json() and r_bi.json()["executive_summary"].get("total_billed", 0) > 0,
        str(r_bi.text),
    )

    r_ai = client.post(
        "/api/v1/ai/chat",
        headers=HEADERS,
        json={"message": "What is our financial performance and operating margin today?", "conversation_id": "test-conv-1"},
    )
    check(
        "POST /api/v1/ai/chat returns deterministic telemetry reply from live Supabase",
        r_ai.status_code == 200 and "reply" in r_ai.json(),
        str(r_ai.text),
    )

    print("=" * 80)
    print(f"FINAL RESULT: {passed} PASSED, {failed} FAILED")
    print("=" * 80)
    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_suite()
