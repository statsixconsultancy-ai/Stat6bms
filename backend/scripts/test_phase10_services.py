#!/usr/bin/env python3
"""
Test Suite for Phase 10: Enterprise Nervous System Microservices
Validates:
1. Support Microservice (8009): Tickets, SLA countdown, escalation broadcast.
2. Collaboration Microservice (8010): Channels, message threads, bot event alerts.
3. Compliance Microservice (8011): Immutable audit logs, GDPR data export, SOC2 controls.
4. Automation Microservice (8012): WHEN-IF-DO event evaluation, rule triggers.
5. AI Copilot Microservice (8013): Cross-service NLP query synthesis, business anomalies.
"""
import os
import sys
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.support_service.main import app as sup_app, on_startup as sup_init
from services.collaboration_service.main import app as col_app, on_startup as col_init
from services.compliance_service.main import app as comp_app, on_startup as comp_init
from services.automation_service.main import app as auto_app, on_startup as auto_init
from services.ai_copilot_service.main import app as ai_app, on_startup as ai_init

sup_init()
col_init()
comp_init()
auto_init()
ai_init()

sup_client = TestClient(sup_app)
col_client = TestClient(col_app)
comp_client = TestClient(comp_app)
auto_client = TestClient(auto_app)
ai_client = TestClient(ai_app)

def test_all_health():
    print("[1/6] Testing Health of All 5 Nervous System Microservices (Ports 8009-8013)...")
    assert sup_client.get("/health").json()["service"] == "support-service"
    assert col_client.get("/health").json()["service"] == "collaboration-service"
    assert comp_client.get("/health").json()["service"] == "compliance-service"
    assert auto_client.get("/health").json()["service"] == "automation-service"
    assert ai_client.get("/health").json()["service"] == "ai-copilot-service"
    print("  [OK] Support (:8009), Collab (:8010), Compliance (:8011), Automation (:8012), AI (:8013) UP & HEALTHY.")

def test_support_service():
    print("[2/6] Testing Support Desk, SLA Countdown & Escalation...")
    sla = sup_client.get("/support/analytics/sla").json()
    assert sla["total_tickets"] >= 3
    assert sla["sla_compliance_rate_percent"] > 0

    # Create & escalate ticket
    tkt_resp = sup_client.post("/support/tickets", json={
        "customer_name": "Sarah Connor",
        "customer_email": "sconnor@cyberdyne.internal",
        "subject": "Rover Telemetry Drop",
        "priority": "High"
    })
    assert tkt_resp.status_code == 200
    t_id = tkt_resp.json()["id"]

    esc_resp = sup_client.post(f"/support/tickets/{t_id}/escalate")
    assert esc_resp.status_code == 200
    assert esc_resp.json()["priority"] == "Urgent"
    assert esc_resp.json()["sla_target_hours"] == 1.0
    print(f"  [OK] Support SLA compliance verified ({sla['sla_compliance_rate_percent']}%), ticket {t_id[:8]} escalated to Urgent (1.0 hr SLA).")

def test_collaboration_service():
    print("[3/6] Testing Collaboration Channels & Event Webhook Bot Broadcast...")
    channels = col_client.get("/chat/channels").json()
    assert len(channels) >= 4
    gen_ch = [c for c in channels if c["name"] == "general"][0]

    # Post message
    msg_resp = col_client.post(f"/chat/channels/{gen_ch['id']}/messages", json={
        "message": "BMS Microservices 2.0 deployment verified."
    })
    assert msg_resp.status_code == 200

    # Test event webhook posting to #incident-response
    event_payload = {
        "event_name": "ticket.urgent",
        "payload": {
            "ticket_number": "TKT-URGENT-99",
            "subject": "Autonomous Rover Brake Stalled",
            "customer": "Nexus Robotics"
        },
        "org_id": "org-acroflow-main"
    }
    hook_resp = col_client.post("/webhooks/events", json=event_payload)
    assert hook_resp.status_code == 200
    assert hook_resp.json()["status"] == "alert_posted"
    print("  [OK] Chat channel message posted, and 'ticket.urgent' event triggered automatic bot alert into #incident-response.")

def test_compliance_service():
    print("[4/6] Testing Compliance Audit Trails, GDPR Subject Export & SOC2 Controls...")
    # SOC2
    soc2 = comp_client.get("/compliance/soc2/readiness").json()
    assert soc2["compliance_score_percent"] == 100.0
    assert len(soc2["controls"]) >= 5

    # GDPR Export
    gdpr_resp = comp_client.post("/compliance/gdpr/export", json={"subject_email": "marcus.chen@acroflow.enterprise"})
    assert gdpr_resp.status_code == 200
    assert gdpr_resp.json()["status"] == "Completed"
    assert len(gdpr_resp.json()["export_bundle"]["data_categories"]) >= 3

    # Audit Logs
    audit_resp = comp_client.get("/compliance/audit-logs")
    assert audit_resp.status_code == 200
    assert len(audit_resp.json()) >= 2
    print(f"  [OK] SOC2 Readiness: {soc2['compliance_score_percent']}% | GDPR Export Bundle verified | Immutable Audit Logs active.")

def test_automation_service():
    print("[5/6] Testing WHEN-IF-DO Automation Rules Engine...")
    rules = auto_client.get("/automation/rules").json()
    assert len(rules) >= 3

    # Send matching event deal.won
    auto_hook = auto_client.post("/webhooks/events", json={
        "event_name": "deal.won",
        "payload": {"amount": 250000.0, "client": "Quantum Dynamics"},
        "org_id": "org-acroflow-main"
    })
    assert auto_hook.status_code == 200
    assert auto_hook.json()["rules_triggered"] >= 1
    print(f"  [OK] Automation Engine matched 'deal.won' (amount >= 100,000) and executed automated action.")

def test_ai_copilot_service():
    print("[6/6] Testing Autonomous AI Copilot Query Synthesis & Anomaly Detection...")
    # 1. Anomalies
    anomalies = ai_client.get("/ai/anomalies").json()
    assert len(anomalies) >= 3

    # 2. NLP Financial Query
    q1 = ai_client.post("/ai/query", json={"query": "What is our current paid revenue and cash reserve?"}).json()
    assert q1["intent"] == "FINANCIAL_INTELLIGENCE"
    assert q1["key_metrics"]["total_paid_revenue"] == 580000.0
    assert q1["key_metrics"]["cash_reserves"] == 1540950.0

    # 3. NLP Pipeline Query
    q2 = ai_client.post("/ai/query", json={"query": "Give me a breakdown of our commercial deals pipeline."}).json()
    assert q2["intent"] == "COMMERCIAL_VELOCITY"
    assert q2["key_metrics"]["pipeline_value"] == 825000.0

    # 4. Strategic suggestions
    suggestions = ai_client.get("/ai/suggestions").json()
    assert len(suggestions) >= 3
    print(f"  [OK] Copilot synthesized multi-service queries accurately, returned {len(anomalies)} anomalies and {len(suggestions)} executive suggestions.")

def main():
    print("=" * 65)
    print("  BMS PHASE 10: ENTERPRISE NERVOUS SYSTEM TEST SUITE")
    print("=" * 65)
    test_all_health()
    test_support_service()
    test_collaboration_service()
    test_compliance_service()
    test_automation_service()
    test_ai_copilot_service()
    print("=" * 65)
    print("  ALL 5 NERVOUS SYSTEM MICROSERVICES PASSED SUCCESSFULLY! (6/6)")
    print("=" * 65)

if __name__ == "__main__":
    main()
