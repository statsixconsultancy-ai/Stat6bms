#!/usr/bin/env python3
"""
Test Suite for Phase 2: Central API Gateway
Validates reverse proxying, event relaying, aggregated overview, and distributed search.
"""
import os
import sys
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.gateway.main import app

client = TestClient(app)

def test_gateway_health():
    print("[1/5] Testing Gateway Health Endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["gateway"] == "HEALTHY"
    assert data["port"] == 8000
    assert "crm" in data["services"]
    assert "finance" in data["services"]
    print("  [OK] Gateway /health endpoint validated successfully.")

def test_event_broker():
    print("[2/5] Testing Gateway Event Relay Hub...")
    # 1. Subscribe mock webhook
    sub_resp = client.post("/events/subscribe", json={
        "event_name": "deal.won",
        "webhook_url": "http://127.0.0.1:8006/webhooks/events"
    })
    assert sub_resp.status_code == 200
    assert sub_resp.json()["status"] == "subscribed"

    # 2. Publish event
    pub_resp = client.post("/events/publish", json={
        "event_name": "deal.won",
        "payload": {"deal_id": "DEAL-999", "amount": 250000.0, "client": "Global Tech Corp"},
        "org_id": "org-acroflow"
    })
    assert pub_resp.status_code == 200
    assert pub_resp.json()["status"] == "published"
    assert pub_resp.json()["subscribers_notified"] >= 1

    # 3. Check event history
    hist_resp = client.get("/events/history")
    assert hist_resp.status_code == 200
    assert hist_resp.json()["count"] >= 1
    print("  [OK] Gateway Event Broker registration and dispatch verified.")

def test_executive_overview():
    print("[3/5] Testing Gateway Aggregated Overview (/api/v1/overview)...")
    resp = client.get("/api/v1/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "kpis" in data
    kpis = data["kpis"]
    assert "total_revenue_paid" in kpis
    assert "total_pipeline" in kpis
    assert "overdue_receivables" in kpis
    assert "active_projects" in kpis
    assert "open_tickets" in kpis
    assert kpis["total_revenue_paid"] > 0
    assert kpis["total_pipeline"] > 0
    print("  [OK] Aggregated Executive Overview returns expected KPI payload.")

def test_distributed_omnisearch():
    print("[4/5] Testing Gateway Distributed Omnisearch (/api/v1/search)...")
    resp = client.get("/api/v1/search?q=Stripe")
    assert resp.status_code == 200
    results = resp.json()
    assert isinstance(results, list)
    assert len(results) >= 1
    first = results[0]
    assert "title" in first
    assert "type" in first
    assert "category" in first
    assert "Stripe" in first["title"]
    print("  [OK] Distributed Omnisearch returned relevant results.")

def test_reverse_proxy_validation():
    print("[5/5] Testing Reverse Proxy Validation & Routing Error Guards...")
    # Unknown module check
    resp = client.get("/api/v1/unknown_module/endpoint")
    assert resp.status_code == 404
    assert "not registered" in resp.json()["detail"]

    # Offline downstream service error guard
    from services.gateway.main import SERVICE_ROUTES
    SERVICE_ROUTES["dummy_offline"] = "http://127.0.0.1:59999"
    try:
        offline_resp = client.get("/api/v1/dummy_offline/test")
        assert offline_resp.status_code == 503
        assert "offline or unreachable" in offline_resp.json()["detail"]
    finally:
        SERVICE_ROUTES.pop("dummy_offline", None)
    print("  [OK] Reverse proxy routing guards and downstream error handling verified.")

def main():
    print("=" * 65)
    print("  BMS PHASE 2: API GATEWAY VALIDATION TEST SUITE")
    print("=" * 65)
    test_gateway_health()
    test_event_broker()
    test_executive_overview()
    test_distributed_omnisearch()
    test_reverse_proxy_validation()
    print("=" * 65)
    print("  ALL PHASE 2 AUTOMATED TESTS PASSED SUCCESSFULLY! (5/5)")
    print("=" * 65)

if __name__ == "__main__":
    main()
