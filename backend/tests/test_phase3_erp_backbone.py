import os
import sys
import unittest
import json
from datetime import datetime
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.finance_service.main import app as finance_app
from services.inventory_service.main import app as inventory_app
from services.procurement_service.main import app as procurement_app

class TestPhase3ERPBackbone(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fin_client = TestClient(finance_app)
        cls.inv_client = TestClient(inventory_app)
        cls.proc_client = TestClient(procurement_app)
        cls.headers = {
            "x-user-id": "usr-finance-001",
            "x-org-id": "org-stat6-erp-test",
            "x-user-role": "cfo",
            "x-user-email": "cfo@stat6.enterprise"
        }

    # =========================================================================
    # 1. Finance & Double-Entry Accounting Tests
    # =========================================================================
    def test_01_invoice_creation_and_payment_reconciliation(self):
        inv_payload = {
            "client_name": "Titanium Global Systems",
            "issue_date": "2026-10-01",
            "due_date": "2026-10-31",
            "items": [
                {"description": "STAT6 Enterprise Core Subscription", "quantity": 1, "unit_price": 50000.0},
                {"description": "Cloud Dedicated Tenant Hosting", "quantity": 1, "unit_price": 10000.0}
            ]
        }
        create_resp = self.fin_client.post("/finance/invoices", json=inv_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        inv = create_resp.json()
        inv_id = inv["id"]
        self.assertEqual(inv["subtotal"], 60000.0)
        self.assertAlmostEqual(inv["total_amount"], 64800.0, places=1) # 8% default tax

        # Record payment in full
        pay_payload = {
            "amount": inv["total_amount"],
            "payment_date": "2026-10-05",
            "payment_method": "Wire Transfer",
            "reference_number": "WIRE-CHASE-9901"
        }
        pay_resp = self.fin_client.post(f"/finance/invoices/{inv_id}/payment", json=pay_payload, headers=self.headers)
        self.assertEqual(pay_resp.status_code, 200)

        # Check invoice status and balance due
        detail_resp = self.fin_client.get(f"/finance/invoices/{inv_id}", headers=self.headers)
        self.assertEqual(detail_resp.status_code, 200)
        d_data = detail_resp.json()
        self.assertEqual(d_data["status"], "Paid")
        self.assertAlmostEqual(d_data["balance_due"], 0.0, places=2)

    def test_02_double_entry_general_ledger_balanced(self):
        resp = self.fin_client.get("/finance/ledger", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        entries = resp.json()
        self.assertGreater(len(entries), 0)
        for entry in entries:
            self.assertTrue(entry["is_balanced"], f"Ledger entry {entry['entry_number']} is not balanced")
            self.assertAlmostEqual(entry["total_debit"], entry["total_credit"], places=2)

    def test_03_subscription_recurring_billing_and_renewal(self):
        sub_payload = {
            "customer_name": "Apex Cloud Partners",
            "customer_email": "billing@apexcloud.test",
            "plan_name": "STAT6 Enterprise Suite - 500 Seats",
            "billing_interval": "monthly",
            "unit_price": 15000.0,
            "quantity": 1,
            "payment_method": "Credit Card"
        }
        create_resp = self.fin_client.post("/finance/subscriptions", json=sub_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        sub = create_resp.json()
        sub_id = sub["id"]
        self.assertEqual(sub["status"], "Active")
        self.assertEqual(sub["total_recurring_amount"], 15000.0)

        # Renew Subscription
        renew_resp = self.fin_client.post(f"/finance/subscriptions/{sub_id}/renew", headers=self.headers)
        self.assertEqual(renew_resp.status_code, 200)
        self.assertEqual(renew_resp.json()["status"], "Active")
        self.assertEqual(renew_resp.json()["next_billing_date"], "2026-12-24")

        # Cancel Subscription
        cancel_resp = self.fin_client.post(f"/finance/subscriptions/{sub_id}/cancel", headers=self.headers)
        self.assertEqual(cancel_resp.status_code, 200)
        self.assertEqual(cancel_resp.json()["status"], "Cancelled")

    def test_04_statutory_gst_vat_calculation_engine(self):
        # 1. Intra-State -> 50% CGST + 50% SGST
        intra_req = {
            "subtotal": 100000.0,
            "place_of_supply": "Intra-State Domestic",
            "tax_rate": 0.18
        }
        intra_resp = self.fin_client.post("/finance/tax/calculate", json=intra_req)
        self.assertEqual(intra_resp.status_code, 200)
        intra_data = intra_resp.json()
        self.assertEqual(intra_data["cgst_amount"], 9000.0)
        self.assertEqual(intra_data["sgst_amount"], 9000.0)
        self.assertEqual(intra_data["igst_amount"], 0.0)
        self.assertEqual(intra_data["total_tax"], 18000.0)
        self.assertEqual(intra_data["gross_amount"], 118000.0)

        # 2. Inter-State -> 100% IGST
        inter_req = {
            "subtotal": 100000.0,
            "place_of_supply": "Inter-State Cross-Border",
            "tax_rate": 0.18
        }
        inter_resp = self.fin_client.post("/finance/tax/calculate", json=inter_req)
        self.assertEqual(inter_resp.status_code, 200)
        inter_data = inter_resp.json()
        self.assertEqual(inter_data["cgst_amount"], 0.0)
        self.assertEqual(inter_data["sgst_amount"], 0.0)
        self.assertEqual(inter_data["igst_amount"], 18000.0)

    def test_05_expense_ocr_receipt_scanner(self):
        scan_req = {
            "receipt_text": "Amazon Web Services Cloud Infrastructure monthly invoice #AWS-99021"
        }
        ocr_resp = self.fin_client.post("/finance/expenses/ocr-scan", json=scan_req)
        self.assertEqual(ocr_resp.status_code, 200)
        ocr_data = ocr_resp.json()
        self.assertEqual(ocr_data["vendor"], "Amazon Web Services Inc")
        self.assertEqual(ocr_data["category"], "Cloud Hosting")
        self.assertEqual(ocr_data["amount"], 1420.50)
        self.assertGreater(ocr_data["confidence_score"], 0.9)

    def test_06_profit_and_loss_and_cash_flow_reports(self):
        pnl_resp = self.fin_client.get("/finance/reports/p-and-l", headers=self.headers)
        self.assertEqual(pnl_resp.status_code, 200)
        pnl = pnl_resp.json()
        self.assertIn("operating_revenue", pnl)
        self.assertIn("ebitda", pnl)

        cf_resp = self.fin_client.get("/finance/reports/cash-flow", headers=self.headers)
        self.assertEqual(cf_resp.status_code, 200)
        cf = cf_resp.json()
        self.assertIn("cash_at_start", cf)
        self.assertIn("cash_at_close", cf)

    # =========================================================================
    # 2. Inventory & Physical Asset Management Tests
    # =========================================================================
    def test_07_warehouse_creation_and_stock_transfer(self):
        # Create 2 Warehouses
        wh1_code = f"WH-CENTRAL-{int(datetime.utcnow().timestamp()) % 10000}"
        wh2_code = f"WH-COASTAL-{int(datetime.utcnow().timestamp()) % 10000}"

        self.inv_client.post("/inventory/warehouses", json={
            "code": wh1_code,
            "name": "Central Distribution Hub",
            "location": "Dallas, TX",
            "capacity": 20000
        }, headers=self.headers)

        self.inv_client.post("/inventory/warehouses", json={
            "code": wh2_code,
            "name": "Coastal Fulfillment Center",
            "location": "Oakland, CA",
            "capacity": 15000
        }, headers=self.headers)

        # Create Product
        sku = f"SRV-EDGE-{int(datetime.utcnow().timestamp()) % 10000}"
        prod_resp = self.inv_client.post("/inventory/products", json={
            "sku": sku,
            "name": "Edge Telemetry Gateway 4U",
            "unit_cost": 1200.0,
            "unit_price": 2400.0,
            "stock_quantity": 100,
            "reorder_level": 20
        }, headers=self.headers)
        self.assertEqual(prod_resp.status_code, 200)

        # Transfer 30 units from WH1 to WH2
        trf_payload = {
            "product_sku": sku,
            "from_warehouse_code": wh1_code,
            "to_warehouse_code": wh2_code,
            "quantity": 30,
            "notes": "Inter-warehouse stock rebalancing for regional launch"
        }
        trf_resp = self.inv_client.post("/inventory/warehouses/transfer", json=trf_payload, headers=self.headers)
        self.assertEqual(trf_resp.status_code, 200)
        trf_data = trf_resp.json()
        self.assertEqual(trf_data["quantity_transferred"], 30)
        self.assertEqual(trf_data["status"], "COMPLETED")

    def test_08_serial_and_batch_quarantine_tracking(self):
        batch_num = f"LOT-2026-{int(datetime.utcnow().timestamp()) % 10000}"
        batch_payload = {
            "product_sku": "SKU-SRV-900",  # Seeded or created product
            "batch_number": batch_num,
            "mfg_date": "2026-09-01",
            "expiry_date": "2029-09-01",
            "quantity": 50,
            "barcode_data": f"BAR-{batch_num}"
        }
        # Create product if not exists
        self.inv_client.post("/inventory/products", json={
            "sku": "SKU-SRV-900",
            "name": "Titanium Storage Array",
            "unit_cost": 3000.0,
            "unit_price": 6000.0,
            "stock_quantity": 50
        }, headers=self.headers)

        create_resp = self.inv_client.post("/inventory/batches", json=batch_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        b_data = create_resp.json()
        b_id = b_data["id"]
        self.assertEqual(b_data["status"], "Released")

        # Quarantine lot
        quar_resp = self.inv_client.post(f"/inventory/batches/{b_id}/quarantine", headers=self.headers)
        self.assertEqual(quar_resp.status_code, 200)
        self.assertEqual(quar_resp.json()["status"], "Quarantined")

    def test_09_fifo_and_weighted_average_valuation(self):
        resp = self.inv_client.get("/inventory/valuation/fifo-weighted", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        val = resp.json()
        self.assertGreaterEqual(val["total_skus"], 1)
        self.assertGreater(val["weighted_average_valuation"], 0.0)
        self.assertGreater(val["fifo_total_valuation"], 0.0)
        self.assertEqual(val["valuation_method_applied"], "HYBRID_FIFO_WEIGHTED")

    def test_10_fixed_asset_depreciation_schedule(self):
        asset_tag = f"AST-TEST-{int(datetime.utcnow().timestamp()) % 10000}"
        create_resp = self.inv_client.post("/inventory/assets", json={
            "asset_tag": asset_tag,
            "name": "Rack Mount AI Server Cluster",
            "purchase_date": "2026-01-15",
            "purchase_price": 50000.0,
            "salvage_value": 5000.0,
            "useful_life_years": 5
        }, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        asset_data = create_resp.json()
        self.assertEqual(len(asset_data["schedules"]), 5)
        # Annual depreciation: (50000 - 5000) / 5 = 9000
        self.assertAlmostEqual(asset_data["schedules"][0]["depreciation_expense"], 9000.0, places=1)
        self.assertAlmostEqual(asset_data["schedules"][-1]["ending_book_value"], 5000.0, places=1)

        resp = self.inv_client.get("/inventory/assets", headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        assets = resp.json()
        self.assertGreater(len(assets), 0)

    # =========================================================================
    # 3. Procurement & Vendor Operations Tests
    # =========================================================================
    def test_11_vendor_profile_and_scorecard(self):
        # Create Vendor
        v_name = f"Quantum Sourcing Corp {int(datetime.utcnow().timestamp()) % 10000}"
        v_resp = self.proc_client.post("/procurement/vendors", json={
            "name": v_name,
            "contact_email": "orders@quantumsourcing.test",
            "rating": 4.8,
            "payment_terms": "Net30"
        }, headers=self.headers)
        self.assertEqual(v_resp.status_code, 200)
        vendor_id = v_resp.json()["id"]

        # Check scorecard
        sc_resp = self.proc_client.get(f"/procurement/vendors/{vendor_id}/scorecard", headers=self.headers)
        self.assertEqual(sc_resp.status_code, 200)
        sc = sc_resp.json()
        self.assertEqual(sc["vendor_name"], v_name)
        self.assertEqual(sc["rating"], 4.8)
        self.assertEqual(sc["tier_classification"], "Tier 1 Strategic Partner")

    def test_12_purchase_requisition_lifecycle(self):
        # 1. Create Requisition
        pr_payload = {
            "department": "Engineering Infrastructure",
            "requested_by": "VP Systems",
            "estimated_budget": 85000.0,
            "notes": "GPU Server expansion for AI inference cluster"
        }
        create_resp = self.proc_client.post("/procurement/requisitions", json=pr_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        pr = create_resp.json()
        pr_id = pr["id"]
        self.assertEqual(pr["status"], "Pending_Approval")

        # 2. Approve Requisition
        appr_resp = self.proc_client.post(f"/procurement/requisitions/{pr_id}/approve", headers=self.headers)
        self.assertEqual(appr_resp.status_code, 200)
        self.assertEqual(appr_resp.json()["status"], "Approved")

        # 3. Convert Requisition to PO
        conv_resp = self.proc_client.post(f"/procurement/requisitions/{pr_id}/convert-to-po", headers=self.headers)
        self.assertEqual(conv_resp.status_code, 200)
        po_data = conv_resp.json()
        self.assertEqual(po_data["total_amount"], 85000.0)
        self.assertEqual(po_data["status"], "Approved")

    def test_13_rfq_bidding_and_vendor_award(self):
        # 1. Create RFQ
        rfq_payload = {
            "title": "Supply of 1,000 Precision Cooling Units",
            "deadline": "2026-11-30"
        }
        create_resp = self.proc_client.post("/procurement/rfqs", json=rfq_payload, headers=self.headers)
        self.assertEqual(create_resp.status_code, 200)
        rfq_id = create_resp.json()["id"]

        # 2. Submit Vendor Bids
        self.proc_client.post(f"/procurement/rfqs/{rfq_id}/bids", json={
            "vendor_id": "v-vendor-alpha",
            "vendor_name": "Alpha Thermal Solutions",
            "bid_amount": 95000.0,
            "delivery_lead_days": 14
        }, headers=self.headers)

        self.proc_client.post(f"/procurement/rfqs/{rfq_id}/bids", json={
            "vendor_id": "v-vendor-beta",
            "vendor_name": "Beta HVAC Technologies",
            "bid_amount": 88000.0,
            "delivery_lead_days": 10
        }, headers=self.headers)

        # 3. Award RFQ to Beta
        award_resp = self.proc_client.post(f"/procurement/rfqs/{rfq_id}/award", json={
            "winning_vendor_id": "v-vendor-beta"
        }, headers=self.headers)
        self.assertEqual(award_resp.status_code, 200)
        award_data = award_resp.json()
        self.assertEqual(award_data["status"], "Awarded")
        bids = json.loads(award_data["vendor_bids"])
        winning_bid = [b for b in bids if b["vendor_id"] == "v-vendor-beta"][0]
        self.assertEqual(winning_bid["status"], "Awarded")

    def test_14_automated_three_way_match_success(self):
        # 1. Create vendor & PO
        v_resp = self.proc_client.post("/procurement/vendors", json={
            "name": f"Premier Electronics {int(datetime.utcnow().timestamp()) % 10000}",
            "contact_email": "premier@supplier.test"
        }, headers=self.headers)
        vendor_id = v_resp.json()["id"]

        po_resp = self.proc_client.post("/procurement/orders", json={
            "vendor_id": vendor_id,
            "order_date": "2026-10-10",
            "items": [
                {"product_sku": "SKU-CHIP-01", "description": "High-Throughput ASICs", "quantity_ordered": 100, "unit_price": 500.0}
            ]
        }, headers=self.headers)
        po_id = po_resp.json()["id"]

        # 2. Record GRN matching ordered quantity (100 units)
        grn_resp = self.proc_client.post(f"/procurement/orders/{po_id}/grn", json={
            "received_by": "Warehouse Supervisor",
            "quantity_received": 100
        }, headers=self.headers)
        self.assertEqual(grn_resp.status_code, 200)

        # 3. Record Vendor Bill matching PO amount ($50,000)
        bill_num = f"BILL-PREMIER-{int(datetime.utcnow().timestamp()) % 10000}"
        bill_resp = self.proc_client.post(f"/procurement/orders/{po_id}/bill", json={
            "bill_number": bill_num,
            "billed_amount": 50000.0
        }, headers=self.headers)
        self.assertEqual(bill_resp.status_code, 200)

        # 4. Execute 3-Way Match
        match_resp = self.proc_client.post(f"/procurement/orders/{po_id}/three-way-match", headers=self.headers)
        self.assertEqual(match_resp.status_code, 200)
        m_data = match_resp.json()
        self.assertEqual(m_data["match_status"], "MATCHED_APPROVED")
        self.assertEqual(m_data["is_verified"], True)

    def test_15_three_way_match_variance_detection(self):
        # 1. Create vendor & PO
        v_resp = self.proc_client.post("/procurement/vendors", json={
            "name": f"Discrepant Vendor Ltd {int(datetime.utcnow().timestamp()) % 10000}",
            "contact_email": "discrepant@vendor.test"
        }, headers=self.headers)
        vendor_id = v_resp.json()["id"]

        po_resp = self.proc_client.post("/procurement/orders", json={
            "vendor_id": vendor_id,
            "order_date": "2026-10-10",
            "items": [
                {"product_sku": "SKU-RELAY-02", "description": "Heavy Relays", "quantity_ordered": 50, "unit_price": 200.0}
            ]
        }, headers=self.headers)
        po_id = po_resp.json()["id"]

        # 2. Record GRN with shortfall (only 35 units received instead of 50)
        self.proc_client.post(f"/procurement/orders/{po_id}/grn", json={
            "received_by": "Warehouse Receiver",
            "quantity_received": 35
        }, headers=self.headers)

        # 3. Record Vendor Bill overcharging ($12,000 instead of $10,000)
        bill_num = f"BILL-DISCREPANT-{int(datetime.utcnow().timestamp()) % 10000}"
        self.proc_client.post(f"/procurement/orders/{po_id}/bill", json={
            "bill_number": bill_num,
            "billed_amount": 12000.0
        }, headers=self.headers)

        # 4. Execute 3-Way Match -> Must flag mismatch
        match_resp = self.proc_client.post(f"/procurement/orders/{po_id}/three-way-match", headers=self.headers)
        self.assertEqual(match_resp.status_code, 200)
        m_data = match_resp.json()
        self.assertEqual(m_data["match_status"], "MISMATCH_DETECTED")
        self.assertEqual(m_data["is_verified"], False)
        self.assertIn("Variance detected", m_data["audit_notes"])

if __name__ == "__main__":
    unittest.main()
