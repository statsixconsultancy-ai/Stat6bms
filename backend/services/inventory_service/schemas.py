from typing import Optional, List
from pydantic import BaseModel

# --- Warehouse Schemas ---
class WarehouseCreate(BaseModel):
    code: str
    name: str
    location: str
    capacity: Optional[int] = 10000

class WarehouseResponse(BaseModel):
    id: str
    org_id: str
    code: str
    name: str
    location: str
    capacity: int

# --- Product Schemas ---
class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = "Hardware Systems"
    unit_cost: float = 0.0
    unit_price: float = 0.0
    stock_quantity: int = 0
    reorder_level: Optional[int] = 10
    reorder_quantity: Optional[int] = 50
    warehouse_id: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    unit_cost: Optional[float] = None
    unit_price: Optional[float] = None
    reorder_level: Optional[int] = None
    reorder_quantity: Optional[int] = None

class ProductResponse(BaseModel):
    id: str
    org_id: str
    sku: str
    name: str
    description: Optional[str] = None
    category: str
    unit_cost: float
    unit_price: float
    stock_quantity: int
    reorder_level: int
    reorder_quantity: int
    warehouse_id: Optional[str] = None
    is_low_stock: bool = False

# --- Stock Movement Schemas ---
class StockMovementRequest(BaseModel):
    quantity_change: int  # positive for INBOUND, negative for OUTBOUND
    movement_type: Optional[str] = "ADJUSTMENT"  # INBOUND, OUTBOUND, TRANSFER, ADJUSTMENT
    reference_id: Optional[str] = None
    notes: Optional[str] = None

class StockMovementResponse(BaseModel):
    id: str
    org_id: str
    product_id: str
    quantity: int
    movement_type: str
    reference_id: Optional[str] = None
    notes: Optional[str] = None
    new_stock_quantity: int
    stock_low_triggered: bool

# --- Asset & Depreciation Schemas ---
class AssetItemCreate(BaseModel):
    asset_tag: str
    name: str
    serial_number: Optional[str] = None
    purchase_date: str
    purchase_price: float
    salvage_value: Optional[float] = 0.0
    useful_life_years: Optional[int] = 5

class DepreciationScheduleResponse(BaseModel):
    year: int
    depreciation_expense: float
    accumulated_depreciation: float
    ending_book_value: float

class AssetItemResponse(BaseModel):
    id: str
    org_id: str
    asset_tag: str
    name: str
    serial_number: Optional[str] = None
    purchase_date: str
    purchase_price: float
    salvage_value: float
    useful_life_years: int
    current_book_value: float
    schedules: List[DepreciationScheduleResponse] = []

# --- Summary ---
class InventoryValuationResponse(BaseModel):
    total_skus: int
    total_units_in_stock: int
    total_asset_cost_value: float
    total_retail_value: float
    low_stock_items_count: int
