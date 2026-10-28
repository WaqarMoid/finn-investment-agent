import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add apps/api to PYTHONPATH
api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from finn.db.database import get_connection, init_db
from finn.db.repository import DataRepository
from finn.ranking.materiality import MaterialityClassifier
from finn.alerts.engine import AlertEngine

class TestMaterialityAndAlerts(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_alerts.db")
        init_db(self.db_path)
        self.conn = get_connection(self.db_path)
        self.repo = DataRepository(self.conn)
        self.repo.seed_master_data()
        self.classifier = MaterialityClassifier()
        self.engine = AlertEngine(self.conn)
        self.session_id = "session-test-alerts-101"
        self.repo.seed_default_watchlist_for_session(self.session_id)

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_results_notice_ranks_strictly_below_actual_results(self):
        """Meeting notices must score as Routine; actual financial results must score as Needs Attention."""
        notice_res = self.classifier.rank_announcement("Intimation of Board Meeting to consider Financial Results")
        self.assertEqual(notice_res.category, "results")
        self.assertEqual(notice_res.stage, "notice")
        self.assertEqual(notice_res.tier, "routine")
        self.assertLess(notice_res.score, 25.0)

        actual_res = self.classifier.rank_announcement("Outcome of Board Meeting: Unaudited Financial Results for Q2 FY25")
        self.assertEqual(actual_res.category, "results")
        self.assertEqual(actual_res.stage, "completed")
        self.assertEqual(actual_res.tier, "needs_attention")
        self.assertGreaterEqual(actual_res.score, 55.0)
        self.assertGreater(actual_res.score, notice_res.score)

    def test_auditor_distress_never_hidden_by_routine_category(self):
        """Auditor resignation and adverse qualifications must trigger Safety Overrides to Needs Attention."""
        resignation = self.classifier.rank_announcement("Resignation of Statutory Auditor of the Company")
        self.assertTrue(resignation.override_applied)
        self.assertEqual(resignation.tier, "needs_attention")
        self.assertGreaterEqual(resignation.score, 90.0)

        qualification = self.classifier.rank_announcement("Auditor's adverse remark and qualification on standalone results")
        self.assertTrue(qualification.override_applied)
        self.assertEqual(qualification.tier, "needs_attention")

    def test_critical_safety_overrides_surfaced(self):
        """Insolvency, CIRP, and regulatory investigations must be surfaced in Needs Attention."""
        cirp = self.classifier.rank_announcement("Commencement of Corporate Insolvency Resolution Process (CIRP) under NCLT")
        self.assertTrue(cirp.override_applied)
        self.assertEqual(cirp.tier, "needs_attention")

        regulatory = self.classifier.rank_announcement("Order received from SEBI: Search and Seizure proceedings")
        self.assertTrue(regulatory.override_applied)
        self.assertEqual(regulatory.tier, "needs_attention")

    def test_alert_dedup_and_no_spam(self):
        """Re-evaluating the same filing or repeated polls must not generate duplicate alerts."""
        ann = {
            "id": "ann-nse-mock-001",
            "company_id": "comp-infy-001",
            "original_title": "Outcome of Board Meeting: Financial Results for Q2"
        }

        # First evaluation generates alert
        alert1 = self.engine.evaluate_filing(self.session_id, ann)
        self.assertIsNotNone(alert1)
        initial_alerts_count = self.conn.execute("SELECT count(*) FROM alerts WHERE session_id = ?", (self.session_id,)).fetchone()[0]
        self.assertEqual(initial_alerts_count, 1)

        # Duplicate evaluation of identical filing -> returns None and does not spam inbox
        alert2 = self.engine.evaluate_filing(self.session_id, ann)
        self.assertIsNone(alert2)
        final_alerts_count = self.conn.execute("SELECT count(*) FROM alerts WHERE session_id = ?", (self.session_id,)).fetchone()[0]
        self.assertEqual(final_alerts_count, 1)

    def test_price_alert_never_attributes_causation_to_coincident_news(self):
        """Price alert reason must explicitly state that causal link to coincident news is unverified."""
        move = {
            "status": "ok",
            "current_date": "2026-10-28",
            "delta_pct": "6.85"
        }
        res = self.engine.evaluate_price_alert(self.session_id, "comp-infy-001", "INFY", move)
        self.assertIsNotNone(res)
        reason = res["reason"]
        self.assertIn("exceeds 5.0% threshold", reason)
        self.assertIn("causal link to coincident filings unverified", reason)
        self.assertNotIn("caused by", reason.lower())

    def test_non_notifying_preview(self):
        """Previewing rules on recent data must NOT insert any alerts into the database."""
        # Insert test announcement
        self.conn.execute("""
            INSERT INTO announcements (
                id, company_id, exchange, source_id, published_at_utc,
                fetched_at_utc, original_title, category, parse_status
            ) VALUES ('ann-prev-1', 'comp-infy-001', 'NSE', 'src-1', '2026-10-28T10:00:00Z',
                      '2026-10-28T10:05:00Z', 'Outcome of Board Meeting: Financial Results', 'results', 'parsed')
        """)
        self.conn.commit()

        alerts_before = self.conn.execute("SELECT count(*) FROM alerts WHERE session_id = ?", (self.session_id,)).fetchone()[0]
        
        # Run preview
        preview_matches = self.engine.preview_rules(self.session_id, categories=["results"], min_materiality="worth_a_look")
        self.assertGreaterEqual(len(preview_matches), 1)

        alerts_after = self.conn.execute("SELECT count(*) FROM alerts WHERE session_id = ?", (self.session_id,)).fetchone()[0]
        self.assertEqual(alerts_before, alerts_after, "Preview must not create alert records in database")

if __name__ == "__main__":
    unittest.main()
