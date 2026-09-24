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

from services.inventory_service.models import Warehouse, Product, StockMovement, AssetItem, DepreciationSchedule
from services.inventory_service.schemas import (
    WarehouseCreate, WarehouseResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    StockMovementRequest, StockMovementResponse,
    AssetItemCreate, AssetItemResponse, DepreciationScheduleResponse,
    InventoryValuationResponse
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
    total_cost = sum(p.stock_quantity * p.unit_cost for p in prods)
    total_retail = sum(p.stock_quantity * p.unit_price for p in prods)
    low_stock = sum(1 for p in prods if p.stock_quantity <= p.reorder_level)

    return InventoryValuationResponse(
        total_skus=len(prods),
        total_units_in_stock=total_units,
        total_asset_cost_value=round(total_cost, 2),
        total_retail_value=round(total_retail, 2),
        low_stock_items_count=low_stock
    )

@app.get("/inventory/assets", response_model=List[AssetItemResponse])
def list_assets(user_ctx: UserContext = Depends(get_user_context), db: Session = Depends(get_db)):
    assets = db.query(AssetItem).filter_by(org_id=user_ctx.org_id).all()
    results = []
    for a in assets:
        schedules = [DepreciationScheduleResponse(**s.to_dict()) for s in a.schedules]
        a_dict = a.to_dict()
        a_dict["schedules"] = schedules
        results.append(AssetItemResponse(**a_dict))
    return results

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

    prod = Product(
        id=str(uuid.uuid4()),
        org_id=user_ctx.org_id,
        sku=req.sku,
        name=req.name,
        description=req.description,
        category=req.category or "Hardware Systems",
        unit_cost=req.unit_cost,
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
