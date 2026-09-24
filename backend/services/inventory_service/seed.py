import uuid
from sqlalchemy.orm import Session
from services.inventory_service.models import Warehouse, Product, AssetItem, DepreciationSchedule

def seed_inventory_data(session: Session, org_id: str = "org-acroflow-main"):
    """Seeds physical warehouses, specialized hardware SKUs, and capital fixed assets."""
    if session.query(Warehouse).filter_by(org_id=org_id).first():
        return

    # 1. Warehouses
    wh1 = Warehouse(id=str(uuid.uuid4()), org_id=org_id, code="WH-BOS-01", name="Boston Robotics Logistics Hub", location="Boston, MA", capacity=15000)
    wh2 = Warehouse(id=str(uuid.uuid4()), org_id=org_id, code="WH-SFO-02", name="Silicon Valley Edge Hardware Vault", location="San Jose, CA", capacity=8000)
    session.add_all([wh1, wh2])
    session.flush()

    # 2. Products
    p1 = Product(
        id=str(uuid.uuid4()),
        org_id=org_id,
        sku="HW-204",
        name="LiDAR Spatial Scanning Array",
        description="High-frequency 360-degree point cloud telemetry sensor for autonomous rovers.",
        category="Robotics Sensors",
        unit_cost=1200.0,
        unit_price=2800.0,
        stock_quantity=24,
        reorder_level=10,
        reorder_quantity=30,
        warehouse_id=wh1.id
    )
    p2 = Product(
        id=str(uuid.uuid4()),
        org_id=org_id,
        sku="HW-501",
        name="Embedded Jetson Tensor Compute Core",
        description="Accelerated edge neural inference board with 64GB Unified Memory.",
        category="Compute Modules",
        unit_cost=850.0,
        unit_price=1650.0,
        stock_quantity=8,
        reorder_level=15,
        reorder_quantity=40,
        warehouse_id=wh1.id
    )
    p3 = Product(
        id=str(uuid.uuid4()),
        org_id=org_id,
        sku="HW-709",
        name="Mil-Spec High-Torque Brushless Actuator",
        description="IP67 sealed servomotor capable of 120Nm sustained stall torque.",
        category="Mechanical Actuators",
        unit_cost=420.0,
        unit_price=950.0,
        stock_quantity=55,
        reorder_level=20,
        reorder_quantity=50,
        warehouse_id=wh2.id
    )
    session.add_all([p1, p2, p3])
    session.flush()

    # 3. Capital Fixed Asset
    ast1 = AssetItem(
        id=str(uuid.uuid4()),
        org_id=org_id,
        asset_tag="AST-9001",
        name="Haas 5-Axis Precision CNC Machining Center",
        serial_number="HAAS-VF2-99812",
        purchase_date="2024-01-15",
        purchase_price=150000.0,
        salvage_value=10000.0,
        useful_life_years=5,
        current_book_value=94000.0
    )
    session.add(ast1)
    session.flush()

    # Schedules for AST-9001: ($150,000 - $10,000) / 5 = $28,000/yr depreciation
    ds1 = DepreciationSchedule(id=str(uuid.uuid4()), org_id=org_id, asset_id=ast1.id, year=1, depreciation_expense=28000.0, accumulated_depreciation=28000.0, ending_book_value=122000.0)
    ds2 = DepreciationSchedule(id=str(uuid.uuid4()), org_id=org_id, asset_id=ast1.id, year=2, depreciation_expense=28000.0, accumulated_depreciation=56000.0, ending_book_value=94000.0)
    session.add_all([ds1, ds2])
    session.commit()
