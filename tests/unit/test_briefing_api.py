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

class TestBriefingAPI(unittest.TestCase):
    def setUp(self):
        self.client_manager = TestClient(app)
        self.client = self.client_manager.__enter__()

    def tearDown(self):
        self.client_manager.__exit__(None, None, None)

    def test_briefing_endpoint_and_counts_reconciliation(self):
        # Initial refresh to populate briefing data
        self.client.post("/api/v1/refresh")

        response = self.client.get("/api/v1/briefing")
        self.assertEqual(response.status_code, 200)
        json_data = response.json()
        
        self.assertIn("data", json_data)
        self.assertIn("meta", json_data)
        
        tiers = json_data["data"]["tiers"]
        summary = json_data["data"]["summary"]

        self.assertIn("needs_attention", tiers)
        self.assertIn("worth_a_look", tiers)
        self.assertIn("routine", tiers)

        # Reconcile counts
        counted_events = len(tiers["needs_attention"]) + len(tiers["worth_a_look"]) + len(tiers["routine"])
        self.assertEqual(summary["total_events"], counted_events, "Summary total_events must equal sum of tiered items")
        self.assertEqual(summary["needs_attention_count"], len(tiers["needs_attention"]))
        self.assertEqual(summary["worth_a_look_count"], len(tiers["worth_a_look"]))
        self.assertEqual(summary["routine_count"], len(tiers["routine"]))

    def test_briefing_custom_date_window(self):
        response = self.client.get("/api/v1/briefing?start=2026-01-01T00:00:00Z&end=2026-12-31T23:59:59Z")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("summary", data["data"])

    def test_removed_demo_evidence_is_not_fabricated(self):
        response = self.client.get("/api/v1/evidence/ev-preview-101")
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
