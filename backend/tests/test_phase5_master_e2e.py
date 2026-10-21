import os
import sys
import unittest
import json
import uuid
from datetime import datetime
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.automation_service.main import app as automation_app
from services.crm_service.main import app as crm_app
from services.finance_service.main import app as finance_app
from services.inventory_service.main import app as inventory_app
from services.hr_service.main import app as hr_app

class TestPhase5MasterE2E(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.auto_client = TestClient(automation_app)
        cls.crm_client = TestClient(crm_app)
        cls.fin_client = TestClient(finance_app)
        cls.inv_client = TestClient(inventory_app)
        cls.hr_client = TestClient(hr_app)

        cls.headers = {
            "x-user-id": "usr-auto-chief-01",
            "x-org-id": "org-stat6-phase5-test",
            "x-user-role": "admin",
            "x-user-email": "automation-lead@stat6.enterprise"
        }

    # =========================================================================
    # 1. Visual Workflows (DAG Execution Engine) Tests
    # =========================================================================
    def test_01_workflow_definition_creation_and_listing(self):
        nodes = [
            {
                "id": "node-trig-1",
                "type": "TRIGGER",
                "title": "Deal Won Trigger",
                "config": {"event_name": "deal.won"},
                "next_node_ids": ["node-cond-2"]
            },
            {
                "id": "node-cond-2",
                "type": "CONDITION",
                "title": "High Value Check ($50k+)",
                "config": {"condition": "amount >= 50000"},
                "on_true": ["node-act-true-3"],
                "on_false": ["node-act-false-4"]
            },
            {
                "id": "node-act-true-3",
                "type": "ACTION",
                "title": "Dispatch CFO Review & Alert",
                "config": {"action_type": "NOTIFY_CFO"},
                "next_node_ids": []
            },
            {
                "id": "node-act-false-4",
                "type": "ACTION",
                "title": "Standard Provisioning",
                "config": {"action_type": "PROVISION_STANDARD"},
                "next_node_ids": []
            }
        ]

        resp = self.auto_client.post("/automation/workflows", json={
            "name": "Enterprise Deal Governance DAG",
            "description": "Evaluates won deals and conditionally routes high-value contracts",
            "trigger_event": "deal.won",
            "nodes": nodes,
            "is_active": True
        }, headers=self.headers)

        self.assertEqual(resp.status_code, 200)
        wf = resp.json()
        self.assertEqual(wf["name"], "Enterprise Deal Governance DAG")
        self.assertEqual(wf["trigger_event"], "deal.won")
        self.assertEqual(wf["execution_count"], 0)

        # List workflows
        list_resp = self.auto_client.get("/automation/workflows", headers=self.headers)
        self.assertEqual(list_resp.status_code, 200)
        all_wfs = list_resp.json()
        self.assertTrue(any(w["id"] == wf["id"] for w in all_wfs))

    def test_02_workflow_dag_execution_true_branch(self):
        nodes = [
            {
                "id": "start-1",
                "type": "TRIGGER",
                "title": "Inbound Invoice Trigger",
                "config": {"event_name": "invoice.submitted"},
                "next_node_ids": ["check-amount-2"]
            },
            {
                "id": "check-amount-2",
                "type": "CONDITION",
                "title": "Invoice Amount Threshold",
                "config": {"condition": "amount >= 10000"},
                "on_true": ["act-cfo-3"],
                "on_false": ["act-auto-approve-4"]
            },
            {
                "id": "act-cfo-3",
                "type": "ACTION",
                "title": "Route to CFO Escalation Queue",
                "config": {"action_type": "QUEUE_CFO_ESCALATION"},
                "next_node_ids": []
            },
            {
                "id": "act-auto-approve-4",
                "type": "ACTION",
                "title": "Auto-Approve Low Value Invoice",
                "config": {"action_type": "AUTO_APPROVE"},
                "next_node_ids": []
            }
        ]

        wf = self.auto_client.post("/automation/workflows", json={
            "name": "Invoice Compliance Routing",
            "trigger_event": "invoice.submitted",
            "nodes": nodes
        }, headers=self.headers).json()

        # Trigger with amount = 25000 (>= 10000 -> True branch)
        trig_resp = self.auto_client.post(f"/automation/workflows/{wf['id']}/trigger", json={
            "payload": {"amount": 25000, "vendor": "Snowflake Inc"}
        }, headers=self.headers)

        self.assertEqual(trig_resp.status_code, 200)
        execution = trig_resp.json()
        self.assertEqual(execution["status"], "COMPLETED")
        self.assertEqual(execution["workflow_id"], wf["id"])

        steps = json.loads(execution["step_history"])
        step_node_ids = [s["node_id"] for s in steps]
        self.assertIn("start-1", step_node_ids)
        self.assertIn("check-amount-2", step_node_ids)
        self.assertIn("act-cfo-3", step_node_ids)
        self.assertNotIn("act-auto-approve-4", step_node_ids)

    def test_03_workflow_dag_execution_false_branch(self):
        nodes = [
            {
                "id": "start-1",
                "type": "TRIGGER",
                "next_node_ids": ["cond-1"]
            },
            {
                "id": "cond-1",
                "type": "CONDITION",
                "config": {"condition": "amount >= 10000"},
                "on_true": ["act-cfo"],
                "on_false": ["act-auto-approve"]
            },
            {
                "id": "act-cfo",
                "type": "ACTION",
                "config": {"action_type": "QUEUE_CFO"},
                "next_node_ids": []
            },
            {
                "id": "act-auto-approve",
                "type": "ACTION",
                "config": {"action_type": "AUTO_APPROVE"},
                "next_node_ids": []
            }
        ]

        wf = self.auto_client.post("/automation/workflows", json={
            "name": "Invoice Routing Low Value Test",
            "trigger_event": "invoice.submitted",
            "nodes": nodes
        }, headers=self.headers).json()

        # Trigger with amount = 4500 (< 10000 -> False branch)
        trig_resp = self.auto_client.post(f"/automation/workflows/{wf['id']}/trigger", json={
            "payload": {"amount": 4500, "vendor": "Fastly CDN"}
        }, headers=self.headers)

        self.assertEqual(trig_resp.status_code, 200)
        execution = trig_resp.json()
        steps = json.loads(execution["step_history"])
        step_node_ids = [s["node_id"] for s in steps]
        self.assertIn("act-auto-approve", step_node_ids)
        self.assertNotIn("act-cfo", step_node_ids)

    # =========================================================================
    # 2. Unified Cross-Module Approvals Inbox Tests
    # =========================================================================
    def test_04_unified_approval_creation_pr(self):
        appr_resp = self.auto_client.post("/automation/approvals", json={
            "module": "PROCUREMENT",
            "record_type": "PURCHASE_REQUISITION",
            "record_id": f"PR-{uuid.uuid4().hex[:6].upper()}",
            "requester_name": "DevOps Lead",
            "approver_role": "FINANCE_DIRECTOR",
            "title": "Hardware Servers Purchase Approval",
            "description": "5x Dell PowerEdge R750 for on-prem banking sandbox",
            "amount": 48500.0
        }, headers=self.headers)

        self.assertEqual(appr_resp.status_code, 200)
        appr = appr_resp.json()
        self.assertEqual(appr["module"], "PROCUREMENT")
        self.assertEqual(appr["status"], "PENDING")
        self.assertEqual(appr["amount"], 48500.0)

    def test_05_unified_approval_decision_approve(self):
        appr = self.auto_client.post("/automation/approvals", json={
            "module": "CRM",
            "record_type": "QUOTE_DISCOUNT",
            "record_id": f"QTE-{uuid.uuid4().hex[:6].upper()}",
            "title": "Enterprise 22% Margin Floor Override",
            "amount": 120000.0,
            "approver_role": "VP_SALES"
        }, headers=self.headers).json()

        # Approve
        dec_resp = self.auto_client.post(f"/automation/approvals/{appr['id']}/action", json={
            "action": "APPROVE",
            "notes": "Approved discount based on 3-year upfront commitment"
        }, headers=self.headers)

        self.assertEqual(dec_resp.status_code, 200)
        dec = dec_resp.json()
        self.assertEqual(dec["status"], "APPROVED")
        self.assertEqual(dec["decision_by_id"], "usr-auto-chief-01")
        self.assertIsNotNone(dec["decided_at"])

    def test_06_unified_approval_decision_delegate(self):
        appr = self.auto_client.post("/automation/approvals", json={
            "module": "HR",
            "record_type": "LEAVE_REQUEST",
            "record_id": f"LV-{uuid.uuid4().hex[:6].upper()}",
            "title": "Executive Sabbatical Request",
            "approver_role": "MANAGER"
        }, headers=self.headers).json()

        # Delegate
        del_resp = self.auto_client.post(f"/automation/approvals/{appr['id']}/action", json={
            "action": "DELEGATE",
            "delegate_to_id": "usr-hr-director-009",
            "notes": "Delegated to HR Director while on travel"
        }, headers=self.headers)

        self.assertEqual(del_resp.status_code, 200)
        dec = del_resp.json()
        self.assertEqual(dec["status"], "DELEGATED")
        self.assertEqual(dec["delegated_to_id"], "usr-hr-director-009")

    def test_07_unified_approval_decision_reject(self):
        appr = self.auto_client.post("/automation/approvals", json={
            "module": "FINANCE",
            "record_type": "EXPENSE",
            "record_id": f"EXP-{uuid.uuid4().hex[:6].upper()}",
            "title": "Unapproved First Class Airfare",
            "amount": 7500.0,
            "approver_role": "FINANCE_MANAGER"
        }, headers=self.headers).json()

        # Reject
        rej_resp = self.auto_client.post(f"/automation/approvals/{appr['id']}/action", json={
            "action": "REJECT",
            "notes": "Violates corporate travel policy section 4.2"
        }, headers=self.headers)

        self.assertEqual(rej_resp.status_code, 200)
        dec = rej_resp.json()
        self.assertEqual(dec["status"], "REJECTED")

    # =========================================================================
    # 3. AI Natural Language Workflow Generator Tests
    # =========================================================================
    def test_08_ai_natural_language_workflow_generator(self):
        resp = self.auto_client.post("/automation/ai/generate-workflow", json={
            "prompt": "When a deal is won and amount > 50000, trigger CFO approval and alert the team on Slack"
        }, headers=self.headers)

        self.assertEqual(resp.status_code, 200)
        ai_wf = resp.json()
        self.assertEqual(ai_wf["trigger_event"], "deal.won")
        self.assertGreater(len(ai_wf["nodes"]), 2)
        
        # Verify synthesized nodes have trigger, condition, and actions
        node_types = [n["type"] for n in ai_wf["nodes"]]
        self.assertIn("TRIGGER", node_types)
        self.assertIn("CONDITION", node_types)
        self.assertIn("ACTION", node_types)

    # =========================================================================
    # 4. Zoho One 1-Click Migration Engine Tests
    # =========================================================================
    def test_09_zoho_one_migration_engine_crm(self):
        zoho_crm_payload = {
            "accounts": [
                {
                    "id": "zoho_acc_101",
                    "Account_Name": "Zoho Enterprise Customer LLC",
                    "Industry": "FinTech",
                    "Annual_Revenue": 5000000.0,
                    "Website": "https://zoho-customer.com"
                }
            ],
            "contacts": [
                {
                    "id": "zoho_cnt_201",
                    "First_Name": "Robert",
                    "Last_Name": "Patterson",
                    "Email": f"robert-{uuid.uuid4().hex[:4]}@zoho-customer.com",
                    "Account_ID": "zoho_acc_101",
                    "Title": "Chief Technology Officer"
                }
            ],
            "deals": [
                {
                    "id": "zoho_dl_301",
                    "Deal_Name": "Core Banking Modernization Contract",
                    "Amount": 250000.0,
                    "Stage": "Negotiation",
                    "Account_ID": "zoho_acc_101",
                    "Contact_ID": "zoho_cnt_201"
                }
            ],
            "leads": [
                {
                    "id": "zoho_ld_401",
                    "First_Name": "Jennifer",
                    "Last_Name": "Walsh",
                    "Email": f"jennifer-{uuid.uuid4().hex[:4]}@prospect.org",
                    "Company": "Prospect Global Corp"
                }
            ]
        }

        resp = self.auto_client.post("/automation/import/zoho-one", json={
            "zoho_crm": zoho_crm_payload
        }, headers=self.headers)

        self.assertEqual(resp.status_code, 200)
        mig = resp.json()
        self.assertEqual(mig["status"], "SUCCESS")
        self.assertEqual(mig["records_migrated"]["crm_companies"], 1)
        self.assertEqual(mig["records_migrated"]["crm_contacts"], 1)
        self.assertEqual(mig["records_migrated"]["crm_deals"], 1)
        self.assertEqual(mig["records_migrated"]["crm_leads"], 1)

        # Verify canonical UUID mapping preserves relationships
        mappings = {m["legacy_id"]: m["canonical_id"] for m in mig["canonical_mappings"]}
        self.assertIn("zoho_acc_101", mappings)
        self.assertIn("zoho_cnt_201", mappings)
        self.assertIn("zoho_dl_301", mappings)

    def test_10_zoho_one_migration_engine_hr_and_inv(self):
        zoho_people_payload = {
            "departments": [
                {"id": "zoho_dept_01", "Department_Name": "Engineering Architecture"}
            ],
            "employees": [
                {
                    "id": "zoho_emp_01",
                    "First_Name": "Alex",
                    "Last_Name": "Rivera",
                    "Email": f"alex-{uuid.uuid4().hex[:4]}@stat6.corp",
                    "Department_ID": "zoho_dept_01",
                    "Designation": "Principal Cloud Architect"
                }
            ]
        }

        zoho_inv_payload = {
            "items": [
                {
                    "id": "zoho_item_01",
                    "Item_Name": "Enterprise Edge Security Appliance",
                    "SKU": f"SKU-EDG-{uuid.uuid4().hex[:4].upper()}",
                    "Category": "Hardware",
                    "Purchase_Rate": 1200.0,
                    "Rate": 2500.0,
                    "Stock_On_Hand": 45
                }
            ]
        }

        resp = self.auto_client.post("/automation/import/zoho-one", json={
            "zoho_people": zoho_people_payload,
            "zoho_inventory": zoho_inv_payload
        }, headers=self.headers)

        self.assertEqual(resp.status_code, 200)
        mig = resp.json()
        self.assertEqual(mig["status"], "SUCCESS")
        self.assertEqual(mig["records_migrated"]["hr_departments"], 1)
        self.assertEqual(mig["records_migrated"]["hr_employees"], 1)
        self.assertEqual(mig["records_migrated"]["inv_products"], 1)

    def test_11_zoho_one_migration_engine_books_invoices(self):
        zoho_books_payload = {
            "invoices": [
                {
                    "id": "zoho_inv_01",
                    "Invoice_Number": f"INV-ZH-{uuid.uuid4().hex[:6].upper()}",
                    "Customer_Name": "Acme Industrial Corp",
                    "Total": 35000.0,
                    "Status": "Sent"
                }
            ]
        }

        resp = self.auto_client.post("/automation/import/zoho-one", json={
            "zoho_books": zoho_books_payload
        }, headers=self.headers)

        self.assertEqual(resp.status_code, 200)
        mig = resp.json()
        self.assertEqual(mig["status"], "SUCCESS")
        self.assertEqual(mig["records_migrated"]["fin_invoices"], 1)

    def test_12_full_zoho_one_master_migration_and_audit(self):
        full_dump = {
            "zoho_crm": {
                "accounts": [{"id": "z_a1", "Account_Name": "Apex Group"}],
                "contacts": [{"id": "z_c1", "First_Name": "Elena", "Last_Name": "Rostova", "Account_ID": "z_a1"}],
                "deals": [{"id": "z_d1", "Deal_Name": "Apex Multi-Cloud Retainer", "Amount": 180000.0, "Account_ID": "z_a1", "Contact_ID": "z_c1"}]
            },
            "zoho_people": {
                "departments": [{"id": "z_dp1", "Department_Name": "Financial Operations"}],
                "employees": [{"id": "z_e1", "First_Name": "Vikram", "Last_Name": "Sharma", "Department_ID": "z_dp1"}]
            },
            "zoho_inventory": {
                "items": [{"id": "z_i1", "Item_Name": "High Bandwidth Switch", "SKU": f"SW-{uuid.uuid4().hex[:4].upper()}", "Rate": 4500.0, "Stock_On_Hand": 12}]
            },
            "zoho_books": {
                "invoices": [{"id": "z_inv1", "Customer_Name": "Apex Group", "Total": 60000.0}]
            }
        }

        resp = self.auto_client.post("/automation/import/zoho-one", json=full_dump, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        mig = resp.json()
        self.assertEqual(mig["status"], "SUCCESS")
        self.assertEqual(mig["total_records"], 7)
        self.assertGreater(mig["elapsed_ms"], 0)
        self.assertEqual(len(mig["validation_errors"]), 0)


if __name__ == "__main__":
    unittest.main()
