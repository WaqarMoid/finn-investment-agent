"""Primary-source research coverage should generalize beyond seed symbols."""

import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "apps" / "api"))

from finn.db.database import get_connection, init_db
from finn.db.resolver import CompanyResolver
from finn.ingestion.nse_research import _allowed_pdf_url, _filing_type, sync_nse_master


class FakeResponse:
    status_code = 200

    def __init__(self, text):
        self.text = text

    def raise_for_status(self):
        pass


class FakeClient:
    def __init__(self, text):
        self.text = text

    def get(self, url):
        return FakeResponse(self.text)


class TestNSEResearch(unittest.TestCase):
    def test_master_resolves_unseeded_companies_and_preserves_isin(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "finn.db")
            init_db(path)
            conn = get_connection(path)
            header = "SYMBOL,NAME OF COMPANY, SERIES, DATE OF LISTING, PAID UP VALUE, MARKET LOT, ISIN NUMBER, FACE VALUE\n"
            rows = [f"TEST{i},Test Company {i},EQ,01-JAN-2020,1,1,INE{i:09d},1\n" for i in range(1001)]
            count = sync_nse_master(conn, FakeClient(header + "".join(rows)))
            self.assertEqual(count, 1001)
            match = CompanyResolver(conn).resolve("TEST1000")
            self.assertEqual(match["status"], "resolved")
            self.assertEqual(match["company"]["isin"], "INE000001000")
            conn.close()

    def test_only_official_pdfs_and_relevant_filing_classes(self):
        self.assertTrue(_allowed_pdf_url("https://nsearchives.nseindia.com/corporate/example.pdf"))
        self.assertFalse(_allowed_pdf_url("https://other.example/corporate/example.pdf"))
        self.assertFalse(_allowed_pdf_url("http://nsearchives.nseindia.com/corporate/example.pdf"))
        self.assertTrue(_allowed_pdf_url("https://investors.coforge.com/report.pdf", ["coforge.com"]))
        self.assertFalse(_allowed_pdf_url("https://coforge.com.attacker.example/report.pdf", ["coforge.com"]))
        self.assertEqual(_filing_type("Analyst Meet", "Earnings Call Transcript"), "earnings_transcript")
        self.assertIsNone(_filing_type("Trading Window", "Closure notice"))
        self.assertIsNone(_filing_type("Copy of Newspaper Publication", "financial results"))


if __name__ == "__main__":
    unittest.main()
