import os
import sys
import unittest
import httpx

GATEWAY_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:3000"

class TestAgenticFrameworkE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = httpx.Client(timeout=60.0)
        try:
            r = cls.client.get(f"{GATEWAY_URL}/health")
            cls.gateway_online = (r.status_code == 200)
        except Exception:
            cls.gateway_online = False

    @classmethod
    def tearDownClass(cls):
        cls.client.close()

    def test_01_gateway_health(self):
        self.assertTrue(self.gateway_online, "Gateway should be online at :8000")
        resp = self.client.get(f"{GATEWAY_URL}/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("gateway"), "HEALTHY")

    def test_02_ai_tools_catalog(self):
        resp = self.client.get(f"{GATEWAY_URL}/api/v1/ai/tools")
        self.assertEqual(resp.status_code, 200)
        tools = resp.json()
        self.assertGreaterEqual(len(tools), 10)
        tool_names = [t["name"] for t in tools]
        self.assertIn("get_financial_summary", tool_names)
        self.assertIn("get_employee_compensation", tool_names)
        self.assertIn("schedule_task", tool_names)

    def test_03_founder_compensation_data_stays_home(self):
        payload = {
            "message": "Give me the complete salary and compensation details of all employees",
            "page_context": {
                "module": "hr",
                "route": "/hr",
                "timezone": "UTC"
            }
        }
        resp = self.client.post(f"{GATEWAY_URL}/api/v1/ai/chat", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("intent"), "HR_COMPENSATION_FOUNDER")
        self.assertEqual(data.get("output_tier"), "TIER_3_RESTRICTED")
        
        table = data.get("data_table")
        self.assertIsNotNone(table, "Tier 3 salary data must return structured data_table")
        self.assertIn("Annual Salary", table.get("columns", []))
        self.assertGreaterEqual(len(table.get("rows", [])), 4)

    def test_04_temporal_scheduling_and_hitl_workflow(self):
        # 1. Schedule a task via natural language through AI Copilot
        payload = {
            "message": "Schedule Net30 overdue invoice reminder to Acme Corp tomorrow at 10 AM (Require Approval)",
            "page_context": {
                "module": "finance",
                "route": "/finance",
                "timezone": "UTC"
            }
        }
        resp = self.client.post(f"{GATEWAY_URL}/api/v1/ai/chat", json=payload)
        self.assertEqual(resp.status_code, 200)
        ai_data = resp.json()
        self.assertEqual(ai_data.get("intent"), "TEMPORAL_TASK_SCHEDULED")
        
        st = ai_data.get("scheduled_task")
        self.assertIsNotNone(st)
        task_id = st.get("task_id")
        hitl_id = st.get("hitl_approval_id")
        self.assertTrue(st.get("requires_hitl"))
        self.assertIsNotNone(hitl_id)

        # 2. Verify task exists in automation daemon queue
        t_resp = self.client.get(f"{GATEWAY_URL}/api/v1/automation/tasks/{task_id}")
        self.assertEqual(t_resp.status_code, 200)
        task_record = t_resp.json()
        self.assertEqual(task_record.get("id"), task_id)
        self.assertEqual(task_record.get("target_service"), "finance-service")

        # 3. Process human approval via HITL decision endpoint
        decision_payload = {
            "decision": "APPROVED",
            "decision_notes": "Authorized by Founder during E2E verification"
        }
        dec_resp = self.client.post(f"{GATEWAY_URL}/api/v1/automation/hitl/{hitl_id}/decision", json=decision_payload)
        self.assertEqual(dec_resp.status_code, 200)
        hitl_record = dec_resp.json()
        self.assertEqual(hitl_record.get("status"), "APPROVED")

        # 4. Verify task transitioned to EXECUTED
        t_after = self.client.get(f"{GATEWAY_URL}/api/v1/automation/tasks/{task_id}").json()
        self.assertEqual(t_after.get("status"), "EXECUTED")
        self.assertIsNotNone(t_after.get("executed_at"))

    def test_05_frontend_availability(self):
        resp = self.client.get(FRONTEND_URL)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<!doctype html>", resp.text.lower())


if __name__ == "__main__":
    unittest.main()
