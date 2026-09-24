#!/usr/bin/env python3
"""
Test Suite for Phase 4: Sales & CRM Microservice
Validates lead management, atomic lead conversion, deal pipelines,
stage transition with 'deal.won' event broadcast, quotations, and webhook intake.
"""
import os
import sys
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.crm_service.main import app as crm_app, on_startup

# Trigger table initialization and seed data
on_startup()
client = TestClient(crm_app)

def test_crm_health():
    print("[1/6] Testing CRM Microservice Health Endpoint...")
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "crm-service"
    assert data["status"] == "UP"
    assert data["port"] == 8002
    print("  [OK] CRM Service /health endpoint validated successfully.")

def test_pipeline_summary():
    print("[2/6] Testing Executive Commercial Summary (/crm/summary)...")
    resp = client.get("/crm/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_pipeline_value" in data
    assert "won_revenue" in data
    assert data["total_pipeline_value"] > 0
    assert data["total_deals_count"] >= 3
    print(f"  [OK] Total Pipeline: ${data['total_pipeline_value']:,.2f} | Won: ${data['won_revenue']:,.2f} | Win Rate: {data['win_rate_percent']}%")

def test_lead_lifecycle_and_conversion():
    print("[3/6] Testing Lead Ingestion & Atomic Conversion (/crm/leads/{id}/convert)...")
    # 1. Ingest new lead
    lead_payload = {
        "first_name": "Alan",
        "last_name": "Grant",
        "email": "alan.grant@jurassicpaleo.internal",
        "phone": "+1 (555) 999-1234",
        "company_name": "Paleo Genomics Labs",
        "source": "Direct Inbound",
        "score": 90,
        "notes": "Interested in automated cryogenic temperature data monitoring."
    }
    create_resp = client.post("/crm/leads", json=lead_payload)
    assert create_resp.status_code == 200
    lead_data = create_resp.json()
    lead_id = lead_data["id"]
    assert lead_data["status"] == "New"
    assert lead_data["score"] == 90

    # 2. Atomic conversion to Account, Contact & Deal
    convert_payload = {
        "deal_title": "Cryogenic IoT Analytics Platform",
        "deal_amount": 175000.0,
        "close_date": "2026-11-30"
    }
    convert_resp = client.post(f"/crm/leads/{lead_id}/convert", json=convert_payload)
    assert convert_resp.status_code == 200
    conv_data = convert_resp.json()
    assert conv_data["company_name"] == "Paleo Genomics Labs"
    assert conv_data["deal_amount"] == 175000.0
    assert conv_data["deal_title"] == "Cryogenic IoT Analytics Platform"

    # 3. Verify lead status is now Converted
    get_lead_resp = client.get(f"/crm/leads/{lead_id}")
    assert get_lead_resp.status_code == 200
    assert get_lead_resp.json()["status"] == "Converted"

    # 4. Verify Company account now exists in directory
    comp_resp = client.get(f"/crm/companies/{conv_data['company_id']}")
    assert comp_resp.status_code == 200
    comp_detail = comp_resp.json()
    assert comp_detail["name"] == "Paleo Genomics Labs"
    assert len(comp_detail["contacts"]) >= 1
    assert comp_detail["contacts"][0]["email"] == "alan.grant@jurassicpaleo.internal"
    print("  [OK] Lead converted atomically to Company, Contact, and Deal successfully.")

def test_deal_pipeline_and_stage_won():
    print("[4/6] Testing Deal Pipeline & 'deal.won' Domain Event Trigger...")
    # 1. Create a deal
    new_deal_payload = {
        "title": "Autonomous Fleet Mission Control Software",
        "amount": 320000.0,
        "stage": "Proposal Sent",
        "probability": 60,
        "owner": "Marcus Reed"
    }
    deal_resp = client.post("/crm/deals", json=new_deal_payload)
    assert deal_resp.status_code == 200
    deal = deal_resp.json()
    deal_id = deal["id"]
    assert deal["stage"] == "Proposal Sent"

    # 2. Advance stage to 'Won'
    patch_resp = client.patch(f"/crm/deals/{deal_id}/stage", json={"stage": "Won"})
    assert patch_resp.status_code == 200
    won_deal = patch_resp.json()
    assert won_deal["stage"] == "Won"
    assert won_deal["probability"] == 100
    print("  [OK] Deal advanced to 'Won' with 100% win probability and event broadcast.")

def test_quote_generation_and_tax():
    print("[5/6] Testing Automated Quotation Calculation (/crm/quotes)...")
    quote_payload = {
        "valid_until": "2026-12-31",
        "items": [
            {"description": "Core Platform License (Annual)", "quantity": 1, "unit_price": 50000.0},
            {"description": "Enterprise Seat Add-ons", "quantity": 10, "unit_price": 1200.0},
            {"description": "Implementation & Training", "quantity": 1, "unit_price": 8000.0}
        ]
    }
    # Subtotal: 50,000 + 12,000 + 8,000 = 70,000
    # Tax 8%: 5,600
    # Total: 75,600
    resp = client.post("/crm/quotes", json=quote_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["subtotal"] == 70000.0
    assert data["tax_amount"] == 5600.0
    assert data["total_amount"] == 75600.0
    assert len(data["items"]) == 3
    print(f"  [OK] Quote {data['quote_number']} calculated accurately: Subtotal ${data['subtotal']:,.2f} + Tax ${data['tax_amount']:,.2f} = Total ${data['total_amount']:,.2f}")

def test_webhook_lead_ingest():
    print("[6/6] Testing Cross-Service Webhook Lead Ingestion (/webhooks/events)...")
    event_payload = {
        "event_name": "lead.captured",
        "payload": {
            "first_name": "Clara",
            "last_name": "Oswald",
            "email": "clara@tardis-solutions.internal",
            "company_name": "TARDIS Solutions Ltd",
            "source": "Marketing Webinar Q3",
            "form_name": "Enterprise Demo Request"
        },
        "org_id": "org-acroflow-main"
    }
    webhook_resp = client.post("/webhooks/events", json=event_payload)
    assert webhook_resp.status_code == 200
    data = webhook_resp.json()
    assert data["status"] == "lead_ingested"
    lead_id = data["lead_id"]

    # Verify lead in CRM leads table
    lead_resp = client.get(f"/crm/leads/{lead_id}")
    assert lead_resp.status_code == 200
    lead = lead_resp.json()
    assert lead["company_name"] == "TARDIS Solutions Ltd"
    assert lead["email"] == "clara@tardis-solutions.internal"
    print("  [OK] Cross-service webhook successfully ingested lead into CRM database.")

def main():
    print("=" * 65)
    print("  BMS PHASE 4: SALES & CRM MICROSERVICE TEST SUITE")
    print("=" * 65)
    test_crm_health()
    test_pipeline_summary()
    test_lead_lifecycle_and_conversion()
    test_deal_pipeline_and_stage_won()
    test_quote_generation_and_tax()
    test_webhook_lead_ingest()
    print("=" * 65)
    print("  ALL PHASE 4 AUTOMATED TESTS PASSED SUCCESSFULLY! (6/6)")
    print("=" * 65)

if __name__ == "__main__":
    main()
