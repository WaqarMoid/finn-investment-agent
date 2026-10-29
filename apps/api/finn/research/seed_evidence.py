"""Seed links to real, first-party investor sources.

Metadata links are useful; hand-written excerpts are not evidence. Page-level
claims are shown only after a document is parsed and verified.
"""

from finn.db.repository import FinnRepository

PRIMARY_SOURCE_CATALOG = [
    ("src-infy-annual-reports", "comp-infy-001", "annual_report_library", "Infosys Investor Relations", "https://www.infosys.com/investors/reports-filings/annual-report/", "FY26"),
    ("src-infy-quarterly-results", "comp-infy-001", "quarterly_results_library", "Infosys Investor Relations", "https://www.infosys.com/investors/reports-filings/quarterly-results/", "FY27"),
    ("src-hcltech-annual-report", "comp-hcltech-003", "annual_report", "HCLTech Investor Relations", "https://www.hcltech.com/hcl-annual-report-2026", "FY26"),
    ("src-hcltech-investor-relations", "comp-hcltech-003", "quarterly_results_library", "HCLTech Investor Relations", "https://www.hcltech.com/investor-relations", "FY27"),
    ("src-tcs-annual-report-fy26", "comp-tcs-002", "annual_report", "TCS Investor Relations", "https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/2025-26/ar/annual-report-2025-2026.pdf", "FY26"),
    ("src-tcs-investor-relations", "comp-tcs-002", "quarterly_results_library", "TCS Investor Relations", "https://www.tcs.com/investor-relations", "FY27"),
    ("src-reliance-annual-report-fy26", "comp-reliance-004", "annual_report", "Reliance Industries Investor Relations", "https://www.ril.com/reports/RIL-Integrated-Annual-Report-2025-26.pdf", "FY26"),
    ("src-reliance-financial-reporting", "comp-reliance-004", "quarterly_results_library", "Reliance Industries Investor Relations", "https://www.ril.com/investors/financial-reporting", "FY27"),
]


def seed_verified_research_evidence(repo: FinnRepository) -> None:
    """Replace the legacy synthetic demo documents with an honest catalog."""
    repo.conn.execute(
        """DELETE FROM source_documents
           WHERE id LIKE 'doc-infy-%' OR id LIKE 'doc-hcl-%'
              OR source_url LIKE 'https://www.nseindia.com/filings/%'"""
    )
    for doc_id, company_id, source_type, publisher, source_url, fiscal_period in PRIMARY_SOURCE_CATALOG:
        repo.store_source_document(
            doc_id=doc_id,
            company_id=company_id,
            source_type=source_type,
            publisher=publisher,
            source_url=source_url,
            content_hash=f"catalog-v2:{doc_id}",
            file_size_bytes=0,
            page_count=0,
            published_at_utc="2026-10-01T00:00:00Z",
            fiscal_period=fiscal_period,
            local_path="",
            parser_version="catalog-v2",
            status="linked_primary_source",
        )
    repo.conn.commit()
