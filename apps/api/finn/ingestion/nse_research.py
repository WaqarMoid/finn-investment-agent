"""On-demand NSE issuer discovery and page-indexed primary-source ingestion.

The exchange is the source of company identity and filings. No financial value or
management statement is generated from a symbol or announcement headline.
"""

import csv
import io
import os
import re
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import httpx

from finn.db.repository import FinnRepository
from finn.extraction.pdf_parser import parse_pdf
from finn.retrieval.indexer import DocumentIndexer


MASTER_URL = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
NSE_HOME = "https://www.nseindia.com/companies-listing/corporate-filings-announcements"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": NSE_HOME,
}
MAX_PDF_BYTES = 20 * 1024 * 1024


def sync_nse_master(conn, client=None):
    """Import the official EQ-series symbol master, preserving existing ISIN IDs."""
    owns_client = client is None
    client = client or httpx.Client(timeout=15, headers=HEADERS)
    try:
        response = client.get(MASTER_URL)
        response.raise_for_status()
        rows = list(csv.DictReader(io.StringIO(response.text)))
        if len(rows) < 1000:
            raise ValueError("NSE securities master was incomplete")
        now = datetime.now(timezone.utc).isoformat()
        count = 0
        for raw in rows:
            row = {key.strip(): (value or "").strip() for key, value in raw.items()}
            symbol, isin = row.get("SYMBOL", ""), row.get("ISIN NUMBER", "")
            if row.get("SERIES") != "EQ" or not re.fullmatch(r"[A-Z0-9&-]{1,30}", symbol) or not re.fullmatch(r"IN[A-Z0-9]{10}", isin):
                continue
            existing = conn.execute("SELECT id FROM companies WHERE isin = ?", (isin,)).fetchone()
            company_id = existing["id"] if existing else f"comp-nse-{isin}"
            conn.execute(
                """INSERT OR IGNORE INTO companies
                   (id, legal_name, isin, sector, fiscal_calendar, verified_ir_domains, identity_verified_at)
                   VALUES (?, ?, ?, NULL, 'APR_MAR', '[]', ?)""",
                (company_id, row.get("NAME OF COMPANY") or symbol, isin, now),
            )
            conn.execute(
                """INSERT OR IGNORE INTO securities
                   (id, company_id, exchange, symbol, series, price_provider_symbol, valid_from)
                   VALUES (?, ?, 'NSE', ?, 'EQ', ?, ?)""",
                (f"sec-nse-{symbol}", company_id, symbol, f"{symbol}.NS", "1990-01-01"),
            )
            count += 1
        conn.commit()
        return count
    finally:
        if owns_client:
            client.close()


def _filing_type(subject, text):
    combined = f"{subject} {text}".lower()
    if "transcript" in combined or "concall transcript" in combined:
        return "earnings_transcript"
    if "financial result" in combined or "quarterly result" in combined:
        return "quarterly_results"
    if "investor presentation" in combined or "earnings presentation" in combined:
        return "investor_presentation"
    return None


def _allowed_pdf_url(url):
    parsed = urlparse(url)
    return (parsed.scheme == "https" and parsed.hostname in {
        "nsearchives.nseindia.com", "archives.nseindia.com",
    } and parsed.path.lower().endswith(".pdf"))


def _download_pdf(client, url):
    if not _allowed_pdf_url(url):
        raise ValueError("Filing URL is outside official NSE archives")
    with client.stream("GET", url, follow_redirects=False, timeout=30) as response:
        response.raise_for_status()
        if response.headers.get("content-length") and int(response.headers["content-length"]) > MAX_PDF_BYTES:
            raise ValueError("Filing exceeds the 20 MB ingestion limit")
        parts, size = [], 0
        for part in response.iter_bytes():
            size += len(part)
            if size > MAX_PDF_BYTES:
                raise ValueError("Filing exceeds the 20 MB ingestion limit")
            parts.append(part)
    return b"".join(parts)


def refresh_company_sources(conn, company, client=None, max_documents=4):
    """Fetch recent official filings; return honest counts and upstream errors."""
    owns_client = client is None
    client = client or httpx.Client(headers=HEADERS, timeout=18)
    symbol = company["symbol"].upper().replace(".NS", "")
    company_id = company["id"]
    result = {"symbol": symbol, "discovered": 0, "indexed": 0, "pages": 0, "errors": []}
    try:
        # NSE currently requires a first-party page visit before its JSON APIs.
        client.get(NSE_HOME).raise_for_status()
        end = datetime.now(timezone.utc).date()
        start = end - timedelta(days=180)
        params = {"index": "equities", "symbol": symbol,
                  "from_date": start.strftime("%d-%m-%Y"), "to_date": end.strftime("%d-%m-%Y")}
        announcements = client.get("https://www.nseindia.com/api/corporate-announcements", params=params)
        announcements.raise_for_status()
        annual = client.get("https://www.nseindia.com/api/annual-reports", params={"index": "equities", "symbol": symbol})
        annual.raise_for_status()
        candidates = []
        annual_candidate = None
        for row in annual.json().get("data", [])[:1]:
            url = row.get("fileName", "")
            if _allowed_pdf_url(url):
                annual_candidate = ("annual_report", url, row.get("broadcast_dttm") or end.isoformat(),
                                    f"FY{row.get('toYr', '')}")
        seen_types = set()
        for row in announcements.json():
            # NSE retains historical ISINs after splits and other capital actions.
            # Its own symbol-filtered announcement feed is authoritative here.
            if row.get("symbol") != symbol:
                continue
            source_type = _filing_type(row.get("desc", ""), row.get("attchmntText", ""))
            url = row.get("attchmntFile", "")
            if source_type and source_type not in seen_types and _allowed_pdf_url(url):
                candidates.append((source_type, url, row.get("sort_date") or end.isoformat(), None))
                seen_types.add(source_type)
        if annual_candidate:
            candidates.append(annual_candidate)
        priority = {"earnings_transcript": 0, "quarterly_results": 1,
                    "annual_report": 2, "investor_presentation": 3}
        candidates.sort(key=lambda item: priority.get(item[0], 9))
        result["discovered"] = len(candidates)
        repo = FinnRepository(conn)
        for source_type, url, published, fiscal_period in candidates[:max_documents]:
            if conn.execute("SELECT 1 FROM source_documents WHERE company_id = ? AND source_url = ? AND page_count > 0", (company_id, url)).fetchone():
                continue
            try:
                parsed = parse_pdf(_download_pdf(client, url))
                if parsed.status != "verified":
                    raise ValueError(parsed.error_message or parsed.status)
                doc_id = f"nse-{parsed.sha256[:24]}"
                repo.store_source_document(doc_id, company_id, source_type, "NSE issuer filing", url,
                                           parsed.sha256, parsed.file_size_bytes, parsed.page_count,
                                           str(published), fiscal_period, local_path=url)
                DocumentIndexer(conn).index_document(doc_id, company_id, parsed.pages)
                result["indexed"] += 1
                result["pages"] += parsed.page_count
            except (httpx.HTTPError, ValueError) as exc:
                result["errors"].append(f"{source_type}: {str(exc)[:180]}")
        return result
    except (httpx.HTTPError, ValueError, TypeError) as exc:
        result["errors"].append(f"NSE retrieval: {str(exc)[:180]}")
        return result
    finally:
        if owns_client:
            client.close()
