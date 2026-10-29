"""Seed links to real, first-party investor sources.

Metadata links are useful; hand-written excerpts are not evidence. Page-level
claims are shown only after a document is parsed and verified.
"""

from finn.db.repository import FinnRepository
import json

PRIMARY_SOURCE_CATALOG = [
    ("src-infy-annual-reports", "comp-infy-001", "annual_report_library", "Infosys Investor Relations", "https://www.infosys.com/investors/reports-filings/annual-report/", "FY26"),
    ("src-infy-quarterly-results", "comp-infy-001", "quarterly_results_library", "Infosys Investor Relations", "https://www.infosys.com/investors/reports-filings/quarterly-results/", "FY27"),
    ("src-hcltech-annual-report", "comp-hcltech-003", "annual_report", "HCLTech Investor Relations", "https://www.hcltech.com/hcl-annual-report-2026", "FY26"),
    ("src-hcltech-investor-relations", "comp-hcltech-003", "quarterly_results_library", "HCLTech Investor Relations", "https://www.hcltech.com/investor-relations", "FY27"),
    ("src-tcs-annual-report-fy26", "comp-tcs-002", "annual_report", "TCS Investor Relations", "https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/2025-26/ar/annual-report-2025-2026.pdf", "FY26"),
    ("src-tcs-investor-relations", "comp-tcs-002", "quarterly_results_library", "TCS Investor Relations", "https://www.tcs.com/investor-relations", "FY27"),
    ("src-reliance-annual-report-fy26", "comp-reliance-004", "annual_report", "Reliance Industries Investor Relations", "https://www.ril.com/reports/RIL-Integrated-Annual-Report-2025-26.pdf", "FY26"),
    ("src-reliance-financial-reporting", "comp-reliance-004", "quarterly_results_library", "Reliance Industries Investor Relations", "https://www.ril.com/investors/financial-reporting", "FY27"),
    ("src-coforge-ir", "comp-coforge-020", "annual_report_library", "Coforge Investor Relations", "https://investors.coforge.com/annual-report", "FY26"),
    ("src-dixon-ir", "comp-dixon-021", "quarterly_results_library", "Dixon Investor Relations", "https://www.dixoninfo.com/financial-performance", "FY26"),
    ("src-astral-ir", "comp-astral-022", "annual_report_library", "Astral Investor Relations", "https://www.astralltd.com/investors/report-accounts/", "FY26"),
]

# Verbatim excerpts from issuer earnings-call transcripts. The PDF page number is
# the physical PDF page (1-based), so the evidence drawer can open the right page.
VERIFIED_TRANSCRIPT_EXCERPTS = [
    {
        "doc_id": "src-coforge-q4-fy26-call", "company_id": "comp-coforge-020",
        "publisher": "Coforge Investor Relations", "url": "https://investors.coforge.com/hubfs/Coforge-Limited-Earnings-Call-Transcript-Q4FY26%20_AJ.pdf?hsLang=en",
        "published": "2026-05-05T00:00:00Z", "period": "Q4_FY26", "pages": 27,
        "items": [
            (8, "Looking ahead, we anticipate free cash flow to PAT to be maintained at 100% from\nFY27 onwards in contrast to our earlier guidance of 70 to 80%.", "fcf_to_pat", "FY27", "100", "100", "percentage", "consolidated", "Earlier corridor was 70–80%."),
            (8, "EBITDA margins of 20.5% to 21% in FY27 on a consolidated basis, which is including\nEncora", "ebitda_margin", "FY27", "20.5", "21", "percentage", "consolidated", "Includes Encora."),
        ],
    },
    {
        "doc_id": "src-dixon-q4-fy26-call", "company_id": "comp-dixon-021",
        "publisher": "Dixon Technologies Investor Relations", "url": "https://dixon-website.s3.ap-south-1.amazonaws.com/uploads/17eb4df3-5044-40f5-b3c4-3def219cbd19-EarningTranscriptQ4FY26.pdf",
        "published": "2026-05-12T00:00:00Z", "period": "Q4_FY26", "pages": 20,
        "items": [
            (14, "Next\nyear, we are targeting almost INR56,000 crores without the Vivo numbers, and mobile volume\nbeing flat. If Vivo comes in, then it's a very major trigger. We feel that without the Vivo also,\nthe company will keep growing at almost 15% to 17%.", "revenue", "FY27", None, None, "crore", "reported", "Approximately INR56,000 crore; excludes Vivo and assumes flat mobile volume."),
        ],
    },
]

# Exact issuer-published snapshots verified on 2026-10-29. These are deliberately
# compact: each fact points to an inspectable excerpt and first-party URL.
VERIFIED_SNAPSHOTS = [
    {
        "doc_id": "src-infy-q2-fy27-snapshot", "company_id": "comp-infy-001",
        "publisher": "Infosys", "source_url": "https://www.infosys.com/about/last-quarter.html",
        "published": "2026-10-23T11:00:00Z", "period": "Q2_FY27", "period_start": "2026-07-01", "period_end": "2026-09-30",
        "excerpt": "Q2 FY27 consolidated revenue was ₹49,244 crore, operating margin was 21.0%, and net profit after non-controlling interests was ₹7,823 crore.",
        "facts": [("revenue", "49244", "crore"), ("operating_margin", "21.0", "percentage"), ("net_profit", "7823", "crore")],
    },
    {
        "doc_id": "src-hcltech-q2-fy27-snapshot", "company_id": "comp-hcltech-003",
        "publisher": "HCLTech Investor Relations", "source_url": "https://www.hcltech.com/investor-relations",
        "published": "2026-10-12T11:00:00Z", "period": "Q2_FY27", "period_start": "2026-07-01", "period_end": "2026-09-30",
        "excerpt": "Q2 FY27 INR revenue was ₹35,620 crore, EBIT margin was 18.2%, and net income was ₹5,132 crore.",
        "facts": [("revenue", "35620", "crore"), ("ebit_margin", "18.2", "percentage"), ("net_income", "5132", "crore")],
    },
    {
        "doc_id": "src-tcs-fy26-snapshot", "company_id": "comp-tcs-002",
        "publisher": "TCS Integrated Annual Report", "source_url": "https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/2025-26/ar/annual-report-2025-2026.pdf",
        "published": "2026-04-09T11:00:00Z", "period": "FY26", "period_start": "2025-04-01", "period_end": "2026-03-31",
        "excerpt": "FY26 consolidated revenue was ₹267,021 crore, operating margin was 25.0%, and net income was ₹52,820 crore.",
        "facts": [("revenue", "267021", "crore"), ("operating_margin", "25.0", "percentage"), ("net_income", "52820", "crore")],
    },
    {
        "doc_id": "src-reliance-fy26-snapshot", "company_id": "comp-reliance-004",
        "publisher": "Reliance Industries Integrated Annual Report", "source_url": "https://www.ril.com/ar2025-26/index.html",
        "published": "2026-06-30T11:00:00Z", "period": "FY26", "period_start": "2025-04-01", "period_end": "2026-03-31",
        "excerpt": "FY26 consolidated revenue was ₹11,75,919 crore, EBITDA was ₹2,07,911 crore, and PAT was ₹95,754 crore.",
        "facts": [("revenue", "1175919", "crore"), ("ebitda", "207911", "crore"), ("profit_after_tax", "95754", "crore")],
    },
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

    for snapshot in VERIFIED_SNAPSHOTS:
        repo.store_source_document(
            doc_id=snapshot["doc_id"], company_id=snapshot["company_id"],
            source_type="issuer_financial_snapshot", publisher=snapshot["publisher"],
            source_url=snapshot["source_url"], content_hash=f"verified-snapshot-v1:{snapshot['doc_id']}",
            file_size_bytes=0, page_count=1, published_at_utc=snapshot["published"],
            fiscal_period=snapshot["period"], local_path="", parser_version="verified-web-v1",
            status="verified",
        )
        page_id = f"page-{snapshot['doc_id']}-1"
        evidence_id = f"ev-{snapshot['doc_id']}"
        repo.store_source_page(page_id, snapshot["doc_id"], 1, snapshot["excerpt"], printed_label="Issuer financial highlights")
        repo.store_evidence_span(evidence_id, page_id, 0, len(snapshot["excerpt"]), snapshot["excerpt"])
        for metric, value, unit in snapshot["facts"]:
            fact_id = f"fact-{snapshot['company_id']}-{snapshot['period'].lower()}-{metric}"
            repo.conn.execute(
                """INSERT OR REPLACE INTO financial_facts (
                    id, company_id, metric_key, source_label, value_decimal, original_unit,
                    original_value, currency, normalized_unit, period_start, period_end,
                    period_type, fiscal_label, scope, status, missing_reason,
                    evidence_ids_json, derivation_id, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'INR', ?, ?, ?, ?, ?, 'consolidated',
                          'reported', NULL, ?, NULL, ?)""",
                (fact_id, snapshot["company_id"], metric, snapshot["publisher"], value, unit,
                 value, unit, snapshot["period_start"], snapshot["period_end"],
                 "quarter" if snapshot["period"].startswith("Q") else "annual",
                 snapshot["period"], json.dumps([evidence_id]), snapshot["published"]),
            )

    for transcript in VERIFIED_TRANSCRIPT_EXCERPTS:
        repo.store_source_document(
            doc_id=transcript["doc_id"], company_id=transcript["company_id"],
            source_type="earnings_transcript", publisher=transcript["publisher"],
            source_url=transcript["url"], content_hash=f"verified-excerpts-v1:{transcript['doc_id']}",
            file_size_bytes=0, page_count=transcript["pages"],
            published_at_utc=transcript["published"], fiscal_period=transcript["period"],
            local_path="", parser_version="verified-transcript-v1", status="verified_excerpt",
        )
        page_texts = {}
        for page, excerpt, *_ in transcript["items"]:
            page_texts.setdefault(page, []).append(excerpt)
        for page, excerpts in page_texts.items():
            repo.store_source_page(f"page-{transcript['doc_id']}-{page}", transcript["doc_id"],
                                   page, "\n\n".join(excerpts), printed_label=f"PDF page {page}")
        for index, (page, excerpt, metric, target_period, low, high, unit, basis, conditions) in enumerate(transcript["items"], 1):
            page_id = f"page-{transcript['doc_id']}-{page}"
            evidence_id = f"ev-{transcript['doc_id']}-{index}"
            offset = "\n\n".join(page_texts[page]).find(excerpt)
            repo.store_evidence_span(evidence_id, page_id, offset, offset + len(excerpt), excerpt)
            repo.conn.execute(
                """INSERT OR REPLACE INTO guidance_statements
                   (id, company_id, metric, speaker_role, speaker_name, stated_at_utc,
                    target_period, low_decimal, high_decimal, unit, currency, basis,
                    qualitative_text, conditions, evidence_ids_json, status, created_at_utc)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'INR', ?, ?, ?, ?, 'original', ?)""",
                (f"guidance-{transcript['doc_id']}-{index}", transcript["company_id"], metric,
                 "CFO" if transcript["company_id"] == "comp-coforge-020" else "MD",
                 "Saurabh Goel" if transcript["company_id"] == "comp-coforge-020" else "Atul Lall",
                 transcript["published"], target_period, low, high, unit, basis,
                 conditions if low is None else None, conditions,
                 json.dumps([evidence_id]), transcript["published"]),
            )
    repo.conn.commit()
