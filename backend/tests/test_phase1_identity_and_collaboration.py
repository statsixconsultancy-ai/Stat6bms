import os
import sys
import unittest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.auth_service.main import app as auth_app
from services.compliance_service.main import app as compliance_app
from services.collaboration_service.main import app as collab_app

class TestPhase1IdentityAndCollaboration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.auth_client = TestClient(auth_app)
        cls.comp_client = TestClient(compliance_app)
        cls.collab_client = TestClient(collab_app)
        cls.headers = {
            "x-user-id": "usr-admin-001",
            "x-org-id": "org-stat6-test",
            "x-user-role": "superadmin",
            "x-user-email": "admin@stat6.enterprise"
        }

    # =========================================================================
    # 1. Multi-Persona Identity & User Provisioning Tests
    # =========================================================================
    def test_01_personas_catalog(self):
        resp = self.auth_client.get("/auth/personas")
        self.assertEqual(resp.status_code, 200)
        personas = resp.json()
        self.assertEqual(len(personas), 7)
        keys = [p["persona"] for p in personas]
        for expected in ["ADMIN", "EMPLOYEE", "MANAGER", "CUSTOMER", "VENDOR", "PARTNER", "EXTERNAL_USER"]:
            self.assertIn(expected, keys)

    def test_02_register_and_login_with_persona(self):
        slug = f"acme-corp-{int(datetime.utcnow().timestamp())}"
        reg_payload = {
            "org_name": "Acme Global Dynamics",
            "org_slug": slug,
            "admin_name": "Sarah Connor",
            "admin_email": f"sarah@{slug}.com",
            "password": "SecurePassword123!",
            "persona": "ADMIN",
            "currency": "INR",
            "timezone": "Asia/Kolkata"
        }
        reg_resp = self.auth_client.post("/auth/register", json=reg_payload)
        self.assertEqual(reg_resp.status_code, 200)
        data = reg_resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["user"]["persona"], "ADMIN")
        self.assertEqual(data["organization"]["currency"], "INR")

        # Login verification
        login_resp = self.auth_client.post("/auth/login", json={
            "email": f"sarah@{slug}.com",
            "password": "SecurePassword123!"
        })
        self.assertEqual(login_resp.status_code, 200)
        self.assertIn("access_token", login_resp.json())

    def test_03_provision_customer_portal_persona(self):
        payload = {
            "email": f"client-{int(datetime.utcnow().timestamp())}@external.com",
            "full_name": "David Wallace",
            "password": "ClientPassword123!",
            "role": "client",
            "persona": "CUSTOMER",
            "portal_profile": {
                "company_id": "comp-dunder-mifflin",
                "can_view_invoices": True,
                "can_sign_quotes": True
            }
        }
        resp = self.auth_client.post("/auth/users", json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        user = resp.json()
        self.assertEqual(user["persona"], "CUSTOMER")
        self.assertEqual(user["portal_profile"]["company_id"], "comp-dunder-mifflin")

    # =========================================================================
    # 2. Organization Multi-Branch, Tax & Module Toggles Tests
    # =========================================================================
    def test_04_organization_multi_branch_and_module_toggles(self):
        update_payload = {
            "name": "STAT6 Enterprise HQ",
            "branches": [
                {"code": "BLR-01", "name": "Bengaluru Tech Park", "gstin": "29AAAAA0000A1Z5", "city": "Bengaluru"},
                {"code": "MUM-01", "name": "Mumbai Financial Hub", "gstin": "27AAAAA0000A1Z6", "city": "Mumbai"}
            ],
            "tax_identifiers": {"pan": "AAACS1234F", "cin": "U72200KA2026PTC000000"},
            "fiscal_year_start": 4, # April
            "enabled_modules": ["crm", "finance", "projects", "hr", "inventory", "collaboration", "compliance", "ai"]
        }
        resp = self.auth_client.put("/auth/organization/settings", json=update_payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["branches"]), 2)
        self.assertEqual(data["branches"][0]["code"], "BLR-01")
        self.assertEqual(data["fiscal_year_start"], 4)
        self.assertIn("crm", data["enabled_modules"])
        self.assertNotIn("marketing", data["enabled_modules"]) # Toggled off

    # =========================================================================
    # 3. Dynamic Custom Fields & Custom Objects (Zoho Creator Alt) Tests
    # =========================================================================
    def test_05_custom_fields_engine(self):
        cf_payload = {
            "module_name": "crm",
            "entity_type": "Deal",
            "field_name": "lead_source_detail",
            "field_label": "Lead Source Sub-Category",
            "field_type": "select",
            "options": ["Google Search", "LinkedIn Outreach", "Y-Combinator Demo", "Webinar"],
            "is_required": True,
            "default_value": "Google Search"
        }
        create_resp = self.auth_client.post("/auth/custom-fields", json=cf_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        field_id = create_resp.json()["id"]

        # List fields by entity
        list_resp = self.auth_client.get("/auth/custom-fields?entity_type=Deal", headers=self.headers)
        self.assertEqual(list_resp.status_code, 200)
        fields = list_resp.json()
        self.assertTrue(any(f["field_name"] == "lead_source_detail" for f in fields))

        # Delete field
        del_resp = self.auth_client.delete(f"/auth/custom-fields/{field_id}", headers=self.headers)
        self.assertEqual(del_resp.status_code, 200)

    def test_06_custom_objects_builder(self):
        obj_payload = {
            "object_name": "flight_charters",
            "display_name": "Private Aviation Charters",
            "description": "Custom aircraft manifest and charter scheduling tracker",
            "schema_definition": {
                "tail_number": {"type": "string", "required": True},
                "departure_icao": {"type": "string", "required": True},
                "arrival_icao": {"type": "string", "required": True},
                "passenger_count": {"type": "integer", "required": True}
            }
        }
        resp = self.auth_client.post("/auth/custom-objects", json=obj_payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["object_name"], "flight_charters")
        self.assertIn("tail_number", data["schema_definition"])

    # =========================================================================
    # 4. 4-Dimensional RBAC & Field-Level Security (Compliance) Tests
    # =========================================================================
    def test_07_four_dimensional_rbac_evaluation(self):
        # Case A: Admin has full access, zero masked fields
        req_admin = {
            "user_id": "usr-admin-1",
            "user_role": "admin",
            "persona": "ADMIN",
            "module": "finance",
            "action": "EXPORT"
        }
        res_admin = self.comp_client.post("/compliance/evaluate-rbac", json=req_admin, headers=self.headers)
        self.assertEqual(res_admin.status_code, 200)
        self.assertTrue(res_admin.json()["allowed"])
        self.assertEqual(res_admin.json()["masked_fields"], [])

        # Case B: Customer attempting to access HR module is rejected
        req_cust = {
            "user_id": "usr-cust-1",
            "user_role": "client",
            "persona": "CUSTOMER",
            "module": "hr",
            "action": "READ"
        }
        res_cust = self.comp_client.post("/compliance/evaluate-rbac", json=req_cust, headers=self.headers)
        self.assertEqual(res_cust.status_code, 200)
        self.assertFalse(res_cust.json()["allowed"])

        # Case C: Employee accessing HR has Field-Level Security masking (salary masked)
        req_emp = {
            "user_id": "usr-emp-1",
            "user_role": "member",
            "persona": "EMPLOYEE",
            "module": "hr",
            "action": "READ"
        }
        res_emp = self.comp_client.post("/compliance/evaluate-rbac", json=req_emp, headers=self.headers)
        self.assertEqual(res_emp.status_code, 200)
        self.assertTrue(res_emp.json()["allowed"])
        self.assertIn("salary", res_emp.json()["masked_fields"])

    def test_08_gdpr_export_and_right_to_be_forgotten(self):
        target = "jane.doe@acme.com"
        # Export DSR
        exp_resp = self.comp_client.post("/compliance/gdpr/export", json={"subject_email": target}, headers=self.headers)
        self.assertEqual(exp_resp.status_code, 200)
        self.assertEqual(exp_resp.json()["status"], "Completed")

        # Anonymize (Right-to-be-Forgotten)
        anon_resp = self.comp_client.post("/compliance/gdpr/anonymize", json={"subject_email": target, "confirmation": True}, headers=self.headers)
        self.assertEqual(anon_resp.status_code, 200)
        self.assertEqual(anon_resp.json()["status"], "Anonymized")

    # =========================================================================
    # 5. Collaboration: Record Cards, Announcements, Calendar & Notes Tests
    # =========================================================================
    def test_09_chat_contextual_record_cards(self):
        # Create channel
        ch_resp = self.collab_client.post("/chat/channels", json={"name": f"deals-q4-{int(datetime.utcnow().timestamp())}", "description": "Q4 Deals Swarming"}, headers=self.headers)
        self.assertEqual(ch_resp.status_code, 200)
        ch_id = ch_resp.json()["id"]

        # Post message with Contextual Record Card
        card_payload = {
            "message": "Check out this major renewal contract!",
            "message_type": "text",
            "card_type": "deal",
            "card_data": {
                "id": "DEAL-2026-X",
                "title": "Quantum Robotics Cloud Infrastructure",
                "amount": 450000.0,
                "stage": "Proposal/Price Quote"
            }
        }
        msg_resp = self.collab_client.post(f"/chat/channels/{ch_id}/messages", json=card_payload, headers=self.headers)
        self.assertEqual(msg_resp.status_code, 200)
        msg = msg_resp.json()
        self.assertEqual(msg["card_type"], "deal")
        self.assertEqual(msg["card_data"]["amount"], 450000.0)

    def test_10_announcements_and_acknowledgments(self):
        ann_payload = {
            "title": "STAT6 Q4 Enterprise Townhall & Product Launch",
            "body": "All hands meeting this Friday at 3:00 PM IST regarding Zoho One migration campaigns.",
            "priority": "urgent"
        }
        ann_resp = self.collab_client.post("/chat/announcements", json=ann_payload, headers=self.headers)
        self.assertEqual(ann_resp.status_code, 200)
        ann_id = ann_resp.json()["id"]

        # Acknowledge
        ack_resp = self.collab_client.post(f"/chat/announcements/{ann_id}/acknowledge", headers=self.headers)
        self.assertEqual(ack_resp.status_code, 200)
        self.assertEqual(ack_resp.json()["status"], "acknowledged")
        self.assertEqual(ack_resp.json()["total_acks"], 1)

    def test_11_shared_calendar_events(self):
        now = datetime.utcnow()
        evt_payload = {
            "title": "Executive Client Sync: Nexus Robotics",
            "description": "Review quarterly SLA compliance and expansion proposal",
            "start_time": (now + timedelta(days=1)).isoformat(),
            "end_time": (now + timedelta(days=1, hours=1)).isoformat(),
            "event_type": "meeting",
            "attendees": ["marcus@nexus.com", "elena@stat6.com"],
            "location_or_link": "https://meet.google.com/abc-defg-hij"
        }
        evt_resp = self.collab_client.post("/chat/calendar/events", json=evt_payload, headers=self.headers)
        self.assertEqual(evt_resp.status_code, 200)
        evt_id = evt_resp.json()["id"]

        # List events
        list_resp = self.collab_client.get("/chat/calendar/events", headers=self.headers)
        self.assertEqual(list_resp.status_code, 200)
        self.assertTrue(any(e["id"] == evt_id for e in list_resp.json()))

        # Cleanup
        del_resp = self.collab_client.delete(f"/chat/calendar/events/{evt_id}", headers=self.headers)
        self.assertEqual(del_resp.status_code, 200)

    def test_12_polymorphic_record_notes_and_activity_stream(self):
        note_payload = {
            "entity_type": "Deal",
            "entity_id": "DEAL-APEX-99",
            "content": "Prospect requested net-45 payment terms instead of standard net-30.",
            "mentions": ["@finance_lead", "@marcus_chen"],
            "attachments": ["https://s3.stat6.cloud/quotes/Q-99.pdf"]
        }
        note_resp = self.collab_client.post("/chat/notes", json=note_payload, headers=self.headers)
        self.assertEqual(note_resp.status_code, 200)
        note = note_resp.json()
        self.assertEqual(note["entity_type"], "Deal")
        self.assertIn("@finance_lead", note["mentions"])

        # Fetch notes for this entity
        get_resp = self.collab_client.get("/chat/notes?entity_type=Deal&entity_id=DEAL-APEX-99", headers=self.headers)
        self.assertEqual(get_resp.status_code, 200)
        self.assertTrue(len(get_resp.json()) >= 1)

        # Activity stream check
        act_resp = self.collab_client.get("/chat/activity-stream", headers=self.headers)
        self.assertEqual(act_resp.status_code, 200)
        self.assertIsInstance(act_resp.json(), list)

if __name__ == "__main__":
    unittest.main()
