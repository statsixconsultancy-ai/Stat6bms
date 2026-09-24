#!/usr/bin/env python3
"""
Test Suite for Phase 9: Supply Chain & Physical Assets
Validates:
1. Inventory Service (port 8007): Multi-warehouse stocks, valuation, and 'stock.low' alarm trigger.
2. Procurement Service (port 8008): Automated PO replenishment, GRN logging, and 3-Way Matching Verification.
"""
import os
import sys
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.inventory_service.main import app as inventory_app, on_startup as inv_startup
from services.procurement_service.main import app as procurement_app, on_startup as proc_startup

inv_startup()
proc_startup()

inv_client = TestClient(inventory_app)
proc_client = TestClient(procurement_app)

def test_inventory_and_procurement_health():
    print("[1/6] Testing Inventory & Procurement Microservices Health Endpoints...")
    inv_h = inv_client.get("/health")
    assert inv_h.status_code == 200
    assert inv_h.json()["service"] == "inventory-service"
    assert inv_h.json()["port"] == 8007

    proc_h = proc_client.get("/health")
    assert proc_h.status_code == 200
    assert proc_h.json()["service"] == "procurement-service"
    assert proc_h.json()["port"] == 8008
    print("  [OK] Both Inventory (:8007) and Procurement (:8008) microservices UP and healthy.")

def test_inventory_valuation_and_products():
    print("[2/6] Testing Inventory Valuation & Product Registry...")
    val_resp = inv_client.get("/inventory/valuation")
    assert val_resp.status_code == 200
    val = val_resp.json()
    assert val["total_skus"] >= 3
    assert val["total_units_in_stock"] > 0
    assert val["total_asset_cost_value"] > 0
    assert val["low_stock_items_count"] >= 1
    print(f"  [OK] Inventory Asset Valuation: ${val['total_asset_cost_value']:,.2f} across {val['total_units_in_stock']} physical units ({val['low_stock_items_count']} low-stock alerts).")

def test_stock_movement_low_trigger():
    print("[3/6] Testing Stock Outbound Movement & 'stock.low' Trigger...")
    prods = inv_client.get("/inventory/products").json()
    hw_204 = [p for p in prods if p["sku"] == "HW-204"][0]
    p_id = hw_204["id"]

    current_stock = hw_204["stock_quantity"]
    if current_stock <= 10:
        inv_client.post(f"/inventory/products/{p_id}/movement", json={
            "quantity_change": 24 - current_stock,
            "movement_type": "INBOUND"
        })
        current_stock = 24

    # Deduct units to trigger reorder threshold (drops to 6 <= 10)
    deduct = current_stock - 6
    mv_resp = inv_client.post(f"/inventory/products/{p_id}/movement", json={
        "quantity_change": -deduct,
        "movement_type": "OUTBOUND",
        "notes": "Rover assembly production line consumption."
    })
    assert mv_resp.status_code == 200
    mv = mv_resp.json()
    assert mv["new_stock_quantity"] == 6
    assert mv["stock_low_triggered"] == True
    print(f"  [OK] Outbound adjustment recorded: SKU HW-204 reduced to 6 units. Low-stock trigger ACTIVATED.")
    return hw_204

def test_procurement_auto_replenishment():
    print("[4/6] Testing Procurement Auto-Replenishment on 'stock.low' Webhook...")
    low_event = {
        "event_name": "stock.low",
        "payload": {
            "sku": "HW-204",
            "name": "LiDAR Spatial Scanning Array",
            "current_stock": 6,
            "reorder_level": 10,
            "reorder_quantity": 30
        },
        "org_id": "org-acroflow-main"
    }
    po_resp = proc_client.post("/webhooks/events", json=low_event)
    assert po_resp.status_code == 200
    data = po_resp.json()
    assert data["status"] == "po_auto_drafted"
    assert data["quantity"] == 30
    print(f"  [OK] Procurement received 'stock.low' and automatically drafted PO {data['po_number']} for {data['quantity']} units.")

def test_three_way_match_successful():
    print("[5/6] Testing Three-Way Matching Engine (PO == GRN == Vendor Bill)...")
    # 1. Fetch vendor
    vendors = proc_client.get("/procurement/vendors").json()
    assert len(vendors) >= 1
    v_id = vendors[0]["id"]

    # 2. Create PO for 50 units @ $100 = $5,000
    po_payload = {
        "vendor_id": v_id,
        "order_date": "2026-09-24",
        "items": [{"product_sku": "HW-MTR-10", "description": "Stepper Motor", "quantity_ordered": 50, "unit_price": 100.0}]
    }
    po_resp = proc_client.post("/procurement/orders", json=po_payload)
    assert po_resp.status_code == 200
    po = po_resp.json()
    po_id = po["id"]
    assert po["total_amount"] == 5000.0

    # 3. Record Goods Receipt Note (GRN) for full 50 units
    grn_resp = proc_client.post(f"/procurement/orders/{po_id}/grn", json={
        "quantity_received": 50,
        "received_by": "Warehouse Lead"
    })
    assert grn_resp.status_code == 200

    # 4. Record Vendor Bill for exactly $5,000
    bill_resp = proc_client.post(f"/procurement/orders/{po_id}/bill", json={
        "bill_number": f"BILL-{po['po_number']}",
        "billed_amount": 5000.0
    })
    assert bill_resp.status_code == 200

    # 5. Execute 3-way match
    match_resp = proc_client.post(f"/procurement/orders/{po_id}/three-way-match")
    assert match_resp.status_code == 200
    res = match_resp.json()
    assert res["is_verified"] == True
    assert res["match_status"] == "MATCHED_APPROVED"
    assert res["ordered_quantity"] == res["received_quantity"] == 50
    assert res["po_amount"] == res["billed_amount"] == 5000.0
    print(f"  [OK] Three-Way Match PASSED: 50 ordered == 50 received, $5,000 PO == $5,000 Billed. PO Approved.")
    return v_id

def test_three_way_match_variance_detection(vendor_id: str):
    print("[6/6] Testing Three-Way Match Anomaly & Variance Detection...")
    # Create PO for 10 units @ $200 = $2,000
    po_payload = {
        "vendor_id": vendor_id,
        "items": [{"product_sku": "HW-SENS-01", "description": "Thermal Sensor", "quantity_ordered": 10, "unit_price": 200.0}]
    }
    po = proc_client.post("/procurement/orders", json=po_payload).json()
    po_id = po["id"]

    # GRN only received 8 units (Short shipment)
    proc_client.post(f"/procurement/orders/{po_id}/grn", json={"quantity_received": 8})

    # Vendor billed full $2,000 (Overbilled)
    import uuid
    proc_client.post(f"/procurement/orders/{po_id}/bill", json={"bill_number": f"BILL-MISMATCH-{uuid.uuid4().hex[:6]}", "billed_amount": 2000.0})

    # Run 3-way match
    match_resp = proc_client.post(f"/procurement/orders/{po_id}/three-way-match").json()
    assert match_resp["is_verified"] == False
    assert match_resp["match_status"] == "MISMATCH_DETECTED"
    assert "Variance detected" in match_resp["audit_notes"]
    print("  [OK] Anomaly caught: Short shipment (8 received vs 10 ordered) correctly flagged and payment disbursement locked.")

def main():
    print("=" * 65)
    print("  BMS PHASE 9: INVENTORY & PROCUREMENT TEST SUITE")
    print("=" * 65)
    test_inventory_and_procurement_health()
    test_inventory_valuation_and_products()
    test_stock_movement_low_trigger()
    test_procurement_auto_replenishment()
    v_id = test_three_way_match_successful()
    test_three_way_match_variance_detection(v_id)
    print("=" * 65)
    print("  ALL PHASE 9 AUTOMATED TESTS PASSED SUCCESSFULLY! (6/6)")
    print("=" * 65)

if __name__ == "__main__":
    main()
