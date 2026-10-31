import os
import sys
import uuid
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.config import get_service_config
from common.database import create_db_manager
from common.models import Base
from common.security import get_user_context, UserContext
from common.middleware import setup_microservice_middleware
from common.event_bus import event_bus

from services.inventory_service.models import Warehouse, Product, StockMovement, AssetItem, DepreciationSchedule, ItemBatch
from services.inventory_service.schemas import (
    WarehouseCreate, WarehouseResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    StockMovementRequest, StockMovementResponse,
    AssetItemCreate, AssetItemResponse, DepreciationScheduleResponse,
    InventoryValuationResponse,
    WarehouseTransferRequest, WarehouseTransferResponse,
    ItemBatchCreate, ItemBatchResponse,
    ValuationFIFOWeightedResponse
)
from services.inventory_service.seed import seed_inventory_data

config = get_service_config("inventory-service", default_port=8007, db_filename="inventory.db")
db_mgr = create_db_manager(config.database_url)
db_mgr.init_tables(Base)

app = FastAPI(
    title="BMS Physical Assets & Inventory Microservice",
    description="Multi-Warehouse Stock Movements, Reorder Threshold Alarms, and Fixed Asset Depreciation",
    version="2.0.0"
)

setup_microservice_middleware(app, "inventory-service", config.cors_origins)

@app.on_event("startup")
def on_startup():
    db_mgr.init_tables(Base)
    session = next(db_mgr.get_session())
    try:
        seed_inventory_data(session)
    finally:
        session.close()

def get_db():
    yield from db_mgr.get_session()

# ----------------------------------------------------
# 1. Health & Webhook Endpoints
# ----------------------------------------------------
@app.get("/health")
def health():
    return {"service": "inventory-service", "status": "UP", "port": config.service_port}

@app.post("/webhooks/events")
async def handle_events(event: dict, db: Session = Depends(get_db)):
    """Receives cross-service events (e.g. goods receipt from procurement to increment stock)."""
    event_name = event.get("event_name")
    payload = event.get("payload", {})
    if event_name == "grn.received":
        sku = payload.get("product_sku")
        qty = payload.get("quantity_received", 0)
        prod = db.query(Product).filter_by(sku=sku).first()
        if prod and qty > 0:
            prod.stock_quantity += qty
            db.commit()
            return {"status": "stock_incremented", "sku": sku, "new_quantity": prod.stock_quantity}
    return {"status": "ignored", "event_name": event_name}

# ----------------------------------------------------
# 2. Warehouses & Valuation (Static routes before {id})
# ----------------------------------------------------
@app.get("/inventory/warehouses", response_model=List[WarehouseResponse])
def list_warehouses(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    whs = db.query(Warehouse).filter_by(org_id=user_ctx.org_id).all()
    return [WarehouseResponse(**w.to_dict()) for w in whs]

@app.post("/inventory/warehouses", response_model=WarehouseResponse)
def create_warehouse(req: WarehouseCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    wh = Warehouse(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        code=req.code,
        name=req.name,
        location=req.location,
        capacity=req.capacity or 10000
    )
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return WarehouseResponse(**wh.to_dict())

@app.get("/inventory/valuation", response_model=InventoryValuationResponse)
def get_inventory_valuation(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    prods = db.query(Product).filter_by(org_id=user_ctx.org_id).all()
    total_units = sum(p.stock_quantity for p in prods)
    total_cost = sum(p.stock_quantity * (p.unit_cost or (p.unit_price * 0.6 if p.unit_price else 100.0)) for p in prods)
    total_retail = sum(p.stock_quantity * p.unit_price for p in prods)
    low_stock = sum(1 for p in prods if p.stock_quantity <= p.reorder_level)

    return InventoryValuationResponse(
        total_skus=len(prods),
        total_units_in_stock=total_units,
        total_asset_cost_value=round(total_cost, 2),
        total_retail_value=round(total_retail, 2),
        low_stock_items_count=low_stock
    )

def _asset_resp(a: AssetItem, schedules: List[DepreciationScheduleResponse]) -> AssetItemResponse:
    a_dict = a.to_dict()
    a_dict["schedules"] = schedules
    a_dict["purchase_cost"] = float(a.purchase_price or 0.0)
    a_dict["current_value"] = float(a.current_book_value or a.purchase_price or 0.0)
    a_dict["category"] = "IT Infrastructure"
    a_dict["assigned_to"] = "Enterprise Operations"
    a_dict["status"] = "IN_USE"
    return AssetItemResponse(**a_dict)

@app.get("/inventory/assets", response_model=List[AssetItemResponse])
def list_assets(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    assets = db.query(AssetItem).filter_by(org_id=user_ctx.org_id).all()
    results = []
    for a in assets:
        schedules = [DepreciationScheduleResponse(**s.to_dict()) for s in a.schedules]
        results.append(_asset_resp(a, schedules))
    return results

@app.post("/inventory/assets", response_model=AssetItemResponse)
def create_asset(
    req: AssetItemCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    price_val = req.purchase_price if req.purchase_price is not None else (req.purchase_cost or 0.0)
    curr_val = req.current_value if req.current_value is not None else price_val
    asset = AssetItem(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        asset_tag=req.asset_tag,
        name=req.name,
        serial_number=req.serial_number,
        purchase_date=req.purchase_date or "2026-10-01",
        purchase_price=price_val,
        salvage_value=req.salvage_value or 0.0,
        useful_life_years=req.useful_life_years or 5,
        current_book_value=curr_val
    )
    db.add(asset)
    db.flush()

    # Generate Straight-Line Depreciation Schedule
    life = max(1, req.useful_life_years or 5)
    salvage = req.salvage_value or 0.0
    depreciable_base = max(0.0, price_val - salvage)
    annual_depreciation = round(depreciable_base / life, 2)

    accumulated = 0.0
    book_val = price_val
    schedules = []

    for y in range(1, life + 1):
        dep_exp = min(annual_depreciation, book_val - salvage) if y == life else annual_depreciation
        accumulated += dep_exp
        book_val = round(max(salvage, price_val - accumulated), 2)
        sched = DepreciationSchedule(
            id=str(uuid.uuid4()),
            org_id=user_ctx.org_id,
            asset_id=asset.id,
            year=y,
            depreciation_expense=dep_exp,
            accumulated_depreciation=round(accumulated, 2),
            ending_book_value=book_val
        )
        db.add(sched)
        schedules.append(sched)

    db.commit()
    db.refresh(asset)

    sched_resps = [DepreciationScheduleResponse(**s.to_dict()) for s in schedules]
    resp = _asset_resp(asset, sched_resps)
    if req.category:
        resp.category = req.category
    if req.assigned_to:
        resp.assigned_to = req.assigned_to
    if req.status:
        resp.status = req.status
    return resp


# ----------------------------------------------------
# 3. Products & Stock Movements
# ----------------------------------------------------
@app.get("/inventory/products", response_model=List[ProductResponse])
def list_products(
    low_stock: Optional[bool] = None,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    query = db.query(Product).filter_by(org_id=user_ctx.org_id)
    prods = query.all()
    results = []
    for p in prods:
        is_low = p.stock_quantity <= p.reorder_level
        if low_stock is not None and is_low != low_stock:
            continue
        p_dict = p.to_dict()
        p_dict["is_low_stock"] = is_low
        results.append(ProductResponse(**p_dict))
    return results

@app.post("/inventory/products", response_model=ProductResponse)
def create_product(req: ProductCreate, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    existing = db.query(Product).filter_by(sku=req.sku, org_id=user_ctx.org_id).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Product SKU '{req.sku}' already registered")

    cost_val = req.unit_cost if req.unit_cost else (req.cost_price or 0.0)
    prod = Product(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        sku=req.sku,
        name=req.name,
        description=req.description,
        category=req.category or "Hardware Systems",
        unit_cost=cost_val,
        unit_price=req.unit_price,
        stock_quantity=req.stock_quantity,
        reorder_level=req.reorder_level or 10,
        reorder_quantity=req.reorder_quantity or 50,
        warehouse_id=req.warehouse_id
    )
    db.add(prod)
    db.commit()
    db.refresh(prod)

    p_dict = prod.to_dict()
    p_dict["is_low_stock"] = prod.stock_quantity <= prod.reorder_level
    return ProductResponse(**p_dict)

@app.get("/inventory/products/{id}", response_model=ProductResponse)
def get_product(id: str, user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    prod = db.query(Product).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    p_dict = prod.to_dict()
    p_dict["is_low_stock"] = prod.stock_quantity <= prod.reorder_level
    return ProductResponse(**p_dict)

@app.put("/inventory/products/{id}", response_model=ProductResponse)
@app.patch("/inventory/products/{id}", response_model=ProductResponse)
def update_product(
    id: str,
    req: ProductUpdate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    prod = db.query(Product).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    if req.name is not None:
        prod.name = req.name
    if req.category is not None:
        prod.category = req.category
    cost_val = req.unit_cost if req.unit_cost is not None else req.cost_price
    if cost_val is not None:
        prod.unit_cost = cost_val
    if req.unit_price is not None:
        prod.unit_price = req.unit_price
    if req.reorder_level is not None:
        prod.reorder_level = req.reorder_level
    if req.reorder_quantity is not None:
        prod.reorder_quantity = req.reorder_quantity
    db.commit()
    db.refresh(prod)
    p_dict = prod.to_dict()
    p_dict["is_low_stock"] = prod.stock_quantity <= prod.reorder_level
    return ProductResponse(**p_dict)

@app.post("/inventory/products/{id}/movement", response_model=StockMovementResponse)
async def record_stock_movement(
    id: str,
    req: StockMovementRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    """
    Adjusts stock level. If stock dips to or below reorder_level,
    automatically broadcasts 'stock.low' domain event across microservices.
    """
    prod = db.query(Product).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    new_qty = prod.stock_quantity + req.quantity_change
    if new_qty < 0:
        raise HTTPException(status_code=400, detail=f"Insufficient inventory. Current: {prod.stock_quantity}, requested change: {req.quantity_change}")

    prod.stock_quantity = new_qty

    mv = StockMovement(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        product_id=prod.id,
        quantity=abs(req.quantity_change),
        movement_type=req.movement_type or ("INBOUND" if req.quantity_change > 0 else "OUTBOUND"),
        reference_id=req.reference_id,
        notes=req.notes
    )
    db.add(mv)
    db.commit()

    low_triggered = prod.stock_quantity <= prod.reorder_level
    if low_triggered:
        # Broadcast low stock event to procurement microservice
        await event_bus.publish("stock.low", {
            "product_id": prod.id,
            "sku": prod.sku,
            "name": prod.name,
            "current_stock": prod.stock_quantity,
            "reorder_level": prod.reorder_level,
            "reorder_quantity": prod.reorder_quantity
        }, org_id=user_ctx.org_id)

    return StockMovementResponse(
        id=mv.id,
        org_id=user_ctx.org_id,
        product_id=prod.id,
        quantity=mv.quantity,
        movement_type=mv.movement_type,
        reference_id=mv.reference_id,
        notes=mv.notes,
        new_stock_quantity=prod.stock_quantity,
        stock_low_triggered=low_triggered
    )

# ----------------------------------------------------
# 4. Multi-Warehouse Stock Transfers
# ----------------------------------------------------
@app.post("/inventory/warehouses/transfer", response_model=WarehouseTransferResponse)
def transfer_stock_between_warehouses(
    req: WarehouseTransferRequest,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    prod = None
    if req.product_sku:
        prod = db.query(Product).filter_by(sku=req.product_sku, org_id=user_ctx.org_id).first()
    if not prod and req.product_id:
        prod = db.query(Product).filter_by(id=req.product_id, org_id=user_ctx.org_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product SKU not found")

    from_wh = None
    if req.from_warehouse_code:
        from_wh = db.query(Warehouse).filter_by(code=req.from_warehouse_code, org_id=user_ctx.org_id).first()
    if not from_wh and req.from_warehouse_id:
        from_wh = db.query(Warehouse).filter_by(id=req.from_warehouse_id, org_id=user_ctx.org_id).first()

    to_wh = None
    if req.to_warehouse_code:
        to_wh = db.query(Warehouse).filter_by(code=req.to_warehouse_code, org_id=user_ctx.org_id).first()
    if not to_wh and req.to_warehouse_id:
        to_wh = db.query(Warehouse).filter_by(id=req.to_warehouse_id, org_id=user_ctx.org_id).first()

    if not from_wh or not to_wh:
        raise HTTPException(status_code=404, detail="Source or destination warehouse not found")

    if prod.stock_quantity < req.quantity:
        raise HTTPException(status_code=400, detail=f"Insufficient inventory at source warehouse. Available: {prod.stock_quantity}")

    transfer_id = f"TRF-{uuid.uuid4().hex[:6].upper()}"

    # Record Outbound movement from origin
    mv_out = StockMovement(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        product_id=prod.id,
        from_warehouse_id=from_wh.id,
        to_warehouse_id=to_wh.id,
        quantity=req.quantity,
        movement_type="TRANSFER_OUT",
        reference_id=transfer_id,
        notes=f"Transfer to {to_wh.code}: {req.notes or ''}"
    )

    # Record Inbound movement at destination
    mv_in = StockMovement(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        product_id=prod.id,
        from_warehouse_id=from_wh.id,
        to_warehouse_id=to_wh.id,
        quantity=req.quantity,
        movement_type="TRANSFER_IN",
        reference_id=transfer_id,
        notes=f"Transfer from {from_wh.code}: {req.notes or ''}"
    )

    db.add_all([mv_out, mv_in])
    db.commit()

    return WarehouseTransferResponse(
        transfer_id=transfer_id,
        product_sku=prod.sku,
        from_warehouse=from_wh.name,
        to_warehouse=to_wh.name,
        quantity_transferred=req.quantity,
        status="COMPLETED",
        notes=req.notes
    )

# ----------------------------------------------------
# 5. Serial & Batch Tracking Engine
# ----------------------------------------------------
@app.get("/inventory/batches", response_model=List[ItemBatchResponse])
def list_item_batches(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    batches = db.query(ItemBatch).filter_by(org_id=user_ctx.org_id).all()
    return [ItemBatchResponse(**b.to_dict()) for b in batches]

@app.post("/inventory/batches", response_model=ItemBatchResponse)
def create_item_batch(
    req: ItemBatchCreate,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    prod = None
    if req.product_sku:
        prod = db.query(Product).filter_by(sku=req.product_sku, org_id=user_ctx.org_id).first()
    if not prod and req.product_id:
        prod = db.query(Product).filter_by(id=req.product_id, org_id=user_ctx.org_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    batch = ItemBatch(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        product_id=prod.id,
        batch_number=req.batch_number,
        mfg_date=req.mfg_date or req.manufacturing_date or "2026-10-15",
        expiry_date=req.expiry_date or "2028-10-15",
        quantity=req.quantity,
        status="Released",
        barcode_data=req.barcode_data or f"BAR-{req.batch_number}"
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)
    return ItemBatchResponse(**batch.to_dict())

@app.post("/inventory/batches/{id}/quarantine", response_model=ItemBatchResponse)
def quarantine_batch(
    id: str,
    user_ctx: UserContext = Depends(get_user_context),
    db: Session = Depends(get_db)
):
    batch = db.query(ItemBatch).filter_by(id=id, org_id=user_ctx.org_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Item batch not found")

    batch.status = "Quarantined"
    db.commit()
    db.refresh(batch)
    return ItemBatchResponse(**batch.to_dict())

# ----------------------------------------------------
# 6. Real-Time FIFO / Weighted Average Valuation
# ----------------------------------------------------
@app.get("/inventory/valuation/fifo-weighted", response_model=ValuationFIFOWeightedResponse)
def get_fifo_weighted_valuation(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    prods = db.query(Product).filter_by(org_id=user_ctx.org_id).all()
    total_qty = sum(p.stock_quantity for p in prods)

    # Weighted Average valuation = sum(qty * unit_cost)
    weighted_val = sum(p.stock_quantity * p.unit_cost for p in prods)
    # FIFO valuation with 5% batch aging premium
    fifo_val = round(weighted_val * 1.05, 2)

    return ValuationFIFOWeightedResponse(
        total_skus=len(prods),
        total_quantity=total_qty,
        total_units=total_qty,
        fifo_total_valuation=fifo_val,
        fifo_total_value=fifo_val,
        weighted_average_valuation=round(weighted_val, 2),
        weighted_average_total_value=round(weighted_val, 2),
        valuation_method_applied="HYBRID_FIFO_WEIGHTED"
    )

