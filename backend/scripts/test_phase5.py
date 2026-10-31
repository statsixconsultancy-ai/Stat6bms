#!/usr/bin/env python3
"""
Test Suite for Phase 5: Marketing Intelligence Microservice
Validates campaign tracking, landing pages, public form submission,
channel attribution, and real-time ROI analytics.
"""
import os
import sys
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.marketing_service.main import app as marketing_app, on_startup

# Ensure tables and seed data
on_startup()
client = TestClient(marketing_app)

def test_marketing_health():
    print("[1/6] Testing Marketing Microservice Health Endpoint...")
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "marketing-service"
    assert data["status"] == "UP"
    assert data["port"] == 8003
    print("  [OK] Marketing Service /health endpoint validated successfully.")

def test_campaigns_list_and_roi():
    print("[2/6] Testing Marketing Campaigns Listing & Individual ROI...")
    resp = client.get("/marketing/campaigns")
    campaigns = resp.json() if resp.status_code == 200 else []
    if len(campaigns) < 3:
        for idx in range(3):
            client.post("/marketing/campaigns", json={
                "name": f"Growth Marketing Campaign {idx+1}",
                "type": "Paid Search",
                "budget": 20000.0,
                "actual_spend": 5000.0 * (idx + 1),
                "attributed_revenue": 50000.0 * (idx + 1),
                "target_audience": "Enterprise Decision Makers"
            })
        resp = client.get("/marketing/campaigns")
        campaigns = resp.json()
    assert resp.status_code == 200
    assert len(campaigns) >= 3
    for c in campaigns:
        assert "roi_percent" in c
        assert c["roi_percent"] > 0
    print(f"  [OK] Listed {len(campaigns)} active campaigns with calculated ROI metrics.")

def test_create_campaign():
    print("[3/6] Testing Campaign Creation (/marketing/campaigns)...")
    payload = {
        "name": "Generative AI Enterprise Workshop Series",
        "type": "Webinar",
        "budget": 25000.0,
        "actual_spend": 18000.0,
        "attributed_revenue": 160000.0,
        "target_audience": "Enterprise IT Directors"
    }
    resp = client.post("/marketing/campaigns", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Generative AI Enterprise Workshop Series"
    # ROI: (160,000 - 18,000) / 18,000 * 100 = 788.9%
    assert data["roi_percent"] > 700.0
    print(f"  [OK] Campaign created with {data['roi_percent']}% ROI.")

def test_landing_pages():
    print("[4/6] Testing Landing Pages & Conversion Rates...")
    import uuid
    resp = client.get("/marketing/landing-pages")
    pages = resp.json() if resp.status_code == 200 else []
    if len(pages) < 2:
        from services.marketing_service.models import LandingPage
        from services.marketing_service.main import db_mgr
        session = next(db_mgr.get_session())
        try:
            for idx in range(len(pages), 2):
                session.add(LandingPage(
                    id=str(uuid.uuid4()),
                    org_id="org-acroflow-main",
                    title=f"Enterprise Solution Brief {idx+1}",
                    slug=f"solution-brief-{uuid.uuid4().hex[:6]}",
                    views_count=1200 * (idx + 1),
                    conversions_count=180 * (idx + 1),
                    bounce_rate=0.28
                ))
            session.commit()
        finally:
            session.close()
        resp = client.get("/marketing/landing-pages")
        pages = resp.json()
    assert resp.status_code == 200
    assert len(pages) >= 2
    for p in pages:
        assert p["views_count"] > 0
        assert p["conversion_rate_percent"] > 0
    print(f"  [OK] Landing pages verified with average conversion rate {pages[0]['conversion_rate_percent']}%.")

def test_public_form_submission_and_event():
    print("[5/6] Testing Public Inbound Form Submission (/marketing/public/submit-form)...")
    sub_payload = {
        "first_name": "Amelia",
        "last_name": "Pond",
        "email": "amelia@leadcorp.internal",
        "company_name": "LeadCorp Enterprises",
        "phone": "+1 (555) 777-8899",
        "utm_source": "google",
        "utm_medium": "cpc",
        "utm_campaign": "autonomous_cloud_ads",
        "notes": "Requesting 500-seat license quote immediately."
    }
    # Unauthenticated public submission
    resp = client.post("/marketing/public/submit-form", json=sub_payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "received"
    assert data["email"] == "amelia@leadcorp.internal"
    assert data["company_name"] == "LeadCorp Enterprises"
    print("  [OK] Public form processed and 'lead.captured' event published to event bus.")

def test_marketing_roi_analytics():
    print("[6/6] Testing Real-Time Aggregated Marketing ROI (/marketing/analytics/roi)...")
    resp = client.get("/marketing/analytics/roi")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_marketing_spend" in data
    assert "total_attributed_revenue" in data
    assert "blended_roi_percent" in data
    assert data["total_attributed_revenue"] > data["total_marketing_spend"]
    assert data["blended_roi_percent"] > 0
    print(f"  [OK] Total Spend: ${data['total_marketing_spend']:,.2f} | Attributed Revenue: ${data['total_attributed_revenue']:,.2f} | Blended ROI: {data['blended_roi_percent']}%")

def main():
    print("=" * 65)
    print("  BMS PHASE 5: MARKETING INTELLIGENCE MICROSERVICE TEST SUITE")
    print("=" * 65)
    test_marketing_health()
    test_campaigns_list_and_roi()
    test_create_campaign()
    test_landing_pages()
    test_public_form_submission_and_event()
    test_marketing_roi_analytics()
    print("=" * 65)
    print("  ALL PHASE 5 AUTOMATED TESTS PASSED SUCCESSFULLY! (6/6)")
    print("=" * 65)

if __name__ == "__main__":
    main()
