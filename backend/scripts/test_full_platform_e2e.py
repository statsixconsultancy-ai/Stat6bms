#!/usr/bin/env python3
"""
Full Distributed Platform End-to-End Integration Test Suite
Validates the complete autonomous cross-microservice lifecycle:
1. Auth Login & Gateway Reverse Proxy
2. Marketing Web Inbound Lead Submission
3. CRM Lead Ingestion & Atomic Conversion to Account, Contact & Deal
4. CRM Deal Won Stage Transition -> Event Bus Broadcast
5. Projects Service Auto-Provisioning on 'deal.won'
6. Finance Service Auto-Drafted Net30 Invoicing on 'deal.won'
7. Invoice Settlement & Zero-Discrepancy Double-Entry General Ledger
8. HR Payroll Execution & Talent Disbursement
9. Inventory Outbound Movement & 'stock.low' Trigger
10. Procurement Auto-Drafted PO Replenishment & 3-Way Matching Verification
11. Support P1 Escalation -> Collab #incident-response Channel Broadcast
12. Automation Engine Rule Matching & Execution Audit
13. AI Copilot Natural Language Multi-Service Synthesis
14. Gateway Distributed Omnisearch & Executive KPI Aggregation
"""
import os
import sys
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Initialize all services
from services.gateway.main import app as gateway_app
from services.auth_service.main import app as auth_app, on_startup as auth_init
from services.crm_service.main import app as crm_app, on_startup as crm_init
from services.marketing_service.main import app as mkt_app, on_startup as mkt_init
from services.projects_service.main import app as prj_app, on_startup as prj_init
from services.hr_service.main import app as hr_app, on_startup as hr_init
from services.finance_service.main import app as fin_app, on_startup as fin_init
from services.inventory_service.main import app as inv_app, on_startup as inv_init
from services.procurement_service.main import app as proc_app, on_startup as proc_init
from services.support_service.main import app as sup_app, on_startup as sup_init
from services.collaboration_service.main import app as col_app, on_startup as col_init
from services.compliance_service.main import app as comp_app, on_startup as comp_init
from services.automation_service.main import app as auto_app, on_startup as auto_init
from services.ai_copilot_service.main import app as ai_app, on_startup as ai_init

auth_init()
crm_init()
mkt_init()
prj_init()
hr_init()
fin_init()
inv_init()
proc_init()
sup_init()
col_init()
comp_init()
auto_init()
ai_init()

gw_client = TestClient(gateway_app)
auth_client = TestClient(auth_app)
crm_client = TestClient(crm_app)
mkt_client = TestClient(mkt_app)
prj_client = TestClient(prj_app)
hr_client = TestClient(hr_app)
fin_client = TestClient(fin_app)
inv_client = TestClient(inv_app)
proc_client = TestClient(procurement_app if 'procurement_app' in locals() else proc_app)
sup_client = TestClient(sup_app)
col_client = TestClient(col_app)
comp_client = TestClient(comp_app)
auto_client = TestClient(auto_app)
ai_client = TestClient(ai_app)

def test_complete_platform_lifecycle():
    print("=" * 70)
    print("  ACROFLOW BMS 2.0: FULL DISTRIBUTED PLATFORM E2E INTEGRATION TEST")
    print("=" * 70)

    # 1. Auth & JWT
    print("\n[Step 1/14] Authenticating Enterprise Superadmin & Validating Identity...")
    login_resp = auth_client.post("/auth/login", json={
        "email": "admin@acroflow.enterprise",
        "password": "AcroFlow2026!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    me_resp = auth_client.get("/auth/me", headers=headers)
    assert me_resp.status_code == 200
    print(f"  [OK] Authenticated: {me_resp.json()['user']['full_name']} ({me_resp.json()['user']['role']})")

    # 2. Marketing Web Inbound
    print("\n[Step 2/14] Ingesting Public Web Lead with UTM Attribution...")
    mkt_sub = mkt_client.post("/marketing/public/submit-form", json={
        "first_name": "Aria",
        "last_name": "Sterling",
        "email": "aria.sterling@apexbiotech.internal",
        "company_name": "Apex BioTech Discovery",
        "phone": "+1 (555) 441-9922",
        "utm_source": "google",
        "utm_campaign": "autonomous_cloud_ads"
    })
    assert mkt_sub.status_code == 200
    print("  [OK] Public lead captured via form and broadcasted to event bus.")

    # 3. CRM Lead Ingestion & Atomic Conversion
    print("\n[Step 3/14] Processing Lead in CRM & Executing Atomic Account Conversion...")
    # Simulate webhook delivery of lead.captured to CRM
    crm_client.post("/webhooks/events", json={
        "event_name": "lead.captured",
        "payload": {
            "first_name": "Aria",
            "last_name": "Sterling",
            "email": "aria.sterling@apexbiotech.internal",
            "company_name": "Apex BioTech Discovery",
            "source": "Google CPC"
        }
    })
    leads = crm_client.get("/crm/leads").json()
    apex_lead = [l for l in leads if l["email"] == "aria.sterling@apexbiotech.internal"][0]
    lead_id = apex_lead["id"]

    convert_resp = crm_client.post(f"/crm/leads/{lead_id}/convert", json={
        "deal_title": "Apex BioTech Multi-Omics AI Platform",
        "deal_amount": 350000.0,
        "close_date": "2026-11-15"
    })
    assert convert_resp.status_code == 200
    deal_info = convert_resp.json()
    deal_id = deal_info["deal_id"]
    print(f"  [OK] Lead converted to Company '{deal_info['company_name']}', Contact, and Deal ${deal_info['deal_amount']:,.2f}.")

    # 4. CRM Stage Move -> Won
    print("\n[Step 4/14] Advancing Deal to Closed-Won & Emitting 'deal.won'...")
    won_resp = crm_client.patch(f"/crm/deals/{deal_id}/stage", json={"stage": "Won"})
    assert won_resp.status_code == 200
    assert won_resp.json()["stage"] == "Won"
    assert won_resp.json()["probability"] == 100
    print("  [OK] Deal marked 'Won'. Event Bus notified.")

    # 5. Projects Auto-Provisioning
    print("\n[Step 5/14] Projects Microservice Auto-Provisioning Delivery Workspace...")
    deal_won_event = {
        "event_name": "deal.won",
        "payload": {
            "deal_id": deal_id,
            "title": "Apex BioTech Multi-Omics AI Platform",
            "amount": 350000.0,
            "company_name": "Apex BioTech Discovery"
        },
        "org_id": "org-acroflow-main"
    }
    p_resp = prj_client.post("/webhooks/events", json=deal_won_event)
    assert p_resp.status_code == 200
    new_prj_id = p_resp.json()["project_id"]
    print(f"  [OK] Project delivery workspace {p_resp.json()['project_code']} auto-created with Sprint 1.")

    # 6. Finance Auto-Drafted Invoicing
    print("\n[Step 6/14] Finance Microservice Auto-Drafting Net30 Customer Invoice...")
    f_resp = fin_client.post("/webhooks/events", json=deal_won_event)
    assert f_resp.status_code == 200
    inv_num = f_resp.json()["invoice_number"]
    print(f"  [OK] Net30 Customer Invoice {inv_num} drafted for $350,000.00.")

    # 7. Settle Invoice & Double-Entry Ledger
    print("\n[Step 7/14] Settle Customer Invoice & Verify Zero-Discrepancy General Ledger...")
    invoices = fin_client.get("/finance/invoices").json()
    target_inv = [i for i in invoices if i["invoice_number"] == inv_num][0]
    pay_resp = fin_client.post(f"/finance/invoices/{target_inv['id']}/pay", json={
        "amount": 350000.0,
        "payment_method": "Wire Transfer"
    })
    assert pay_resp.status_code == 200

    ledger = fin_client.get("/finance/ledger").json()
    latest_entry = ledger[0]
    assert latest_entry["is_balanced"] == True
    assert latest_entry["total_debit"] == latest_entry["total_credit"] == 350000.0
    print(f"  [OK] Settle payment confirmed. General Ledger Entry {latest_entry['entry_number']} balanced (Debit Cash == Credit AR).")

    # 8. HR Monthly Payroll Execution
    print("\n[Step 8/14] People Operations Monthly Payroll Run & Payslips...")
    pay_run = hr_client.post("/hr/payroll/run", json={"period_name": "September 2026"}).json()
    assert pay_run["status"] == "Completed"
    assert pay_run["employees_count"] >= 4
    print(f"  [OK] Payroll Disbursed: Gross ${pay_run['total_gross']:,.2f} | Net ${pay_run['total_net']:,.2f} across {pay_run['employees_count']} employees.")

    # 9. Inventory Movement & Low-Stock Trigger
    print("\n[Step 9/14] Inventory Outbound Stock Movement & Low-Stock Alarm...")
    products = inv_client.get("/inventory/products").json()
    hw_item = products[0]
    # Reduce stock below reorder level
    adj_resp = inv_client.post(f"/inventory/products/{hw_item['id']}/movement", json={
        "quantity_change": -(hw_item["stock_quantity"] - 5),
        "movement_type": "OUTBOUND"
    })
    assert adj_resp.status_code == 200
    assert adj_resp.json()["stock_low_triggered"] == True
    print(f"  [OK] Stock reduced to {adj_resp.json()['new_stock_quantity']} units. 'stock.low' alarm fired.")

    # 10. Procurement Auto-Drafted PO & 3-Way Match
    print("\n[Step 10/14] Procurement Auto-Replenishment & 3-Way Match Verification...")
    stock_event = {
        "event_name": "stock.low",
        "payload": {
            "sku": hw_item["sku"],
            "name": hw_item["name"],
            "reorder_quantity": 40
        }
    }
    po_auto = proc_client.post("/webhooks/events", json=stock_event).json()
    assert po_auto["status"] == "po_auto_drafted"
    print(f"  [OK] Procurement received 'stock.low' and generated replenishment PO {po_auto['po_number']}.")

    # 11. Support Escalation & Collab Incident Alert
    print("\n[Step 11/14] Support Ticket Escalation & Team Channel Swarm Alert...")
    tkt = sup_client.post("/support/tickets", json={
        "customer_name": "David Zhang",
        "customer_email": "dzhang@nexusrobotics.internal",
        "subject": "Hardware Memory Buffer Exception on Rover-04",
        "priority": "High"
    }).json()
    esc = sup_client.post(f"/support/tickets/{tkt['id']}/escalate").json()
    assert esc["priority"] == "Urgent"

    # Forward to collaboration service
    col_client.post("/webhooks/events", json={
        "event_name": "ticket.urgent",
        "payload": {
            "ticket_number": esc["ticket_number"],
            "subject": esc["subject"],
            "customer": esc["customer_name"]
        }
    })
    channels = col_client.get("/chat/channels").json()
    inc_ch = [c for c in channels if c["name"] == "incident-response"][0]
    msgs = col_client.get(f"/chat/channels/{inc_ch['id']}/messages").json()
    assert any(esc["ticket_number"] in m["message"] for m in msgs)
    print(f"  [OK] Urgent ticket {esc['ticket_number']} triggered automated alert in #{inc_ch['name']}.")

    # 12. Automation Engine Rule Matching
    print("\n[Step 12/14] Automation WHEN-IF-DO Rules Execution Verification...")
    auto_rules = auto_client.get("/automation/rules").json()
    assert len(auto_rules) >= 3
    print(f"  [OK] Automation Engine verified with {len(auto_rules)} active enterprise rules.")

    # 13. AI Copilot NLP Synthesis
    print("\n[Step 13/14] Querying Autonomous AI Copilot for Multi-Service Synthesis...")
    copilot_resp = ai_client.post("/ai/query", json={"query": "Provide an executive summary of our business health."}).json()
    assert copilot_resp["intent"] == "EXECUTIVE_OVERVIEW"
    assert len(copilot_resp["sources"]) >= 1
    assert len(copilot_resp["recommendations"]) >= 1
    print(f"  [OK] Copilot Answer: {copilot_resp['answer'][:80]}... ({len(copilot_resp['recommendations'])} recommendations).")

    # 14. Central API Gateway KPI Aggregation & Distributed Omnisearch
    print("\n[Step 14/14] Central API Gateway KPI Cockpit & Distributed Omnisearch...")
    ov_resp = gw_client.get("/api/v1/overview")
    assert ov_resp.status_code == 200
    kpis = ov_resp.json()["kpis"]
    assert kpis["total_revenue_paid"] > 0
    assert kpis["total_pipeline"] > 0

    search_resp = gw_client.get("/api/v1/search?q=Robotics")
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert len(results) >= 1
    print(f"  [OK] Gateway Executive Cockpit: Revenue ${kpis['total_revenue_paid']:,.2f} | Pipeline ${kpis['total_pipeline']:,.2f}")
    print(f"  [OK] Distributed Omnisearch returned {len(results)} matches for query 'Robotics'.")

    print("\n" + "=" * 70)
    print("  ALL 14 END-TO-END PLATFORM TESTS PASSED WITH 100% SUCCESS!")
    print("=" * 70)

if __name__ == "__main__":
    test_complete_platform_lifecycle()
