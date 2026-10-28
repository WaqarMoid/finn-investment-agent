import os
import sys
import unittest
import sqlite3
import tempfile
import shutil
from pathlib import Path
from decimal import Decimal

# Add apps/api to PYTHONPATH
api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from finn.db.database import get_connection, init_db
from finn.db.repository import DataRepository
from finn.adapters.exchange_adapter import (
    ExchangeAdapter,
    AnnouncementRecord,
    FixtureExchangeAdapter,
    BSEExchangeAdapter
)
from finn.ingestion.announcements import AnnouncementIngestionService
from finn.jobs.worker import JobManager

class MockPartialExchangeAdapter(ExchangeAdapter):
    """Simulates a middle-page network failure during multi-page pagination."""
    def fetch_announcements(self, start_date=None, end_date=None, max_pages=3):
        return {
            "records": [
                AnnouncementRecord(
                    exchange="NSE",
                    source_id="mock-page-1-rec-1",
                    symbol="INFY",
                    published_at_utc="2026-10-28T10:00:00Z",
                    title="Outcome of Board Meeting",
                    description="Financial results submitted"
                )
            ],
            "pages_completed": 1,
            "total_pages_expected": 3,
            "status": "partial",
            "error": "Failed fetching page 2: Connection timed out"
        }

class MockRateLimitedAdapter(ExchangeAdapter):
    """Simulates an exchange returning HTTP 429 rate limit."""
    def fetch_announcements(self, start_date=None, end_date=None, max_pages=3):
        return {
            "records": [],
            "pages_completed": 0,
            "total_pages_expected": 1,
            "status": "partial",
            "error": "NSE returned HTTP 429 (rate limited)"
        }

class TestJobsAndIngestion(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_ingestion.db")
        init_db(self.db_path)
        self.conn = get_connection(self.db_path)
        self.repo = DataRepository(self.conn)
        self.repo.seed_master_data()
        self.service = AnnouncementIngestionService(self.conn)
        self.job_manager = JobManager(self.conn)
        self.fixture_path = str(
            Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures" / "source" / "nse_announcements_sample.json"
        )

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_watermark_not_advanced_on_partial_page_failure(self):
        """Failed middle page must NOT advance the full watermark and must record partial status."""
        adapter = MockPartialExchangeAdapter()
        res = self.service.ingest(adapter)
        self.assertEqual(res["status"], "partial")
        self.assertFalse(res["watermark_advanced"])
        
        # Check sync_runs record
        row = self.conn.execute("SELECT status, error_message FROM sync_runs WHERE id = ?", (res["sync_id"],)).fetchone()
        self.assertEqual(row["status"], "partial")
        self.assertIn("Connection timed out", row["error_message"])

    def test_duplicate_poll_emits_no_duplicate_announcement(self):
        """Re-polling the same exchange feed must not insert duplicate rows or duplicate events."""
        adapter = FixtureExchangeAdapter(fixture_path=self.fixture_path)
        
        # First poll
        res1 = self.service.ingest(adapter)
        self.assertEqual(res1["status"], "completed")
        self.assertTrue(res1["watermark_advanced"])
        count_first = self.conn.execute("SELECT count(*) FROM announcements").fetchone()[0]
        self.assertGreater(count_first, 0)

        # Second identical poll
        res2 = self.service.ingest(adapter)
        self.assertEqual(res2["status"], "completed")
        self.assertGreater(res2["counts"]["duplicate_announcements"], 0)
        self.assertEqual(res2["counts"]["inserted_announcements"], 0)
        
        count_second = self.conn.execute("SELECT count(*) FROM announcements").fetchone()[0]
        self.assertEqual(count_first, count_second, "Duplicate announcements must not increase row count")

    def test_bse_adapter_403_becomes_visible_partial_state(self):
        """Disabled / blocked exchange (BSE) produces visible partial state without crashing."""
        bse = BSEExchangeAdapter()
        res = self.service.ingest(bse)
        self.assertEqual(res["status"], "partial")
        self.assertFalse(res["watermark_advanced"])
        self.assertIn("HTTP 403", res["error"])

    def test_source_429_rate_limit_state(self):
        adapter = MockRateLimitedAdapter()
        res = self.service.ingest(adapter)
        self.assertEqual(res["status"], "partial")
        self.assertIn("429", res["error"])

    def test_worker_lease_and_stale_recovery(self):
        """Durable job queue leases jobs atomically and recovers stale jobs after simulated crash."""
        job = self.job_manager.enqueue_job("test_task", dedup_key="key-test-01")
        self.assertEqual(job["status"], "queued")

        # Worker 1 claims job with expired lease (expired 5 seconds ago)
        claimed = self.job_manager.claim_job(lease_seconds=-5)
        self.assertIsNotNone(claimed)
        self.assertEqual(claimed["id"], job["id"])
        self.assertEqual(claimed["status"], "running")

        # Simulate worker crash: job lease expired. Run recovery
        recovered_count = self.job_manager.recover_stale_jobs()
        self.assertEqual(recovered_count, 1)

        # Job is now eligible to be claimed again by restarted worker
        reclaimed = self.job_manager.claim_job(lease_seconds=30)
        self.assertIsNotNone(reclaimed)
        self.assertEqual(reclaimed["id"], job["id"])
        self.assertEqual(reclaimed["attempt_count"], 2)

        # Worker completes job
        self.job_manager.complete_job(job["id"], output_id="out-123")
        completed = self.conn.execute("SELECT status, output_id FROM jobs WHERE id = ?", (job["id"],)).fetchone()
        self.assertEqual(completed["status"], "succeeded")
        self.assertEqual(completed["output_id"], "out-123")

    def test_revised_attachment_retains_previous_version(self):
        """Revised document retains previous version ID in supersedes_id for full audit trail."""
        # Insert initial document version
        doc_v1_id = "doc-infy-results-v1"
        self.repo.store_source_document(
            doc_id=doc_v1_id,
            company_id="comp-infy-001",
            source_type="quarterly_results",
            publisher="NSE",
            source_url="https://nsearchives.nseindia.com/corporate/INFY_Results_v1.pdf",
            content_hash="hash_v1_11111111111111111111111111111111",
            file_size_bytes=100000,
            page_count=10,
            published_at_utc="2026-10-28T10:00:00Z",
            fiscal_period="Q2_FY27",
            local_path="data/docs/INFY_v1.pdf"
        )

        # Insert revised document version
        doc_v2_id = "doc-infy-results-v2"
        self.conn.execute("""
            INSERT INTO source_documents (
                id, company_id, source_type, publisher, source_url, content_hash,
                file_size_bytes, page_count, published_at_utc, fiscal_period,
                local_path, fetched_at_utc, parser_version, status, supersedes_id
            ) VALUES (?, ?, 'quarterly_results', 'NSE', ?, ?, 105000, 10, ?, 'Q2_FY27', ?, ?, '1.0.0', 'verified', ?)
        """, (
            doc_v2_id, "comp-infy-001",
            "https://nsearchives.nseindia.com/corporate/INFY_Results_v2_revised.pdf",
            "hash_v2_22222222222222222222222222222222",
            "2026-10-28T12:00:00Z",
            "data/docs/INFY_v2.pdf",
            "2026-10-28T12:05:00Z",
            doc_v1_id
        ))
        self.conn.commit()

        # Both records exist in database
        v1 = self.conn.execute("SELECT id, supersedes_id FROM source_documents WHERE id = ?", (doc_v1_id,)).fetchone()
        v2 = self.conn.execute("SELECT id, supersedes_id FROM source_documents WHERE id = ?", (doc_v2_id,)).fetchone()
        self.assertIsNotNone(v1)
        self.assertIsNotNone(v2)
        self.assertEqual(v2["supersedes_id"], doc_v1_id, "Revised document must reference superseded document ID")

if __name__ == "__main__":
    unittest.main()
