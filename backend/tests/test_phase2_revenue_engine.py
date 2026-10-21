import os
import sys
import unittest
from datetime import datetime
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.crm_service.main import app as crm_app
from services.marketing_service.main import app as marketing_app
from services.support_service.main import app as support_app

class TestPhase2RevenueEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.crm_client = TestClient(crm_app)
        cls.mkt_client = TestClient(marketing_app)
        cls.sup_client = TestClient(support_app)
        cls.headers = {
            "x-user-id": "usr-sales-001",
            "x-org-id": "org-stat6-rev-test",
            "x-user-role": "admin",
            "x-user-email": "rev-lead@stat6.enterprise"
        }

    # =========================================================================
    # 1. Sales & CRM Engine Tests
    # =========================================================================
    def test_01_lead_creation_and_atomic_qualification(self):
        lead_payload = {
            "first_name": "Elon",
            "last_name": "Musk",
            "email": "elon@xcorp.test",
            "phone": "+1-800-555-0199",
            "company_name": "X Corp Enterprise",
            "source": "Inbound Demo",
            "score": 92,
            "assigned_to": "Enterprise AE",
            "notes": "Looking to migrate 5,000 seats from Zoho One."
        }
        create_resp = self.crm_client.post("/crm/leads", json=lead_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        lead_data = create_resp.json()
        lead_id = lead_data["id"]
        self.assertEqual(lead_data["status"], "New")
        self.assertEqual(lead_data["score"], 92)

        # Atomic Qualification
        conv_payload = {
            "deal_title": "X Corp - STAT6 Enterprise Suite",
            "deal_amount": 250000.0,
            "close_date": "2026-12-31"
        }
        conv_resp = self.crm_client.post(f"/crm/leads/{lead_id}/convert", json=conv_payload, headers=self.headers)
        self.assertEqual(conv_resp.status_code, 200)
        conv_data = conv_resp.json()

        self.assertIsNotNone(conv_data.get("company_id"))
        self.assertIsNotNone(conv_data.get("contact_id"))
        self.assertIsNotNone(conv_data.get("deal_id"))
        self.assertEqual(conv_data["company_name"], "X Corp Enterprise")
        self.assertEqual(conv_data["deal_amount"], 250000.0)

        # Verify Lead record is marked Converted and holds references
        lead_check = self.crm_client.get(f"/crm/leads/{lead_id}", headers=self.headers)
        self.assertEqual(lead_check.status_code, 200)
        self.assertEqual(lead_check.json()["status"], "Converted")
        self.assertEqual(lead_check.json()["converted_deal_id"], conv_data["deal_id"])

    def test_02_customizable_pipelines_and_stages(self):
        pipeline_payload = {
            "name": "Enterprise Strategic Deals",
            "stages": [
                {"name": "Discovery", "order": 1, "probability": 20},
                {"name": "Solution Presentation", "order": 2, "probability": 40},
                {"name": "Security & Architecture Review", "order": 3, "probability": 70},
                {"name": "Contract Execution", "order": 4, "probability": 90},
                {"name": "Closed Won", "order": 5, "probability": 100}
            ]
        }
        create_resp = self.crm_client.post("/crm/pipelines", json=pipeline_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        p_data = create_resp.json()
        self.assertEqual(p_data["name"], "Enterprise Strategic Deals")
        self.assertEqual(len(p_data["stages"]), 5)

        # List pipelines
        list_resp = self.crm_client.get("/crm/pipelines", headers=self.headers)
        self.assertEqual(list_resp.status_code, 200)
        self.assertTrue(any(p["name"] == "Enterprise Strategic Deals" for p in list_resp.json()))

    def test_03_appointment_scheduling(self):
        appt_payload = {
            "title": "Technical Architecture Deep Dive",
            "host_email": "solutions-architect@stat6.enterprise",
            "guest_name": "CTO Jane Doe",
            "guest_email": "cto@megacorp.test",
            "scheduled_time": "2026-11-15T14:00:00Z",
            "duration_minutes": 45,
            "meeting_link": "https://meet.stat6.enterprise/arch-deep-dive-01"
        }
        create_resp = self.crm_client.post("/crm/appointments", json=appt_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        appt = create_resp.json()
        self.assertEqual(appt["guest_name"], "CTO Jane Doe")
        self.assertEqual(appt["duration_minutes"], 45)

        # List appointments
        list_resp = self.crm_client.get("/crm/appointments", headers=self.headers)
        self.assertEqual(list_resp.status_code, 200)
        self.assertTrue(any(a["id"] == appt["id"] for a in list_resp.json()))

    def test_04_cpq_quote_and_cryptographic_esign(self):
        # Create quote
        quote_payload = {
            "quote_number": f"QUO-2026-{int(datetime.utcnow().timestamp())}",
            "company_name": "Acme Innovations Ltd",
            "total_amount": 120000.0,
            "status": "Draft",
            "line_items": [
                {"item": "STAT6 Enterprise License - 250 Seats", "quantity": 250, "unit_price": 400.0, "total": 100000.0},
                {"item": "Premium 24/7 SLA Support", "quantity": 1, "unit_price": 20000.0, "total": 20000.0}
            ]
        }
        create_resp = self.crm_client.post("/crm/quotes", json=quote_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        quote = create_resp.json()
        quote_id = quote["id"]
        self.assertEqual(quote["e_signature_status"], "Pending")

        # Execute Cryptographic E-Signature
        sign_payload = {
            "signer_name": "Alice Walker",
            "signer_email": "alice@acme-innovations.test",
            "signer_role": "Chief Financial Officer",
            "ip_address": "198.51.100.42"
        }
        sign_resp = self.crm_client.post(f"/crm/quotes/{quote_id}/e-sign", json=sign_payload, headers=self.headers)
        self.assertEqual(sign_resp.status_code, 200)
        sign_data = sign_resp.json()

        self.assertEqual(sign_data["e_signature_status"], "Signed")
        self.assertEqual(sign_data["signer_email"], "alice@acme-innovations.test")
        self.assertTrue(len(sign_data["e_signature_audit_hash"]) >= 64)  # Valid SHA-256 hash length

    def test_05_deal_to_invoice_and_project_conversion(self):
        # Create deal
        deal_payload = {
            "title": "Quantum Compute - STAT6 Platform Expansion",
            "amount": 180000.0,
            "stage": "Proposal/Price Quote",
            "probability": 75,
            "close_date": "2026-12-15"
        }
        create_resp = self.crm_client.post("/crm/deals", json=deal_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        deal_id = create_resp.json()["id"]

        # 1. Convert Deal to Invoice
        inv_conv_resp = self.crm_client.post(f"/crm/deals/{deal_id}/convert-to-invoice", headers=self.headers)
        self.assertEqual(inv_conv_resp.status_code, 200)
        inv_data = inv_conv_resp.json()
        self.assertIn("invoice_id", inv_data)
        self.assertEqual(inv_data["deal_id"], deal_id)

        # 2. Convert Deal to Project
        proj_conv_resp = self.crm_client.post(f"/crm/deals/{deal_id}/convert-to-project", headers=self.headers)
        self.assertEqual(proj_conv_resp.status_code, 200)
        proj_data = proj_conv_resp.json()
        self.assertIn("project_id", proj_data)
        self.assertEqual(proj_data["deal_id"], deal_id)

    # =========================================================================
    # 2. Marketing Intelligence & Omnichannel Lead Engine Tests
    # =========================================================================
    def test_06_campaign_spend_and_revenue_tracking(self):
        camp_payload = {
            "name": "Q4 Google Search - Enterprise ERP Replacement",
            "type": "Paid Search",
            "status": "Active",
            "budget": 50000.0,
            "actual_spend": 28500.0,
            "attributed_revenue": 142500.0,
            "target_audience": "Chief Information Officers & VP Engineering"
        }
        create_resp = self.mkt_client.post("/marketing/campaigns", json=camp_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        camp = create_resp.json()
        self.assertEqual(camp["name"], "Q4 Google Search - Enterprise ERP Replacement")
        self.assertAlmostEqual(camp["roi_percent"], 400.0, places=1)

    def test_07_public_inbound_lead_capture_and_utm(self):
        lead_submit = {
            "first_name": "Devin",
            "last_name": "Vance",
            "email": "devin@globex.test",
            "company_name": "Globex Systems",
            "phone": "+1-555-897-4411",
            "utm_source": "linkedin",
            "utm_medium": "paid_social",
            "utm_campaign": "q4_erp_replacement",
            "notes": "Requesting 100-user migration trial."
        }
        submit_resp = self.mkt_client.post("/marketing/public/submit-form", json=lead_submit)
        self.assertEqual(submit_resp.status_code, 200)
        sub_data = submit_resp.json()
        self.assertEqual(sub_data["status"], "received")
        self.assertEqual(sub_data["email"], "devin@globex.test")

    def test_08_drip_journeys_and_automated_sequences(self):
        drip_payload = {
            "name": "Enterprise High-Intent Inbound Nurture",
            "trigger_event": "lead.captured",
            "steps_config": '[{"step": 1, "channel": "email", "delay_hours": 0, "template": "Whitepaper"}, {"step": 2, "channel": "whatsapp", "delay_hours": 24, "template": "VIP Demo"}]',
            "is_active": True
        }
        create_resp = self.mkt_client.post("/marketing/drip-journeys", json=drip_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        journey = create_resp.json()
        self.assertEqual(journey["name"], "Enterprise High-Intent Inbound Nurture")
        self.assertEqual(journey["enrolled_count"], 0)

        # Trigger enrollment
        trig_resp = self.mkt_client.post(f"/marketing/drip-journeys/{journey['id']}/trigger", headers=self.headers)
        self.assertEqual(trig_resp.status_code, 200)
        self.assertEqual(trig_resp.json()["enrolled_count"], 1)

    def test_09_broadcast_campaigns(self):
        bcast_payload = {
            "name": "STAT6 v2.0 General Availability Product Announcement",
            "channel": "email",
            "target_segment": "All B2B Decision Makers",
            "message_template": "We are proud to introduce STAT6 v2.0 - the unified business platform."
        }
        create_resp = self.mkt_client.post("/marketing/broadcasts", json=bcast_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        bcast = create_resp.json()
        self.assertEqual(bcast["status"], "Draft")

        # Send broadcast
        send_resp = self.mkt_client.post(f"/marketing/broadcasts/{bcast['id']}/send", headers=self.headers)
        self.assertEqual(send_resp.status_code, 200)
        sent_data = send_resp.json()
        self.assertEqual(sent_data["status"], "Sent")
        self.assertEqual(sent_data["recipient_count"], 150)
        self.assertGreater(sent_data["open_rate"], 40.0)

    def test_10_closed_loop_roi_attribution(self):
        # 1. Create campaign
        camp_resp = self.mkt_client.post("/marketing/campaigns", json={
            "name": "LinkedIn ABM Campaign",
            "budget": 20000.0,
            "actual_spend": 10000.0,
            "attributed_revenue": 0.0
        }, headers=self.headers)
        camp_id = camp_resp.json()["id"]

        # 2. Attribute closed deal revenue
        attr_payload = {
            "campaign_id": camp_id,
            "deal_id": "deal-closed-won-9988",
            "attributed_revenue": 80000.0,
            "attribution_model": "last_touch"
        }
        attr_resp = self.mkt_client.post("/marketing/roi-attribution", json=attr_payload, headers=self.headers)
        self.assertEqual(attr_resp.status_code, 200)
        attr_data = attr_resp.json()
        self.assertEqual(attr_data["new_attributed_revenue"], 80000.0)
        self.assertAlmostEqual(attr_data["calculated_roi_percent"], 700.0, places=1)

    # =========================================================================
    # 3. Customer Support & SLA Engine Tests
    # =========================================================================
    def test_11_ticket_creation_and_sla_calculation(self):
        # High priority ticket -> 4.0 hours SLA
        tkt_payload = {
            "customer_name": "Marcus Aurelius",
            "customer_email": "marcus@meditations.test",
            "subject": "Integration Webhook Timeout under Heavy Load",
            "description": "Our batch job is seeing 504 gateway timeouts on the CRM lead intake webhook.",
            "priority": "High"
        }
        resp = self.sup_client.post("/support/tickets", json=tkt_payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        tkt = resp.json()
        self.assertEqual(tkt["priority"], "High")
        self.assertEqual(tkt["sla_target_hours"], 4.0)
        self.assertEqual(tkt["is_breached"], False)

        # Urgent priority ticket -> 2.0 hours SLA
        urgent_payload = {
            "customer_name": "Marcus Aurelius",
            "customer_email": "marcus@meditations.test",
            "subject": "Production Payment Gateway Unreachable",
            "description": "Billing module cannot reach Stripe API.",
            "priority": "Urgent"
        }
        resp_urgent = self.sup_client.post("/support/tickets", json=urgent_payload, headers=self.headers)
        self.assertEqual(resp_urgent.status_code, 200)
        self.assertEqual(resp_urgent.json()["sla_target_hours"], 2.0)

    def test_12_ticket_messaging_and_executive_escalation(self):
        # Create ticket
        create_resp = self.sup_client.post("/support/tickets", json={
            "customer_name": "Sarah Connor",
            "customer_email": "sarah@cyberdyne.test",
            "subject": "Data Export Request stalled at 90%",
            "priority": "Medium"
        }, headers=self.headers)
        ticket_id = create_resp.json()["id"]

        # Add ticket messages
        msg1_resp = self.sup_client.post(f"/support/tickets/{ticket_id}/messages", json={
            "sender_name": "Support Agent Dave",
            "sender_type": "Agent",
            "message": "We have identified the locked background task and are restarting the export worker."
        }, headers=self.headers)
        self.assertEqual(msg1_resp.status_code, 200)

        # Escalate ticket to Executive Response Team
        esc_resp = self.sup_client.post(f"/support/tickets/{ticket_id}/escalate", headers=self.headers)
        self.assertEqual(esc_resp.status_code, 200)
        esc_data = esc_resp.json()
        self.assertEqual(esc_data["priority"], "Urgent")
        self.assertEqual(esc_data["sla_target_hours"], 1.0)
        self.assertEqual(esc_data["assigned_to"], "Executive Escalation Response Team")

    def test_13_ticket_csat_and_nps_ratings(self):
        # Create ticket
        create_resp = self.sup_client.post("/support/tickets", json={
            "customer_name": "Ada Lovelace",
            "customer_email": "ada@analytics.engine",
            "subject": "Query regarding Custom Field API Schema",
            "priority": "Low"
        }, headers=self.headers)
        ticket_id = create_resp.json()["id"]

        # Submit Feedback
        feedback_payload = {
            "csat_score": 5,
            "nps_score": 10,
            "feedback_comment": "Superb resolution speed and very comprehensive architecture guidance!"
        }
        fb_resp = self.sup_client.post(f"/support/tickets/{ticket_id}/feedback", json=feedback_payload, headers=self.headers)
        self.assertEqual(fb_resp.status_code, 200)
        fb_data = fb_resp.json()
        self.assertEqual(fb_data["csat_score"], 5)
        self.assertEqual(fb_data["nps_score"], 10)
        self.assertIn("Superb resolution", fb_data["feedback_comment"])

    def test_14_customer_360_context_timeline(self):
        # Lookup 360 context for customer
        email = "enterprise-client@acme.test"
        # Seed two tickets for this customer
        self.sup_client.post("/support/tickets", json={
            "customer_name": "Acme VIP",
            "customer_email": email,
            "subject": "Ticket A - SSO SAML Setup",
            "priority": "Medium"
        }, headers=self.headers)

        tkt2 = self.sup_client.post("/support/tickets", json={
            "customer_name": "Acme VIP",
            "customer_email": email,
            "subject": "Ticket B - Billing Cycle Alignment",
            "priority": "Low"
        }, headers=self.headers).json()

        # Submit 5-star rating on ticket 2
        self.sup_client.post(f"/support/tickets/{tkt2['id']}/feedback", json={"csat_score": 5}, headers=self.headers)

        # Get 360 Context
        ctx_resp = self.sup_client.get(f"/support/tickets/{tkt2['id']}/context", headers=self.headers)
        self.assertEqual(ctx_resp.status_code, 200)
        ctx = ctx_resp.json()
        self.assertEqual(ctx["customer_email"], email)
        self.assertGreaterEqual(ctx["total_tickets"], 2)
        self.assertEqual(ctx["average_csat"], 5.0)
        self.assertIn("associated_crm_context", ctx)
        self.assertEqual(ctx["associated_crm_context"]["customer_tier"], "Enterprise Tier 1")

    def test_15_knowledge_base_articles_and_voting(self):
        article_payload = {
            "title": "Migrating from Zoho CRM to STAT6 in Under 60 Minutes",
            "category": "Migration Guides",
            "content": "Follow this step-by-step tutorial to export Zoho CSV/API tokens and ingest into STAT6.",
            "is_published": True
        }
        create_resp = self.sup_client.post("/support/kb/articles", json=article_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        art = create_resp.json()
        art_id = art["id"]
        self.assertEqual(art["category"], "Migration Guides")
        self.assertEqual(art["helpful_votes"], 0)

        # Upvote article
        vote_resp = self.sup_client.post(f"/support/kb/articles/{art_id}/vote", headers=self.headers)
        self.assertEqual(vote_resp.status_code, 200)
        self.assertEqual(vote_resp.json()["helpful_votes"], 1)

if __name__ == "__main__":
    unittest.main()
