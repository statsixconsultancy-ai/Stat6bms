import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from common.models import Base, TenantModel

class Warehouse(TenantModel):
    __tablename__ = "inv_warehouses"

    code = Column(String(50), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    capacity = Column(Integer, default=10000)

    products = relationship("Product", back_populates="warehouse")

class Product(TenantModel):
    __tablename__ = "inv_products"

    sku = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), default="Hardware Systems", index=True)
    unit_cost = Column(Float, default=0.0)
    unit_price = Column(Float, default=0.0)
    stock_quantity = Column(Integer, default=0, index=True)
    reorder_level = Column(Integer, default=10)
    reorder_quantity = Column(Integer, default=50)
    warehouse_id = Column(String(36), ForeignKey("inv_warehouses.id"), nullable=True, index=True)

    warehouse = relationship("Warehouse", back_populates="products")
    movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")

class StockMovement(TenantModel):
    __tablename__ = "inv_stock_movements"

    product_id = Column(String(36), ForeignKey("inv_products.id"), nullable=False, index=True)
    from_warehouse_id = Column(String(36), nullable=True)
    to_warehouse_id = Column(String(36), nullable=True)
    quantity = Column(Integer, nullable=False)
    movement_type = Column(String(50), default="ADJUSTMENT")  # INBOUND, OUTBOUND, TRANSFER, ADJUSTMENT
    reference_id = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)

    product = relationship("Product", back_populates="movements")

class AssetItem(TenantModel):
    __tablename__ = "inv_asset_items"

    asset_tag = Column(String(50), nullable=False, unique=True, index=True)  # e.g., AST-9001
    name = Column(String(255), nullable=False)
    serial_number = Column(String(100), nullable=True)
    purchase_date = Column(String(50), nullable=False)
    purchase_price = Column(Float, nullable=False)
    salvage_value = Column(Float, default=0.0)
    useful_life_years = Column(Integer, default=5)
    current_book_value = Column(Float, nullable=False)

    schedules = relationship("DepreciationSchedule", back_populates="asset", cascade="all, delete-orphan")

class DepreciationSchedule(TenantModel):
    __tablename__ = "inv_depreciation_schedules"

    asset_id = Column(String(36), ForeignKey("inv_asset_items.id"), nullable=False, index=True)
    year = Column(Integer, nullable=False)
    depreciation_expense = Column(Float, nullable=False)
    accumulated_depreciation = Column(Float, nullable=False)
    ending_book_value = Column(Float, nullable=False)

    asset = relationship("AssetItem", back_populates="schedules")
