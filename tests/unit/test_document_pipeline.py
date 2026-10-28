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
from finn.extraction.url_validator import validate_url_ssrf_safe
from finn.extraction.pdf_parser import parse_pdf
from finn.retrieval.indexer import DocumentIndexer, chunk_document_pages
from finn.ingestion.discovery import GenericIRDiscoveryService

class TestDocumentPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test_doc_pipeline.db")
        init_db(self.db_path)
        self.conn = get_connection(self.db_path)
        self.indexer = DocumentIndexer(self.conn)
        self.discovery = GenericIRDiscoveryService()
        self.fixtures_dir = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures" / "source"

    def tearDown(self):
        self.conn.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_ssrf_safe_url_validation(self):
        """Rejects localhost, loopback, private IPs, cloud metadata, and non-HTTP schemes."""
        # Blocked URLs
        self.assertFalse(validate_url_ssrf_safe("http://127.0.0.1:8000/secret.pdf")[0])
        self.assertFalse(validate_url_ssrf_safe("http://localhost/admin")[0])
        self.assertFalse(validate_url_ssrf_safe("http://169.254.169.254/latest/meta-data")[0])
        self.assertFalse(validate_url_ssrf_safe("http://10.0.0.5/report.pdf")[0])
        self.assertFalse(validate_url_ssrf_safe("http://192.168.1.1/ir/doc.pdf")[0])
        self.assertFalse(validate_url_ssrf_safe("file:///etc/passwd")[0])
        self.assertFalse(validate_url_ssrf_safe("ftp://files.example.com/ar.pdf")[0])

        # Allowed public URLs
        is_safe, msg = validate_url_ssrf_safe("https://www.infosys.com/investors/reports-filings/annual-report.pdf")
        self.assertTrue(is_safe, f"Expected public URL to pass: {msg}")

    def test_pdf_parsing_multi_layout_fixtures(self):
        """Parses at least two different PDF layouts: conversational transcript and tabular financial results."""
        # Layout 1: Conversational Transcript
        pdf_path_1 = self.fixtures_dir / "INFY_Q4_FY24_earningscall.pdf"
        res1 = parse_pdf(str(pdf_path_1))
        self.assertEqual(res1.status, "verified")
        self.assertEqual(res1.page_count, 28)
        self.assertIn("guidance", res1.pages[3].text.lower()) # Page 4 (index 3)

        # Layout 2: Tabular Quarterly Financial Results
        pdf_path_2 = self.fixtures_dir / "HCLTECH_Q2_FY27_results_tabular.pdf"
        res2 = parse_pdf(str(pdf_path_2))
        self.assertEqual(res2.status, "verified")
        self.assertEqual(res2.page_count, 1)
        self.assertIn("revenue from operations", res2.pages[0].text.lower())

    def test_corrupt_and_scanned_pdf_handling(self):
        """Invalid files and scanned documents are detected cleanly with explicit limitations."""
        # Corrupt file (missing %PDF- header, e.g. HTML 404 page)
        html_bytes = b"<html><body>404 Not Found</body></html>"
        res_corrupt = parse_pdf(html_bytes)
        self.assertEqual(res_corrupt.status, "corrupt_or_invalid")
        self.assertIn("magic header", res_corrupt.error_message)

    def test_fts5_indexing_and_exact_page_retrieval(self):
        """Chunks document text, populates SQLite FTS5, and retrieves exact page attribution."""
        from finn.db.repository import DataRepository
        repo = DataRepository(self.conn)
        repo.seed_master_data()

        pdf_path = self.fixtures_dir / "INFY_Q4_FY24_earningscall.pdf"
        parse_res = parse_pdf(str(pdf_path))
        doc_id = "doc-infy-fts-test"
        company_id = "comp-infy-001"

        # Store document first to satisfy foreign keys
        repo.store_source_document(
            doc_id=doc_id,
            company_id=company_id,
            source_type="earnings_transcript",
            publisher="Infosys IR",
            source_url="https://www.infosys.com/investors/q4-fy24.pdf",
            content_hash=parse_res.sha256,
            file_size_bytes=parse_res.file_size_bytes,
            page_count=parse_res.page_count,
            published_at_utc="2024-04-18T10:00:00Z",
            fiscal_period="Q4_FY24",
            local_path=str(pdf_path)
        )

        # Index document
        chunk_count = self.indexer.index_document(doc_id, company_id, parse_res.pages)
        self.assertGreater(chunk_count, 0)

        # Search FTS5 for guidance keyword
        results = self.indexer.search_chunks(company_id, "operating margin guidance", limit=5)
        self.assertGreater(len(results), 0)
        
        # Verify citation points to exact 1-based page and contains key term
        hit = results[0]
        self.assertIn("page_start", hit)
        self.assertIn("operating margin", hit["text_content"].lower())

    def test_generic_ir_discovery_from_html(self):
        """Generic discovery classifies annual reports and transcripts and reports missing classes."""
        sample_html = """
        <html>
            <body>
                <a href="/docs/ar-2024.pdf">Annual Report FY24</a>
                <a href="/transcripts/q4-concall.pdf">Earnings Call Transcript Q4 FY24</a>
                <a href="/press/results-q4.pdf">Quarterly Financial Results Press Release</a>
            </body>
        </html>
        """
        res = self.discovery.discover_from_html(
            base_url="https://www.infosys.com/investors/",
            html_content=sample_html,
            company_id="comp-infy-001",
            symbol="INFY"
        )
        self.assertEqual(len(res.discovered), 3)
        self.assertEqual(res.status, "completed")
        self.assertEqual(len(res.missing_classes), 0)

        types = [d.document_type for d in res.discovered]
        self.assertIn("annual_report", types)
        self.assertIn("earnings_transcript", types)
        self.assertIn("quarterly_results", types)

if __name__ == "__main__":
    unittest.main()
