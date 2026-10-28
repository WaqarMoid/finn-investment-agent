import os
import sys
import unittest
import sqlite3
from unittest.mock import patch
from pathlib import Path

# Add apps/api to PYTHONPATH
api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from starlette.testclient import TestClient
from finn.main import app
from finn.db.database import get_connection
from finn.db.repository import DataRepository
from finn.jobs.worker import JobManager
from finn.adapters.exchange_adapter import ExchangeAdapter, AnnouncementRecord

class MockFailingExchangeAdapter(ExchangeAdapter):
    """Simulates an upstream exchange adapter failing with HTTP 503 Service Unavailable."""
    def fetch_announcements(self, start_date=None, end_date=None, page=1, max_pages=None, **kwargs):
        raise ConnectionError("Upstream exchange API unavailable (HTTP 503)")

class TestReplayAndResilience(unittest.TestCase):
    def setUp(self):
        self.client_manager = TestClient(app)
        self.client = self.client_manager.__enter__()

    def tearDown(self):
        self.client_manager.__exit__(None, None, None)

    def test_historical_replay_mode_and_fixed_clock(self):
        """Gate: Historical replay clock mode (FINN_MODE=replay) fixes the clock and labels output."""
        with patch.dict(os.environ, {"FINN_MODE": "replay"}):
            resp = self.client.get("/api/v1/briefing")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()

            meta = data["meta"]
            self.assertEqual(meta["mode"], "replay")
            self.assertTrue(meta["is_replay"])
            self.assertIn("Historical Replay", meta["historical_label"])
            self.assertIn("2024-10-18", meta["last_updated_utc"])

            # In replay mode, refreshing returns replay_active without making network calls
            refresh_resp = self.client.post("/api/v1/refresh")
            self.assertEqual(refresh_resp.status_code, 200)
            self.assertEqual(refresh_resp.json()["status"], "replay_active")

    def test_rate_limiting_on_refresh(self):
        """Gate: Rapid consecutive refresh requests trigger HTTP 429 rate limit."""
        with patch.dict(os.environ, {"FINN_MODE": "live"}):
            headers = {"Cookie": "finn_session_id=rate-limit-test-sess"}
            # First refresh request
            r1 = self.client.post("/api/v1/refresh", headers=headers)
            self.assertIn(r1.status_code, [200, 429])

            # Immediate second refresh request must trigger 429
            r2 = self.client.post("/api/v1/refresh", headers=headers)
            self.assertEqual(r2.status_code, 429)
            self.assertIn("Refresh rate limit exceeded", r2.json()["detail"])

    def test_failure_injection_does_not_crash_system(self):
        """Gate: Upstream failure (HTTP 503) does not crash or corrupt database state."""
        from finn.ingestion.announcements import AnnouncementIngestionService
        conn = get_connection()
        try:
            service = AnnouncementIngestionService(conn)
            failing_adapter = MockFailingExchangeAdapter()

            # Ingestion should catch exception, record failure run, and return failure status
            res = service.ingest(failing_adapter)
            self.assertEqual(res["status"], "failed")
            self.assertIn("503", res["error"])

            # System and database remain healthy and queryable
            count = conn.execute("SELECT count(*) FROM companies").fetchone()[0]
            self.assertGreater(count, 0)
        finally:
            conn.close()

    def test_worker_crash_recovery_resumes_expired_leases(self):
        """Gate: Worker crash recovers stale/expired leases upon restart without dropping jobs."""
        conn = get_connection()
        try:
            # Ensure session exists for foreign key
            conn.execute("INSERT OR IGNORE INTO sessions (id, created_at_utc, expires_at_utc) VALUES ('test-crash-session', '2026-10-28T00:00:00Z', '2026-11-28T00:00:00Z')")
            conn.commit()

            jm = JobManager(conn)
            job = jm.enqueue_job(
                job_type="research_task",
                dedup_key="crash-resilience-job-1",
                session_id="test-crash-session",
                company_id="comp-infy-001"
            )
            job_id = job["id"]

            # Simulate worker crash mid-execution: job is running with expired lease in the past
            conn.execute("UPDATE jobs SET status = 'running', lease_until_utc = '2020-01-01T00:00:00Z' WHERE id = ?", (job_id,))
            conn.commit()

            # Worker crashed! Stale job recovery runs on startup
            recovered_count = jm.recover_stale_jobs()
            self.assertGreaterEqual(recovered_count, 1)

            # Verified job status was reset back to 'queued' for retry
            row = conn.execute("SELECT status FROM jobs WHERE id = ?", (job_id,)).fetchone()
            self.assertEqual(row["status"], "queued")
        finally:
            conn.close()

    def test_session_isolation_watchlists_and_rules(self):
        """Gate: Distinct browser sessions maintain fully isolated watchlists and alert thresholds."""
        # Initialize Session A and remove INFY from its watchlist
        client_a = TestClient(app, cookies={"finn_session_id": "sess-alpha-123"})
        client_a.delete("/api/v1/watchlist/comp-infy-001")
        client_a.put("/api/v1/notification-rules", json={
            "price_pct": 2.5,
            "volume_multiple": 2.0,
            "categories": ["financial_results"]
        })

        # Initialize Session B and keep INFY in its watchlist, with different rules
        client_b = TestClient(app, cookies={"finn_session_id": "sess-beta-456"})
        client_b.post("/api/v1/watchlist/comp-infy-001")
        client_b.put("/api/v1/notification-rules", json={
            "price_pct": 8.0,
            "volume_multiple": 3.0,
            "categories": ["dividend"]
        })

        # Verify Session A: INFY was deleted, price_pct is 2.5
        wl_a = client_a.get("/api/v1/watchlist").json()["data"]
        symbols_a = [item["symbol"] for item in wl_a]
        self.assertNotIn("INFY", symbols_a)

        rules_a = client_a.get("/api/v1/notification-rules").json()["data"]
        self.assertEqual(rules_a["price_pct"], 2.5)

        # Verify Session B: INFY is present, price_pct is 8.0
        wl_b = client_b.get("/api/v1/watchlist").json()["data"]
        symbols_b = [item["symbol"] for item in wl_b]
        self.assertIn("INFY", symbols_b)

        rules_b = client_b.get("/api/v1/notification-rules").json()["data"]
        self.assertEqual(rules_b["price_pct"], 8.0)

if __name__ == "__main__":
    unittest.main()
