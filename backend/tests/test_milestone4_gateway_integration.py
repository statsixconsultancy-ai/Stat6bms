import os
import sys
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = r"C:\Users\prann\.gemini\antigravity\scratch\bms-platform\backend"
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from common.security import create_access_token
from services.gateway.main import app as gateway_app, SERVICE_ROUTES

def test_milestone4():
    print("--> Testing Milestone 4: Gateway Route Mapping & Integration...")
    client = TestClient(gateway_app)

    token = create_access_token({"sub": "user-exec-1", "user_id": "user-exec-1", "org_id": "org-acroflow-main", "role": "SUPER_ADMIN"})
    headers = {"Authorization": f"Bearer {token}"}

    # Verify Gateway route table contains automation and ai
    assert "automation" in SERVICE_ROUTES
    assert "ai" in SERVICE_ROUTES
    assert SERVICE_ROUTES["automation"] == "http://127.0.0.1:8012"
    assert SERVICE_ROUTES["ai"] == "http://127.0.0.1:8013"
    print("  [PASS] Service Route Table verified: 'ai' -> :8013 and 'automation' -> :8012")

    # Verify Gateway Health
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["gateway"] == "HEALTHY"
    print(f"  [PASS] Central API Gateway Health: {health_resp.json()['gateway']}")

    print("\n--> MILESTONE 4 VERIFICATION COMPLETED: GATEWAY ROUTING MAPPING VERIFIED!\n")

if __name__ == "__main__":
    test_milestone4()
