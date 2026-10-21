import os
import sys
import unittest

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.security import UserContext
from services.ai_copilot_service.tools.base import DataTier, SideEffect
from services.ai_copilot_service.tools.registry import default_registry
from services.ai_copilot_service.privacy import PrivacyGateway
from services.ai_copilot_service.engine import default_engine


class TestAgenticFrameworkCore(unittest.TestCase):
    def setUp(self):
        self.admin_ctx = UserContext(
            user_id="usr-dev-001",
            org_id="org-acroflow-main",
            role="admin",
            email="admin@acroflow.enterprise"
        )
        self.sales_ctx = UserContext(
            user_id="usr-sales-002",
            org_id="org-acroflow-main",
            role="sales",
            email="sales@acroflow.enterprise"
        )

    def test_tool_registry_registration(self):
        tools = default_registry.list_tools("admin")
        self.assertGreaterEqual(len(tools), 10, "Registry should have at least 10 domain tools")
        tool_names = [t.name for t in tools]
        self.assertIn("get_financial_summary", tool_names)
        self.assertIn("get_employee_compensation", tool_names)
        self.assertIn("create_lead", tool_names)
        self.assertIn("schedule_task", tool_names)
        self.assertIn("list_issues", tool_names)

    def test_rbac_filtering_on_tools(self):
        admin_tools = [t.name for t in default_registry.list_tools("admin")]
        sales_tools = [t.name for t in default_registry.list_tools("sales")]
        # Executive compensation is strictly excluded for sales reps
        self.assertIn("get_employee_compensation", admin_tools)
        self.assertNotIn("get_employee_compensation", sales_tools)

    def test_schema_validation_rejection(self):
        # Passing invalid arguments should fail schema validation cleanly
        res = default_registry.execute_tool("create_invoice", {"client_name": "Acme", "amount": -500.0, "due_date": "2026-11-01"}, self.admin_ctx)
        self.assertFalse(res["success"])
        self.assertEqual(res["error"], "SCHEMA_VALIDATION_ERROR")

    def test_privacy_gateway_classification(self):
        tier_public = PrivacyGateway.classify_data_tier({"title": "Documentation Guide"})
        self.assertEqual(tier_public, DataTier.TIER_1_INTERNAL)

        tier_confidential = PrivacyGateway.classify_data_tier({"client_name": "Acme Corp", "amount": 25000})
        self.assertEqual(tier_confidential, DataTier.TIER_2_CONFIDENTIAL)

        tier_restricted = PrivacyGateway.classify_data_tier({"employee": "John Doe", "salary_annual": 145000})
        self.assertEqual(tier_restricted, DataTier.TIER_3_RESTRICTED)
        self.assertFalse(PrivacyGateway.is_export_permitted(tier_restricted, "hosted_llm"))

    def test_pseudonymization_and_restore(self):
        raw = "Contact Marcus at marcus.chen@enterprise.com or call 555-019-2834 regarding PO-102."
        masked, rev_map = PrivacyGateway.pseudonymize_text(raw)
        self.assertNotIn("marcus.chen@enterprise.com", masked)
        restored = PrivacyGateway.restore_pseudonyms(masked, rev_map)
        self.assertEqual(raw, restored)

    def test_engine_financial_summary(self):
        res = default_engine.process_request("What is our current financial position and paid revenue?", {}, self.admin_ctx)
        self.assertEqual(res["intent"], "FINANCIAL_SYNTHESIS")
        self.assertIn("Corporate Financial", res["reply"])
        self.assertIn("total_paid_revenue", res.get("immediate_data", {}))

    def test_engine_founder_compensation_data_stays_home(self):
        res = default_engine.process_request("Give me the complete salary and compensation details of all employees", {}, self.admin_ctx)
        self.assertEqual(res["intent"], "HR_COMPENSATION_FOUNDER")
        self.assertIsNotNone(res.get("data_table"), "Should return data_table for direct client rendering")
        self.assertEqual(res["output_tier"], DataTier.TIER_3_RESTRICTED.value)

    def test_engine_sales_compensation_rejected(self):
        res = default_engine.process_request("Give me the salary of all employees", {}, self.sales_ctx)
        self.assertIn("Access Denied", res["reply"])
        self.assertEqual(res.get("error"), "FORBIDDEN")

    def test_engine_temporal_task_scheduling(self):
        res = default_engine.process_request("Schedule an invoice reminder for Acme Corp tomorrow at 10 AM", {}, self.admin_ctx)
        self.assertEqual(res["intent"], "TEMPORAL_TASK_SCHEDULED")
        self.assertIsNotNone(res.get("scheduled_task"))
        self.assertTrue(res["scheduled_task"]["requires_hitl"])
        self.assertEqual(res["scheduled_task"]["target_service"], "finance-service")


if __name__ == "__main__":
    unittest.main()
