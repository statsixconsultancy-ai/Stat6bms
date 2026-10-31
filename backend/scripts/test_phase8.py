#!/usr/bin/env python3
"""
Test Suite for Phase 8: Financial Core — Finance & Double-Entry Ledger Microservice
Validates multi-line invoicing, invoice settlement, balanced double-entry
general ledger (Debit Cash == Credit AR), P&L reports, and webhook event integrations.
"""
import os
import sys
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.finance_service.main import app as finance_app, on_startup

# Ensure tables and seed data
on_startup()
client = TestClient(finance_app)

def test_finance_health():
    print("[1/6] Testing Finance Microservice Health Endpoint...")
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "finance-service"
    assert data["status"] == "UP"
    assert data["port"] == 8006
    print("  [OK] Finance Service /health endpoint validated successfully.")

def test_invoices_listing_and_creation():
    print("[2/6] Testing Invoices Listing & Multi-Line Invoicing...")
    resp = client.get("/finance/invoices")
    invoices = resp.json() if resp.status_code == 200 else []
    if len(invoices) < 3:
        for idx in range(len(invoices), 3):
            client.post("/finance/invoices", json={
                "client_name": f"Enterprise Client {idx+1}",
                "issue_date": "2026-09-24",
                "due_date": "2026-10-24",
                "items": [{"description": "Cloud Service", "quantity": 1, "unit_price": 10000.0 * (idx + 1)}]
            })
        resp = client.get("/finance/invoices")
        invoices = resp.json()
    assert resp.status_code == 200
    assert len(invoices) >= 3

    # Create new invoice
    new_inv_payload = {
        "client_name": "Helios Solar Dynamics",
        "deal_id": "DEAL-SOLAR-09",
        "issue_date": "2026-09-24",
        "due_date": "2026-10-24",
        "items": [
            {"description": "Grid Edge Telemetry Controller (10 Units)", "quantity": 10, "unit_price": 5000.0},
            {"description": "Field Calibration & Onsite Integration", "quantity": 1, "unit_price": 15000.0}
        ]
    }
    create_resp = client.post("/finance/invoices", json=new_inv_payload)
    assert create_resp.status_code == 200
    created = create_resp.json()
    assert created["subtotal"] == 65000.0
    assert created["total_amount"] >= 65000.0
    assert created["balance_due"] >= 65000.0
    print(f"  [OK] Created invoice {created['invoice_number']} for ${created['total_amount']:,.2f}.")
    return created["id"]

def test_settle_invoice_payment_and_double_entry_ledger(invoice_id: str):
    print("[3/6] Testing Payment Settlement & Zero-Discrepancy Double-Entry Ledger...")
    inv_data = client.get(f"/finance/invoices/{invoice_id}").json()
    full_amt = inv_data["total_amount"]
    pay_payload = {
        "amount": full_amt,
        "payment_method": "Wire Transfer",
        "reference_number": "WIRE-HELIOS-991"
    }
    pay_resp = client.post(f"/finance/invoices/{invoice_id}/pay", json=pay_payload)
    assert pay_resp.status_code == 200
    payment = pay_resp.json()
    assert payment["amount"] == full_amt

    # Verify invoice is now fully Paid
    inv_resp = client.get(f"/finance/invoices/{invoice_id}")
    assert inv_resp.status_code == 200
    inv = inv_resp.json()
    assert inv["status"] == "Paid"
    assert inv["balance_due"] == 0.0

    # Verify General Ledger reflects balanced entry
    ledger_resp = client.get("/finance/ledger")
    assert ledger_resp.status_code == 200
    entries = ledger_resp.json()
    payment_entries = [e for e in entries if e["reference_id"] == invoice_id]
    assert len(payment_entries) >= 1
    je = payment_entries[0]
    assert je["is_balanced"] == True
    assert je["total_debit"] == full_amt
    assert je["total_credit"] == full_amt

    # Verify ledger lines (Debit 1010 Cash, Credit 1200 AR)
    codes = {l["account_code"]: (l["debit"], l["credit"]) for l in je["lines"]}
    assert "1010" in codes and codes["1010"][0] == full_amt  # Debit Cash
    assert "1200" in codes and codes["1200"][1] == full_amt  # Credit AR
    print(f"  [OK] Settle invoice completed: General Ledger {je['entry_number']} balanced (Debit Cash ${full_amt:,.2f} == Credit AR ${full_amt:,.2f}).")

def test_operating_expenses():
    print("[4/6] Testing Operating Expenses Management...")
    exp_payload = {
        "category": "Cloud Hosting & Infrastructure",
        "vendor": "Google Cloud Platform",
        "amount": 12800.0,
        "date": "2026-09-24",
        "approved_by": "Elena Rostova"
    }
    create_resp = client.post("/finance/expenses", json=exp_payload)
    assert create_resp.status_code == 200
    exp = create_resp.json()
    assert exp["amount"] == 12800.0
    assert exp["status"] == "Approved"
    print(f"  [OK] Recorded expense ${exp['amount']:,.2f} for {exp['vendor']}.")

def test_profit_and_loss_report():
    print("[5/6] Testing Financial Reports: P&L Statement & Cash Flow...")
    pnl_resp = client.get("/finance/reports/p-and-l")
    assert pnl_resp.status_code == 200
    pnl = pnl_resp.json()
    assert pnl["operating_revenue"] > 0
    assert pnl["gross_profit"] > 0
    assert pnl["ebitda"] > 0
    assert pnl["net_operating_margin_percent"] > 0

    cf_resp = client.get("/finance/reports/cash-flow")
    assert cf_resp.status_code == 200
    cf = cf_resp.json()
    assert cf["cash_at_start"] > 0
    assert cf["cash_at_close"] > 0
    print(f"  [OK] P&L Verified: Revenue ${pnl['operating_revenue']:,.2f} | EBITDA ${pnl['ebitda']:,.2f} (Margin: {pnl['net_operating_margin_percent']}%) | Closing Cash ${cf['cash_at_close']:,.2f}")

def test_deal_won_and_payroll_event_webhooks():
    print("[6/6] Testing Cross-Service Event Webhooks (deal.won & payroll.executed)...")
    # 1. deal.won -> auto-draft Net30 invoice
    deal_event = {
        "event_name": "deal.won",
        "payload": {
            "deal_id": "DEAL-ORION-01",
            "title": "Orion Cloud Satellite Link",
            "amount": 220000.0,
            "company_name": "Orion Space Systems"
        },
        "org_id": "org-acroflow-main"
    }
    deal_resp = client.post("/webhooks/events", json=deal_event)
    assert deal_resp.status_code == 200
    assert deal_resp.json()["status"] == "invoice_drafted"

    # 2. payroll.executed -> auto-book expense
    pay_event = {
        "event_name": "payroll.executed",
        "payload": {
            "period_name": "September 2026",
            "total_net": 64533.34
        },
        "org_id": "org-acroflow-main"
    }
    pay_resp = client.post("/webhooks/events", json=pay_event)
    assert pay_resp.status_code == 200
    assert pay_resp.json()["status"] == "payroll_booked"
    print("  [OK] 'deal.won' auto-drafted invoice and 'payroll.executed' auto-booked talent expense successfully.")

def main():
    print("=" * 65)
    print("  BMS PHASE 8: FINANCE & DOUBLE-ENTRY LEDGER TEST SUITE")
    print("=" * 65)
    test_finance_health()
    inv_id = test_invoices_listing_and_creation()
    test_settle_invoice_payment_and_double_entry_ledger(inv_id)
    test_operating_expenses()
    test_profit_and_loss_report()
    test_deal_won_and_payroll_event_webhooks()
    print("=" * 65)
    print("  ALL PHASE 8 AUTOMATED TESTS PASSED SUCCESSFULLY! (6/6)")
    print("=" * 65)

if __name__ == "__main__":
    main()
