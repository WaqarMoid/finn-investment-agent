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

class TestFilingsAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_filings_and_refresh_flow(self):
        # 1. Trigger manual refresh
        r_refresh = self.client.post("/api/v1/refresh")
        self.assertIn(r_refresh.status_code, [200, 429])

        # 2. Get filings
        r_filings = self.client.get("/api/v1/filings?limit=10")
        self.assertEqual(r_filings.status_code, 200)
        data = r_filings.json()
        self.assertIn("data", data)
        self.assertIn("meta", data)
        self.assertIsInstance(data["data"], list)

        # 3. Test rate limiting on rapid second refresh
        r_rapid = self.client.post("/api/v1/refresh")
        self.assertEqual(r_rapid.status_code, 429)
        self.assertIn("rate limit exceeded", r_rapid.json()["detail"].lower())

if __name__ == "__main__":
    unittest.main()
