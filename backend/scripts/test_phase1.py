#!/usr/bin/env python3
"""
Test Suite for Phase 1: Microservices Foundation, Shared Core & Event Bus
Executes deep automated assertions on all Phase 1 components.
"""
import os
import sys
import asyncio
import time

# Ensure backend root is on sys.path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.config import ServiceConfig, get_service_config
from common.models import Base, TenantModel, generate_uuid
from common.database import create_db_manager
from common.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    UserContext
)
from common.event_bus import EventBus, DomainEvent
from sqlalchemy import Column, String

# Sample Entity inheriting from TenantModel for testing
class TestSampleEntity(TenantModel):
    __tablename__ = "test_sample_entities"
    title = Column(String(100), nullable=False)

def test_config():
    print("[1/5] Testing Service Configuration...")
    cfg = get_service_config("crm-service", default_port=8002, db_filename="crm_test.db")
    assert cfg.service_name == "crm-service"
    assert cfg.service_port == 8002
    assert "crm_test.db" in cfg.database_url or "postgres" in cfg.database_url or "supabase" in cfg.database_url
    print("  [OK] ServiceConfig instantiated and validated correctly.")

def test_models_and_database():
    print("[2/5] Testing TenantModel and DatabaseManager...")
    test_db_file = os.path.join(backend_dir, "test_phase1.db")
    if os.path.exists(test_db_file):
        try:
            os.remove(test_db_file)
        except Exception:
            pass

    db_mgr = create_db_manager(f"sqlite:///{test_db_file}")
    db_mgr.init_tables(Base)

    # Insert a record via session
    gen = db_mgr.get_session()
    session = next(gen)

    item = TestSampleEntity(
        org_id="org-enterprise-999",
        title="Test Microservice Entity"
    )
    session.add(item)
    session.commit()
    session.refresh(item)

    assert item.id is not None
    assert len(item.id) == 36 # Valid UUID format
    assert item.org_id == "org-enterprise-999"
    assert item.created_at is not None

    d = item.to_dict()
    assert d["title"] == "Test Microservice Entity"
    assert d["org_id"] == "org-enterprise-999"
    assert isinstance(d["created_at"], str)

    # Query back
    queried = session.query(TestSampleEntity).filter_by(id=item.id).first()
    assert queried is not None
    assert queried.title == "Test Microservice Entity"

    session.close()
    db_mgr.engine.dispose()
    if os.path.exists(test_db_file):
        try:
            os.remove(test_db_file)
        except Exception:
            pass

    print("  [OK] TenantModel and DatabaseManager fully functional with SQLite.")

def test_security():
    print("[3/5] Testing Security (PBKDF2 Password Hashing & JWT)...")
    # Password hashing
    password = "EnterpriseSecurePassword2026!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False

    # JWT Tokens
    payload_data = {"sub": "usr-12345", "org_id": "org-999", "role": "admin", "email": "test@bms.com"}
    token = create_access_token(payload_data, expires_minutes=30)
    assert isinstance(token, str)

    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "usr-12345"
    assert decoded["org_id"] == "org-999"
    assert decoded["role"] == "admin"

    # Tampered token check
    tampered_token = token[:-5] + "XXXXX"
    assert decode_access_token(tampered_token) is None
    print("  [OK] Password hashing, verification, and JWT issuance/decoding verified.")

async def async_test_event_bus():
    print("[4/5] Testing Asynchronous Event Bus (Pub/Sub Choreography)...")
    bus = EventBus()
    received_events = []

    async def handle_deal_won(event: DomainEvent):
        received_events.append(event)

    async def handle_wildcard(event: DomainEvent):
        received_events.append(event)

    bus.subscribe("deal.won", handle_deal_won)
    bus.subscribe("*", handle_wildcard)

    event = await bus.publish(
        event_name="deal.won",
        payload={"deal_id": "DEAL-500", "amount": 125000.0, "client": "Apex Dynamics Corp"},
        org_id="org-acroflow"
    )

    # Allow event loop to process background tasks
    await asyncio.sleep(0.05)

    assert len(received_events) == 2 # handle_deal_won + handle_wildcard
    assert received_events[0].event_name == "deal.won"
    assert received_events[0].payload["amount"] == 125000.0
    assert received_events[0].payload["client"] == "Apex Dynamics Corp"

    # Check history
    history = bus.get_history()
    assert len(history) == 1
    assert history[0]["event_name"] == "deal.won"
    print("  [OK] Non-blocking EventBus pub/sub choreography verified.")

def test_event_bus():
    asyncio.run(async_test_event_bus())

def test_orchestration_registry():
    print("[5/5] Testing Microservices Orchestrator Registry...")
    from scripts.dev_orchestrator import SERVICES, get_python_exe
    assert len(SERVICES) == 14
    ports = [s["port"] for s in SERVICES]
    assert len(ports) == len(set(ports)) # All ports unique
    assert 8000 in ports # Gateway
    assert 8001 in ports # Auth
    assert 8002 in ports # CRM
    assert 8013 in ports # AI Copilot
    python_exe = get_python_exe()
    assert os.path.exists(python_exe)
    print("  [OK] 14 microservice port allocations verified without conflict.")

def main():
    print("=" * 65)
    print("  BMS PHASE 1 VALIDATION TEST SUITE")
    print("=" * 65)
    test_config()
    test_models_and_database()
    test_security()
    test_event_bus()
    test_orchestration_registry()
    print("=" * 65)
    print("  ALL PHASE 1 AUTOMATED TESTS PASSED SUCCESSFULLY! (5/5)")
    print("=" * 65)

if __name__ == "__main__":
    main()
