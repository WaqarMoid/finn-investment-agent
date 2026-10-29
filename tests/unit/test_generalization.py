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
from finn.db.database import get_connection
from finn.db.repository import DataRepository
from finn.db.resolver import CompanyResolver
from finn.retrieval.indexer import FTSIndexer
from finn.extraction.pdf_parser import ParsedPage
from finn.ingestion.discovery import GenericIRDiscoveryService

class TestGeneralizationAndHeldOutEvaluation(unittest.TestCase):
    """T10 Generalization Gate:
    Evaluates 3 held-out tickers (COFORGE, DIXON, ASTRAL) representing different sectors:
    - COFORGE: Information Technology
    - DIXON: Consumer Electronics & EMS
    - ASTRAL: Building Materials & Industrial

    Guarantees:
    - No ticker-specific narrative code or hardcoded answers.
    - Generic pipeline resolves identity, discovers filings, indexes chunks, and answers questions.
    - Missing documents/transcripts result in honest 'insufficient_evidence' / empty ledger, never fabricated data.
    """

    def setUp(self):
        self.client_manager = TestClient(app)
        self.client = self.client_manager.__enter__()

    def tearDown(self):
        self.client_manager.__exit__(None, None, None)

    def test_held_out_company_resolution(self):
        """Verify that all 3 held-out tickers resolve cleanly through generic CompanyResolver."""
        conn = get_connection()
        try:
            resolver = CompanyResolver(conn)

            # 1. COFORGE (IT)
            res_coforge = resolver.resolve("COFORGE")
            self.assertEqual(res_coforge["status"], "resolved")
            self.assertEqual(res_coforge["company"]["legal_name"], "Coforge Limited")
            self.assertEqual(res_coforge["company"]["sector"], "Information Technology")

            # 2. DIXON (EMS / Electronics)
            res_dixon = resolver.resolve("DIXON")
            self.assertEqual(res_dixon["status"], "resolved")
            self.assertEqual(res_dixon["company"]["legal_name"], "Dixon Technologies (India) Limited")
            self.assertEqual(res_dixon["company"]["sector"], "Electronics Manufacturing")

            # 3. ASTRAL (Building Materials)
            res_astral = resolver.resolve("ASTRAL")
            self.assertEqual(res_astral["status"], "resolved")
            self.assertEqual(res_astral["company"]["legal_name"], "Astral Limited")
            self.assertEqual(res_astral["company"]["sector"], "Building Products / Pipes")
        finally:
            conn.close()

    def test_held_out_generic_discovery_and_missing_classes(self):
        """Verify generic HTML IR discovery identifies available docs and honestly flags missing classes."""
        discovery_service = GenericIRDiscoveryService()

        # Simulated IR page for Astral Limited containing results PDF but missing concall transcript
        sample_astral_ir_html = """
        <html>
            <body>
                <h1>Astral Limited Investor Relations</h1>
                <a href="/investors/Astral_Q2_FY25_Financial_Results.pdf">Astral Q2 FY25 Financial Results Press Release</a>
                <a href="/investors/Astral_Annual_Report_2023_24.pdf">Integrated Annual Report 2023-24</a>
            </body>
        </html>
        """
        result = discovery_service.discover_from_html(
            base_url="https://astralpipes.com/investor-relations/",
            html_content=sample_astral_ir_html,
            company_id="comp-astral-022",
            symbol="ASTRAL"
        )

        self.assertEqual(result.status, "partial_coverage")
        self.assertEqual(len(result.discovered), 2)
        # Transcript was not on this page -> correctly identified as missing
        self.assertIn("earnings_transcript", result.missing_classes)
        self.assertNotIn("annual_report", result.missing_classes)

    def test_held_out_indexing_and_bounded_answering_coforge(self):
        """Index a real filing excerpt for COFORGE and verify bounded question answering cites exact page."""
        conn = get_connection()
        try:
            repo = DataRepository(conn)
            doc_id = "doc-coforge-q2fy25"
            repo.store_source_document(
                doc_id=doc_id,
                company_id="comp-coforge-020",
                source_type="quarterly_results",
                publisher="NSE Filings",
                source_url="https://www.nseindia.com/filings/COFORGE/q2_fy25_press_release.pdf",
                content_hash="coforge_hash_q2fy25_verified_sha256",
                file_size_bytes=342000,
                page_count=6,
                published_at_utc="2024-10-22T12:00:00Z",
                fiscal_period="Q2_FY25"
            )

            # Index page containing order intake figures
            indexer = FTSIndexer(conn)
            sample_text = "Coforge Reports Strong Q2 FY25 Operating Performance. Order intake for the quarter was $516 million, marking the third consecutive quarter of $500M+ deals. Headcount increased to 32,484."
            pages = [
                ParsedPage(
                    pdf_page_1based=1,
                    text=sample_text,
                    char_count=len(sample_text)
                )
            ]
            indexer.index_document(document_id=doc_id, company_id="comp-coforge-020", pages=pages)
        finally:
            conn.close()

        # Ask question using the generic research API
        resp = self.client.post("/api/v1/research/COFORGE/ask", json={
            "question": "order intake quarter deals"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertIn("516 million", data["answer"])
        self.assertGreaterEqual(len(data["evidence_citations"]), 1)
        self.assertIn("Page 1", data["evidence_citations"][0]["label"])

    def test_held_out_unavailable_data_returns_honest_limitation(self):
        """A verified statement may appear before its outcome; unrelated questions stay unanswered."""
        resp = self.client.get("/api/v1/research/DIXON")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()

        self.assertEqual(data["company"]["symbol"], "DIXON")
        # Issuer transcript supplies a statement, but the FY27 outcome is not assessed.
        self.assertEqual(len(data["guidance_ledger"]), 1)
        self.assertEqual(data["guidance_ledger"][0]["assessment"], "not_due")
        evidence_id = data["guidance_ledger"][0]["stated_evidence_id"]
        evidence = self.client.get(f"/api/v1/evidence/{evidence_id}")
        self.assertEqual(evidence.status_code, 200)
        self.assertEqual(evidence.json()["data"]["pdf_page_1based"], 14)
        self.assertGreaterEqual(len(data["limitations"]), 1)

        # Asking an ungrounded speculative question must return explicit limitation
        resp_q = self.client.post("/api/v1/research/DIXON/ask", json={
            "question": "What is management's 5-year solar module margin outlook?"
        })
        self.assertEqual(resp_q.status_code, 200)
        q_data = resp_q.json()
        self.assertIn("cannot answer", q_data["answer"])
        self.assertEqual(len(q_data["evidence_citations"]), 0)
        self.assertIn("No verified page excerpt", q_data["limitation"])

    def test_freeform_questions_use_real_issuer_excerpts(self):
        for symbol, question, expected, page in [
            ("COFORGE", "What did management say about free cash flow conversion?", "100%", 8),
            ("DIXON", "What revenue target did management give excluding Vivo?", "56,000", 14),
        ]:
            answer = self.client.post(f"/api/v1/research/{symbol}/ask", json={"question": question})
            self.assertEqual(answer.status_code, 200)
            result = answer.json()
            self.assertIn(expected, result["answer"])
            self.assertEqual(len(result["evidence_citations"]), 1)
            evidence_id = result["evidence_citations"][0]["evidence_id"]
            evidence = self.client.get(f"/api/v1/evidence/{evidence_id}")
            self.assertEqual(evidence.status_code, 200)
            self.assertEqual(evidence.json()["data"]["pdf_page_1based"], page)

if __name__ == "__main__":
    unittest.main()
