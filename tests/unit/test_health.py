import os
import sys
import unittest
from pathlib import Path

# Add apps/api to PYTHONPATH
api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from starlette.testclient import TestClient
from finn.main import app

class TestHealthEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_live(self):
        response = self.client.get("/api/v1/health/live")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["version"], "0.1.0")
        self.assertIn("timestamp_utc", data)
        self.assertEqual(data["details"]["process"], "alive")

    def test_health_ready(self):
        response = self.client.get("/api/v1/health/ready")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["details"]["database_accessible"])
        self.assertTrue(data["details"]["fts5_available"])

    def test_session_cookie_isolation(self):
        response = self.client.get("/api/v1/health/live")
        self.assertEqual(response.status_code, 200)
        self.assertIn("finn_session_id", response.cookies)

    def test_spa_serving(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("FINN", response.text)

if __name__ == "__main__":
    unittest.main()
