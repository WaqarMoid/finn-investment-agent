import os
import sys
import unittest
import sqlite3
import tempfile
import shutil
from pathlib import Path

# Add apps/api to PYTHONPATH
api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from finn.db.database import get_connection, init_db
from finn.db.seed_data import CANDIDATE_COMPANIES
from finn.db.repository import DataRepository
from finn.db.resolver import CompanyResolver

class TestDatabaseAndResolver(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_finn.db")
        # Run migration on clean DB
        init_db(self.db_path)
        self.conn = get_connection(self.db_path)
        self.repo = DataRepository(self.conn)
        self.repo.seed_master_data()
        self.resolver = CompanyResolver(self.conn)

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_migration_idempotency(self):
        """Migration can rerun cleanly on existing database without error."""
        init_db(self.db_path)
        tables = [r[0] for r in self.conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()]
        self.assertIn("companies", tables)
        self.assertIn("securities", tables)
        self.assertIn("source_documents", tables)
        self.assertIn("evidence_spans", tables)
        self.assertIn("watchlist_members", tables)

    def test_foreign_key_enforcement(self):
        """Foreign keys must prevent orphaned securities or invalid references."""
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("""
                INSERT INTO securities (id, company_id, exchange, symbol, series, price_provider_symbol, valid_from)
                VALUES ('sec-orphan', 'comp-does-not-exist', 'NSE', 'NONEXIST', 'EQ', 'NONEXIST.NS', '2024-01-01')
            """)

    def test_candidate_holdings_seeded(self):
        """Master database contains at least 18 candidate companies."""
        count = self.conn.execute("SELECT count(*) FROM companies").fetchone()[0]
        self.assertGreaterEqual(count, 18)

    def test_resolver_exact_symbol_and_suffixes(self):
        """Resolves exact symbols and handles .NS / .BO suffixes cleanly."""
        res1 = self.resolver.resolve("INFY")
        self.assertEqual(res1["status"], "resolved")
        self.assertEqual(res1["company"]["isin"], "INE009A01021")

        # Test case insensitivity and exchange suffix stripping
        res2 = self.resolver.resolve("infy.ns")
        self.assertEqual(res2["status"], "resolved")
        self.assertEqual(res2["company"]["isin"], "INE009A01021")

        res3 = self.resolver.resolve("TCS.BO")
        self.assertEqual(res3["status"], "resolved")
        self.assertEqual(res3["company"]["isin"], "INE467B01029")

    def test_resolver_bse_code_and_isin(self):
        """Resolves BSE scrip code and ISIN directly."""
        res_bse = self.resolver.resolve("500209")
        self.assertEqual(res_bse["status"], "resolved")
        self.assertEqual(res_bse["company"]["legal_name"], "Infosys Limited")

        res_isin = self.resolver.resolve("INE009A01021")
        self.assertEqual(res_isin["status"], "resolved")
        self.assertEqual(res_isin["company"]["legal_name"], "Infosys Limited")

    def test_resolver_aliases(self):
        """Resolves common aliases without hardcoding company narrative code."""
        res = self.resolver.resolve("HCL Tech")
        self.assertEqual(res["status"], "resolved")
        self.assertEqual(res["company"]["isin"], "INE860A01027")

    def test_resolver_unknown_and_ambiguous(self):
        """Handles unknown and ambiguous company queries safely."""
        unknown = self.resolver.resolve("XYZ_NON_EXISTENT_COMPANY")
        self.assertEqual(unknown["status"], "unknown")

        ambiguous = self.resolver.resolve("Limited")
        self.assertEqual(ambiguous["status"], "ambiguous")
        self.assertGreater(len(ambiguous["candidates"]), 1)

    def test_evidence_backbone_and_provenance(self):
        """Stores document, page, and evidence span; retrieves accurate source attribution."""
        doc_id = "doc-test-transcript-001"
        self.repo.store_source_document(
            doc_id=doc_id,
            company_id="comp-infy-001",
            source_type="earnings_transcript",
            publisher="Infosys IR",
            source_url="https://www.infosys.com/investors/reports-filings/q4-fy24.pdf",
            content_hash="ab268076b83ea82b4293f77341399cb633fa38318b32ba364379ca2fcbb571bc",
            file_size_bytes=284498,
            page_count=28,
            published_at_utc="2024-04-18T10:00:00Z",
            fiscal_period="Q4_FY24",
            local_path="tests/fixtures/source/INFY_Q4_FY24_earningscall.pdf"
        )

        page_id = "page-test-004"
        self.repo.store_source_page(
            page_id=page_id,
            document_id=doc_id,
            pdf_page_1based=4,
            text_content="With that, our revenue growth guidance for FY '25 is 1% to 3% in CC."
        )

        span_id = "ev-guidance-fy25-q4"
        self.repo.store_evidence_span(
            span_id=span_id,
            page_id=page_id,
            start_offset=10,
            end_offset=74,
            excerpt="revenue growth guidance for FY '25 is 1% to 3% in CC."
        )

        # Lookup evidence
        item = self.repo.get_evidence_by_id(span_id)
        self.assertIsNotNone(item)
        self.assertEqual(item["pdf_page_1based"], 4)
        self.assertEqual(item["excerpt"], "revenue growth guidance for FY '25 is 1% to 3% in CC.")
        self.assertEqual(item["company"]["legal_name"], "Infosys Limited")
        self.assertEqual(item["document"]["source_type"], "earnings_transcript")

    def test_session_watchlist_isolation(self):
        """Two separate browser sessions must have completely isolated watchlists."""
        session_a = "session-reviewer-alpha"
        session_b = "session-reviewer-beta"

        # Seed defaults for Session A
        self.repo.seed_default_watchlist_for_session(session_a)
        items_a = self.repo.get_session_watchlist(session_a)
        self.assertEqual(len(items_a), 18)

        # Session B starts empty
        items_b_initial = self.repo.get_session_watchlist(session_b)
        self.assertEqual(len(items_b_initial), 0)

        # Session B adds only HCLTECH
        self.repo.add_to_watchlist(session_b, "comp-hcltech-003")
        items_b = self.repo.get_session_watchlist(session_b)
        self.assertEqual(len(items_b), 1)
        self.assertEqual(items_b[0]["symbol"], "HCLTECH")

        # Session A removes INFY
        self.repo.remove_from_watchlist(session_a, "comp-infy-001")
        items_a_after = self.repo.get_session_watchlist(session_a)
        self.assertEqual(len(items_a_after), 17)

        # Session B still has exactly 1 item
        items_b_after = self.repo.get_session_watchlist(session_b)
        self.assertEqual(len(items_b_after), 1)

if __name__ == "__main__":
    unittest.main()
