import unittest
from fastapi.testclient import TestClient
from services.auth_service.main import app

class TestNativeOAuth(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_oauth_token_password_grant_success(self):
        resp = self.client.post("/auth/oauth/token", json={
            "grant_type": "password",
            "username": "admin@acroflow.enterprise",
            "password": "Password123!"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["token_type"], "bearer")
        self.assertEqual(data["persona"], "ADMIN")
        self.assertEqual(data["role"], "superadmin")

    def test_oauth_token_vendor_grant(self):
        resp = self.client.post("/auth/oauth/token", json={
            "grant_type": "password",
            "email": "supplier@portal.enterprise",
            "password": "Password123!"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["persona"], "VENDOR")

    def test_oauth_token_invalid_password(self):
        resp = self.client.post("/auth/oauth/token", json={
            "grant_type": "password",
            "username": "admin@acroflow.enterprise",
            "password": "WrongPassword!"
        })
        self.assertEqual(resp.status_code, 401)

    def test_oauth_userinfo(self):
        token_resp = self.client.post("/auth/oauth/token", json={
            "grant_type": "password",
            "username": "admin@acroflow.enterprise",
            "password": "Password123!"
        })
        token = token_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        userinfo_resp = self.client.get("/auth/oauth/userinfo", headers=headers)
        self.assertEqual(userinfo_resp.status_code, 200)
        data = userinfo_resp.json()
        self.assertEqual(data["email"], "admin@acroflow.enterprise")
        self.assertEqual(data["persona"], "ADMIN")

if __name__ == "__main__":
    unittest.main()
