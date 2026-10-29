import unittest
import sqlite3
import sys
from decimal import Decimal
from pathlib import Path
from fastapi.testclient import TestClient

# Add apps/api to PYTHONPATH
api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from finn.main import app
from finn.db.database import init_db
from finn.db.repository import FinnRepository
from finn.research.guidance_ledger import (
    GuidanceStatementModel,
    assess_guidance_outcome,
    INFY_VERIFIED_LEDGER,
    HCLTECH_VERIFIED_LEDGER,
)
from finn.research.seed_evidence import seed_verified_research_evidence

class TestGuidanceLedger(unittest.TestCase):
    def setUp(self):
        self.client_manager = TestClient(app)
        self.client = self.client_manager.__enter__()

    def tearDown(self):
        self.client_manager.__exit__(None, None, None)

    def test_future_period_is_never_marked_missed(self):
        """Gate: Future full-year target must not be marked missed; assessment must be 'not_due'."""
        guidance = GuidanceStatementModel(
            id="g-1",
            company_id="comp-infy-001",
            metric="revenue_growth",
            speaker_role="CFO",
            stated_at_utc="2025-01-16T10:00:00Z",
            target_period="FY25",
            low_decimal=Decimal("4.5"),
            high_decimal=Decimal("5.0"),
            evidence_id="ev-preview-106"
        )
        # Target period is not completed
        outcome = assess_guidance_outcome(
            guidance=guidance,
            reported_actual=None,
            is_period_completed=False
        )
        self.assertEqual(outcome["assessment"], "not_due")
        self.assertIn("not yet completed", outcome["explanation"])

    def test_qualitative_guidance_does_not_invent_numbers(self):
        """Gate: Qualitative guidance must not invent numbers or fake percentages."""
        guidance = GuidanceStatementModel(
            id="g-qual",
            company_id="comp-infy-001",
            metric="capex_outlook",
            speaker_role="CEO",
            stated_at_utc="2024-04-18T10:00:00Z",
            target_period="FY25",
            qualitative_text="Management expects steady capex focused on cloud and generative AI infrastructure.",
            evidence_id="ev-preview-101"
        )
        outcome = assess_guidance_outcome(
            guidance=guidance,
            reported_actual=None,
            is_period_completed=True
        )
        self.assertEqual(outcome["assessment"], "qualitative_supported")
        self.assertIn("Management expects steady capex", outcome["explanation"])

    def test_deterministic_range_evaluation(self):
        """Verify met, exceeded, and missed verdicts on higher-is-better metrics."""
        guidance = GuidanceStatementModel(
            id="g-rev",
            company_id="comp-infy-001",
            metric="cc_revenue_growth",
            speaker_role="CFO",
            stated_at_utc="2024-04-18T10:00:00Z",
            target_period="Q1_FY25",
            low_decimal=Decimal("1.0"),
            high_decimal=Decimal("3.0"),
            evidence_id="ev-preview-101"
        )
        # Met (within 1.0% to 3.0%)
        res_met = assess_guidance_outcome(guidance, Decimal("2.5"), is_period_completed=True)
        self.assertEqual(res_met["assessment"], "met")

        # Exceeded (above 3.0%)
        res_exceeded = assess_guidance_outcome(guidance, Decimal("3.8"), is_period_completed=True)
        self.assertEqual(res_exceeded["assessment"], "exceeded")

        # Missed (below 1.0%)
        res_missed = assess_guidance_outcome(guidance, Decimal("0.8"), is_period_completed=True)
        self.assertEqual(res_missed["assessment"], "missed")

    def test_withdrawn_guidance_retained(self):
        """Gate: Formally withdrawn guidance is explicitly retained with withdrawn status."""
        guidance = GuidanceStatementModel(
            id="g-withdrawn",
            company_id="comp-infy-001",
            metric="annual_revenue",
            speaker_role="CEO",
            stated_at_utc="2024-04-18T10:00:00Z",
            target_period="FY25",
            low_decimal=Decimal("5.0"),
            high_decimal=Decimal("7.0"),
            evidence_id="ev-preview-101",
            status="withdrawn"
        )
        outcome = assess_guidance_outcome(guidance, Decimal("4.0"), is_period_completed=True)
        self.assertEqual(outcome["assessment"], "withdrawn")

    def test_verified_ledgers_integrity(self):
        """Verify 4-quarter verified ledgers for INFY and HCLTECH."""
        self.assertEqual(len(INFY_VERIFIED_LEDGER), 4)
        self.assertEqual(len(HCLTECH_VERIFIED_LEDGER), 4)

        # INFY checks
        q1 = INFY_VERIFIED_LEDGER[0]
        self.assertEqual(q1.target_period, "Q1 FY25")
        self.assertEqual(q1.assessment, "met")
        self.assertTrue(q1.stated_evidence_id.startswith("ev-"))
        self.assertTrue(q1.reported_evidence_id.startswith("ev-"))

        q4 = INFY_VERIFIED_LEDGER[3]
        self.assertEqual(q4.target_period, "Q4 FY25")
        self.assertEqual(q4.assessment, "not_due")
        self.assertIsNone(q4.reported_evidence_id)

        # HCLTECH checks
        hcl_q3 = HCLTECH_VERIFIED_LEDGER[2]
        self.assertEqual(hcl_q3.assessment, "missed")
        self.assertTrue(hcl_q3.reported_evidence_id.startswith("ev-"))

    def test_research_api_infy(self):
        """Source links are returned without manufacturing page facts or ledger rows."""
        resp = self.client.get("/api/v1/research/INFY")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["company"]["symbol"], "INFY")
        self.assertEqual(data["guidance_ledger"], [])
        self.assertEqual(data["overview_facts"], [])
        self.assertGreaterEqual(len(data["source_coverage"]), 2)
        self.assertTrue(all(item["source_url"].startswith("https://www.infosys.com/") for item in data["source_coverage"]))
        self.assertGreaterEqual(len(data["limitations"]), 1)

    def test_legacy_demo_evidence_is_removed(self):
        """Legacy hand-written demo quotations must not resolve as verified evidence."""
        resp_stated = self.client.get("/api/v1/evidence/ev-preview-101")
        self.assertEqual(resp_stated.status_code, 404)

    def test_bounded_question_api(self):
        """Test POST /api/v1/research/INFY/ask returns grounded citations."""
        resp = self.client.post("/api/v1/research/INFY/ask", json={
            "question": "What changed in guidance?"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("cannot answer", data["answer"].lower())
        self.assertEqual(len(data["evidence_citations"]), 0)
        self.assertTrue(len(data["limitation"]) > 0)

if __name__ == "__main__":
    unittest.main()
