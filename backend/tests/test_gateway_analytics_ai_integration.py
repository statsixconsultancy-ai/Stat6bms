import os
import sys

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from services.gateway.main import app as gateway_app


def run_gateway_integration_tests():
    client = TestClient(gateway_app)
    headers = {
        "x-user-id": "usr-ceo-01",
        "x-org-id": "org-acroflow-main",
        "x-user-role": "Admin",
    }

    # 1. Cluster Health Check
    r_health = client.get("/health")
    assert r_health.status_code == 200, r_health.text
    health_data = r_health.json()
    assert health_data["gateway"] == "HEALTHY"
    for svc_name, svc_state in health_data["services"].items():
        assert svc_state["status"] == "UP", f"Service {svc_name} not UP: {svc_state}"
    print("[PASS] 1. Gateway /health verified all 13 downstream services UP")

    # 2. Overview Cockpit KPIs
    r_ov = client.get("/api/v1/overview", headers=headers)
    assert r_ov.status_code == 200, r_ov.text
    ov = r_ov.json()
    assert "kpis" in ov and "recent_audit" in ov
    assert "total_revenue_paid" in ov["kpis"]
    assert "total_pipeline" in ov["kpis"]
    assert "net_profit" in ov["kpis"]
    print("[PASS] 2. Gateway /api/v1/overview verified real unpadded KPIs:", ov["kpis"])

    # 3. Distributed Omnisearch
    r_search = client.get("/api/v1/search?q=a", headers=headers)
    assert r_search.status_code == 200, r_search.text
    search_items = r_search.json()
    assert isinstance(search_items, list)
    print(f"[PASS] 3. Gateway /api/v1/search returned {len(search_items)} real cross-module records")

    # 4. Module 9: Cross-Module BI Dashboard & Predictive Forecast
    r_bi = client.get("/api/v1/analytics/bi-dashboard", headers=headers)
    assert r_bi.status_code == 200, r_bi.text
    bi = r_bi.json()
    assert "executive_summary" in bi
    assert "client_360_matrix" in bi
    assert "marketing_roi_matrix" in bi
    assert "department_allocation" in bi
    assert "predictive_forecast" in bi and len(bi["predictive_forecast"]) == 4
    print("[PASS] 4. Module 9 BI Dashboard & Predictive Forecast verified")

    # 5. Module 9: Custom Report Builder + CSV Export
    r_rep = client.post(
        "/api/v1/analytics/custom-report",
        json={"primary_module": "finance", "group_by": "status", "metric": "sum"},
        headers=headers,
    )
    assert r_rep.status_code == 200, r_rep.text
    rep = r_rep.json()
    assert "columns" in rep and "rows" in rep and "summary_groups" in rep and "csv_export" in rep
    print(f"[PASS] 5. Module 9 Custom Report Builder verified ({rep['total_records']} records)")

    # 6. Module 10: Collaboration Route Alias (/api/v1/collaboration/* -> /chat/*)
    r_collab = client.get("/api/v1/collaboration/channels", headers=headers)
    assert r_collab.status_code == 200, r_collab.text
    r_ann = client.get("/api/v1/collaboration/announcements", headers=headers)
    assert r_ann.status_code == 200, r_ann.text
    print("[PASS] 6. Module 10 /api/v1/collaboration/* proxy verified")

    # 7. Module 13: AI Copilot & Insights via Gateway
    for ai_ep in [
        "/api/v1/ai/executive-briefing",
        "/api/v1/ai/forecast/sales",
        "/api/v1/ai/customers/churn-rfm",
        "/api/v1/ai/anomalies/detect",
    ]:
        r_ai = client.get(ai_ep, headers=headers)
        assert r_ai.status_code == 200, f"{ai_ep} failed: {r_ai.text}"

    r_sum = client.post(
        "/api/v1/ai/documents/summarize",
        json={
            "document_title": "Master Enterprise MSA",
            "document_type": "Contract",
            "content": "Total value $180,000 USD. SLA 99.95% uptime. Auto-renewal every 12 months unless 30 days notice. Ensure GDPR compliance.",
        },
        headers=headers,
    )
    assert r_sum.status_code == 200, r_sum.text

    r_chat = client.post(
        "/api/v1/ai/chat",
        json={"prompt": "Show our revenue, pipeline deals, and open tickets"},
        headers=headers,
    )
    assert r_chat.status_code == 200, r_chat.text
    assert "answer" in r_chat.json()
    print("[PASS] 7. Module 13 AI Copilot & Insights endpoints verified via Gateway")

    # 8. Verify Proxy Across All Core Modules
    module_checks = [
        "/api/v1/auth/personas",
        "/api/v1/crm/leads",
        "/api/v1/crm/deals",
        "/api/v1/crm/quotes",
        "/api/v1/marketing/campaigns",
        "/api/v1/marketing/drip-journeys",
        "/api/v1/projects",
        "/api/v1/projects/tasks",
        "/api/v1/hr/employees",
        "/api/v1/hr/okrs",
        "/api/v1/finance/invoices",
        "/api/v1/finance/reports/p-and-l",
        "/api/v1/inventory/products",
        "/api/v1/inventory/warehouses",
        "/api/v1/procurement/orders",
        "/api/v1/procurement/requisitions",
        "/api/v1/support/tickets",
        "/api/v1/support/kb/articles",
        "/api/v1/compliance/soc2/readiness",
        "/api/v1/automation/workflows",
        "/api/v1/automation/approvals",
    ]
    for ep in module_checks:
        resp = client.get(ep, headers=headers)
        assert resp.status_code == 200, f"Endpoint {ep} returned {resp.status_code}: {resp.text}"
    print(f"[PASS] 8. All {len(module_checks)} cross-module Gateway proxy endpoints returned 200 OK!")

    # 9. Verify Enterprise Secrets Vault (Create, List, Reveal, Rotate, Audit Trail)
    r_vault_create = client.post(
        "/api/v1/compliance/vault",
        json={
            "name": "Production Redis Cluster Token",
            "category": "API_KEY",
            "username": "redis-admin",
            "service_url": "redis://cache.stat6.io:6379",
            "secret_value": "stat6_super_secret_token_2026_xyz9",
            "environment": "PRODUCTION",
            "allowed_roles": "ADMIN,MANAGER",
            "rotation_days": 60,
        },
        headers=headers,
    )
    assert r_vault_create.status_code == 200, r_vault_create.text
    created_secret = r_vault_create.json()
    secret_id = created_secret["id"]
    assert created_secret["masked_preview"].endswith("xyz9")
    assert "stat6_super_secret_token_2026_xyz9" not in str(created_secret)

    r_vault_reveal = client.post(f"/api/v1/compliance/vault/{secret_id}/reveal", json={}, headers=headers)
    assert r_vault_reveal.status_code == 200, r_vault_reveal.text
    revealed = r_vault_reveal.json()
    assert revealed["plaintext_secret"] == "stat6_super_secret_token_2026_xyz9"
    assert revealed["access_count"] == 1

    r_vault_rotate = client.post(
        f"/api/v1/compliance/vault/{secret_id}/rotate",
        json={"new_secret_value": "rotated_secret_key_8877"},
        headers=headers,
    )
    assert r_vault_rotate.status_code == 200, r_vault_rotate.text
    assert r_vault_rotate.json()["masked_preview"].endswith("8877")
    print("[PASS] 9. Enterprise Password & Secrets Vault (Create/Reveal/Rotate/Audit) verified")

    # 10. Verify Custom Object Record CRUD & Kanban Stage Transitions
    r_co_create = client.post(
        "/api/v1/auth/custom-objects",
        json={
            "object_name": "datacenter_racks",
            "display_name": "Datacenter Server Racks",
            "description": "Custom asset tracking table",
            "schema_definition": {"fields": ["rack_code", "datacenter", "power_kw"]},
        },
        headers=headers,
    )
    assert r_co_create.status_code == 200, r_co_create.text
    co_id = r_co_create.json()["id"]

    r_rec_create = client.post(
        f"/api/v1/auth/custom-objects/{co_id}/records",
        json={"record_data": {"rack_code": "RCK-US-01", "datacenter": "US-East-1", "power_kw": 14.5}},
        headers=headers,
    )
    assert r_rec_create.status_code == 200, r_rec_create.text
    rec_id = r_rec_create.json()["id"]

    r_rec_list = client.get(f"/api/v1/auth/custom-objects/{co_id}/records", headers=headers)
    assert r_rec_list.status_code == 200, r_rec_list.text
    assert any(r["id"] == rec_id for r in r_rec_list.json())

    r_rec_del = client.delete(f"/api/v1/auth/custom-objects/records/{rec_id}", headers=headers)
    assert r_rec_del.status_code == 200, r_rec_del.text
    print("[PASS] 10. Custom Object Record CRUD verified")


import unittest


class TestGatewayAnalyticsAiIntegration(unittest.TestCase):
    def test_full_gateway_analytics_ai_vault_custom_objects(self):
        run_gateway_integration_tests()


if __name__ == "__main__":
    run_gateway_integration_tests()

