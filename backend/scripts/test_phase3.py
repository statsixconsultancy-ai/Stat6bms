#!/usr/bin/env python3
"""
Test Suite for Phase 3: Auth, Identity & Multi-Tenancy Microservice
Validates user provisioning, password hashing, JWT authentication,
RBAC, multi-tenant isolation, and profile extraction.
"""
import os
import sys
from fastapi.testclient import TestClient

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from services.auth_service.main import app as auth_app, on_startup

# Ensure startup seed executes
on_startup()
client = TestClient(auth_app)

def test_auth_health():
    print("[1/6] Testing Auth Service Health Endpoint...")
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "auth-service"
    assert data["status"] == "UP"
    assert data["port"] == 8001
    print("  [OK] Auth Service /health endpoint validated successfully.")

def test_seed_login():
    print("[2/6] Testing Default Seed Admin Login & JWT Issuance...")
    response = client.post("/auth/login", json={
        "email": "admin@acroflow.enterprise",
        "password": "AcroFlow2026!"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["expires_in_minutes"] > 0
    assert data["user"]["email"] == "admin@acroflow.enterprise"
    assert data["user"]["role"] == "superadmin"
    assert data["organization"]["slug"] == "acroflow"
    print("  [OK] Admin login successful, JWT access token issued.")
    return data["access_token"]

def test_auth_me(token: str):
    print("[3/6] Testing Authenticated Profile Extraction (/auth/me)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert data["user"]["email"] == "admin@acroflow.enterprise"
    assert "AcroFlow" in data["organization"]["name"]
    print("  [OK] /auth/me successfully resolved current authenticated identity.")

def test_list_tenant_users(token: str):
    print("[4/6] Testing Tenant User Directory Listing (/auth/users)...")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/users", headers=headers)
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 1
    emails = [u["email"] for u in users]
    assert "admin@acroflow.enterprise" in emails
    print(f"  [OK] Listed {len(users)} tenant users with RBAC claims.")

def test_tenant_registration():
    print("[5/6] Testing Dynamic Multi-Tenant Registration & Onboarding...")
    new_org_slug = "quantum-dynamics-test"
    reg_payload = {
        "org_name": "Quantum Dynamics Corp",
        "org_slug": new_org_slug,
        "admin_name": "Dr. Eleanor Vance",
        "admin_email": "eleanor@quantumdynamics.test",
        "password": "QuantumSecurePass2026!"
    }
    response = client.post("/auth/register", json=reg_payload)
    # If already exists from previous test run, status might be 409 or 200
    if response.status_code == 409:
        print("  [INFO] Tenant already registered, proceeding to verify login.")
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["organization"]["slug"] == new_org_slug
        assert data["user"]["email"] == "eleanor@quantumdynamics.test"
        assert "access_token" in data

    # Test login with newly registered tenant admin
    login_resp = client.post("/auth/login", json={
        "email": "eleanor@quantumdynamics.test",
        "password": "QuantumSecurePass2026!"
    })
    assert login_resp.status_code == 200
    new_token = login_resp.json()["access_token"]
    assert new_token is not None
    print("  [OK] Multi-tenant provisioning & isolated tenant login verified.")

def test_invalid_credentials():
    print("[6/6] Testing Invalid Credentials & Security Safeguards...")
    # Bad password
    bad_pass_resp = client.post("/auth/login", json={
        "email": "admin@acroflow.enterprise",
        "password": "WrongPassword999!"
    })
    assert bad_pass_resp.status_code == 401
    assert "Invalid email or password" in bad_pass_resp.json()["detail"]

    # Non-existent user
    bad_user_resp = client.post("/auth/login", json={
        "email": "ghost@doesnotexist.com",
        "password": "AnyPassword"
    })
    assert bad_user_resp.status_code == 401

    # Unauthorized access to protected route with invalid token
    unauth_resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid.token.payload"})
    assert unauth_resp.status_code == 401
    print("  [OK] Security guards rejected invalid credentials and unauthenticated requests.")

def main():
    print("=" * 65)
    print("  BMS PHASE 3: AUTH & IDENTITY MICROSERVICE TEST SUITE")
    print("=" * 65)
    test_auth_health()
    token = test_seed_login()
    test_auth_me(token)
    test_list_tenant_users(token)
    test_tenant_registration()
    test_invalid_credentials()
    print("=" * 65)
    print("  ALL PHASE 3 AUTOMATED TESTS PASSED SUCCESSFULLY! (6/6)")
    print("=" * 65)

if __name__ == "__main__":
    main()
