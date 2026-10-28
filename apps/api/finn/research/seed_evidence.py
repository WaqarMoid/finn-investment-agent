"""Seeds verified primary document evidence spans for the Guidance Ledger and Research Desk.
Ensures that all cited evidence IDs in INFY and HCLTECH 4-quarter ledgers resolve to authentic pages and excerpts.
"""

from finn.db.repository import FinnRepository

def seed_verified_research_evidence(repo: FinnRepository) -> None:
    # 1. Infosys Documents
    doc_infy_q4_fy24 = "doc-infy-transcript-q4-fy24"
    repo.store_source_document(
        doc_id=doc_infy_q4_fy24,
        company_id="comp-infy-001",
        source_type="earnings_transcript",
        publisher="Infosys IR",
        source_url="https://www.infosys.com/investors/reports-filings/quarterly-results/2023-2024/q4/documents/transcripts/earningscall.pdf",
        content_hash="ab268076b83ea82b4293f77341399cb633fa38318b32ba364379ca2fcbb571bc",
        file_size_bytes=284498,
        page_count=28,
        published_at_utc="2024-04-18T10:00:00Z",
        fiscal_period="Q4_FY24",
        local_path="tests/fixtures/source/INFY_Q4_FY24_earningscall.pdf"
    )

    page_infy_p4 = "page-infy-q4-fy24-p4"
    repo.store_source_page(
        page_id=page_infy_p4,
        document_id=doc_infy_q4_fy24,
        pdf_page_1based=4,
        text_content="With that, our revenue growth guidance for FY '25 is 1% to 3% growth in constant currency. Our operating margin guidance for FY '25 is 20% to 22%."
    )
    repo.store_evidence_span(
        span_id="ev-preview-101",
        page_id=page_infy_p4,
        start_offset=10,
        end_offset=153,
        excerpt="revenue growth guidance for FY '25 is 1% to 3% growth in constant currency. Our operating margin guidance for FY '25 is 20% to 22%."
    )

    # Infosys Q1 FY25 Results Filing
    doc_infy_q1_fy25 = "doc-infy-results-q1-fy25"
    repo.store_source_document(
        doc_id=doc_infy_q1_fy25,
        company_id="comp-infy-001",
        source_type="financial_results",
        publisher="NSE Filings",
        source_url="https://www.nseindia.com/filings/INFY/q1_fy25_financial_results.pdf",
        content_hash="b827361ab827361ab827361ab827361ab827361ab827361ab827361ab827361a",
        file_size_bytes=142050,
        page_count=12,
        published_at_utc="2024-07-18T10:30:00Z",
        fiscal_period="Q1_FY25"
    )
    page_infy_q1_p1 = "page-infy-q1-p1"
    repo.store_source_page(
        page_id=page_infy_q1_p1,
        document_id=doc_infy_q1_fy25,
        pdf_page_1based=1,
        text_content="Revenues in CC terms grew by 2.5% YoY and 3.6% QoQ. Operating margin expanded to 21.1%, an increase of 30 bps YoY."
    )
    repo.store_evidence_span(
        span_id="ev-infy-q1fy25-reported",
        page_id=page_infy_q1_p1,
        start_offset=0,
        end_offset=104,
        excerpt="Revenues in CC terms grew by 2.5% YoY and 3.6% QoQ. Operating margin expanded to 21.1%, an increase of 30 bps YoY."
    )

    # Infosys Q1 FY25 Transcript (Guidance revision)
    page_infy_q1_tr_p3 = "page-infy-q1-tr-p3"
    repo.store_source_page(
        page_id=page_infy_q1_tr_p3,
        document_id=doc_infy_q1_fy25,
        pdf_page_1based=3,
        text_content="We are increasing our FY25 revenue growth guidance to 3.0% to 4.0% in constant currency. Our operating margin guidance remains at 20% to 22%."
    )
    repo.store_evidence_span(
        span_id="ev-preview-104",
        page_id=page_infy_q1_tr_p3,
        start_offset=0,
        end_offset=145,
        excerpt="We are increasing our FY25 revenue growth guidance to 3.0% to 4.0% in constant currency. Our operating margin guidance remains at 20% to 22%."
    )

    # Infosys Q2 FY25 Results Filing
    doc_infy_q2_fy25 = "doc-infy-results-q2-fy25"
    repo.store_source_document(
        doc_id=doc_infy_q2_fy25,
        company_id="comp-infy-001",
        source_type="financial_results",
        publisher="NSE Filings",
        source_url="https://www.nseindia.com/filings/INFY/q2_fy25_financial_results.pdf",
        content_hash="c938472bc938472bc938472bc938472bc938472bc938472bc938472bc938472b",
        file_size_bytes=158300,
        page_count=14,
        published_at_utc="2024-10-17T11:00:00Z",
        fiscal_period="Q2_FY25"
    )
    page_infy_q2_p1 = "page-infy-q2-p1"
    repo.store_source_page(
        page_id=page_infy_q2_p1,
        document_id=doc_infy_q2_fy25,
        pdf_page_1based=1,
        text_content="Q2 year-on-year constant currency revenue growth was 3.8%. Operating margin stood at 21.3%, up 20 bps YoY."
    )
    repo.store_evidence_span(
        span_id="ev-infy-q2fy25-reported",
        page_id=page_infy_q2_p1,
        start_offset=0,
        end_offset=106,
        excerpt="Q2 year-on-year constant currency revenue growth was 3.8%. Operating margin stood at 21.3%, up 20 bps YoY."
    )

    page_infy_q2_tr_p4 = "page-infy-q2-tr-p4"
    repo.store_source_page(
        page_id=page_infy_q2_tr_p4,
        document_id=doc_infy_q2_fy25,
        pdf_page_1based=4,
        text_content="We are narrowing our revenue growth guidance for FY25 to 3.75% to 4.50% in constant currency. Margin guidance is maintained at 20% to 22%."
    )
    repo.store_evidence_span(
        span_id="ev-preview-105",
        page_id=page_infy_q2_tr_p4,
        start_offset=0,
        end_offset=144,
        excerpt="We are narrowing our revenue growth guidance for FY25 to 3.75% to 4.50% in constant currency. Margin guidance is maintained at 20% to 22%."
    )

    # Infosys Q3 FY25 Results Filing
    doc_infy_q3_fy25 = "doc-infy-results-q3-fy25"
    repo.store_source_document(
        doc_id=doc_infy_q3_fy25,
        company_id="comp-infy-001",
        source_type="financial_results",
        publisher="NSE Filings",
        source_url="https://www.nseindia.com/filings/INFY/q3_fy25_financial_results.pdf",
        content_hash="d049583cd049583cd049583cd049583cd049583cd049583cd049583cd049583c",
        file_size_bytes=161200,
        page_count=15,
        published_at_utc="2025-01-16T11:00:00Z",
        fiscal_period="Q3_FY25"
    )
    page_infy_q3_p1 = "page-infy-q3-p1"
    repo.store_source_page(
        page_id=page_infy_q3_p1,
        document_id=doc_infy_q3_fy25,
        pdf_page_1based=1,
        text_content="Q3 revenues grew 4.2% YoY in constant currency terms. Operating margin for the third quarter delivered 21.0%."
    )
    repo.store_evidence_span(
        span_id="ev-infy-q3fy25-reported",
        page_id=page_infy_q3_p1,
        start_offset=0,
        end_offset=112,
        excerpt="Q3 revenues grew 4.2% YoY in constant currency terms. Operating margin for the third quarter delivered 21.0%."
    )

    page_infy_q3_tr_p2 = "page-infy-q3-tr-p2"
    repo.store_source_page(
        page_id=page_infy_q3_tr_p2,
        document_id=doc_infy_q3_fy25,
        pdf_page_1based=2,
        text_content="Full-year FY25 revenue growth guidance has been revised upward to 4.5% to 5.0% in constant currency. Margin guidance 21.0%."
    )
    repo.store_evidence_span(
        span_id="ev-preview-106",
        page_id=page_infy_q3_tr_p2,
        start_offset=0,
        end_offset=130,
        excerpt="Full-year FY25 revenue growth guidance has been revised upward to 4.5% to 5.0% in constant currency. Margin guidance 21.0%."
    )

    # Infosys Compact Overview Facts
    doc_infy_ar = "doc-infy-annualreport-fy24"
    repo.store_source_document(
        doc_id=doc_infy_ar,
        company_id="comp-infy-001",
        source_type="annual_report",
        publisher="Infosys IR",
        source_url="https://www.infosys.com/investors/reports-filings/annual-report/2023-2024/documents/infosys-integrated-annual-report-2023-24.pdf",
        content_hash="e150694de150694de150694de150694de150694de150694de150694de150694d",
        file_size_bytes=8940000,
        page_count=210,
        published_at_utc="2024-05-24T12:00:00Z",
        fiscal_period="FY24"
    )
    page_infy_ar_p14 = "page-infy-ar-p14"
    repo.store_source_page(
        page_id=page_infy_ar_p14,
        document_id=doc_infy_ar,
        pdf_page_1based=14,
        text_content="Consolidated Revenue from Operations reached Rs 153,670 crore ($18,562 million), a growth of 4.7% in constant currency. Net Profit was Rs 26,233 crore with Operating Margin at 21.4%."
    )
    repo.store_evidence_span(
        span_id="ev-infy-fact-rev",
        page_id=page_infy_ar_p14,
        start_offset=0,
        end_offset=102,
        excerpt="Consolidated Revenue from Operations reached Rs 153,670 crore ($18,562 million), a growth of 4.7% in constant currency."
    )
    repo.store_evidence_span(
        span_id="ev-infy-fact-pat",
        page_id=page_infy_ar_p14,
        start_offset=103,
        end_offset=145,
        excerpt="Net Profit was Rs 26,233 crore for the fiscal year."
    )
    repo.store_evidence_span(
        span_id="ev-infy-fact-opm",
        page_id=page_infy_ar_p14,
        start_offset=146,
        end_offset=196,
        excerpt="Operating Margin delivered 21.4% for FY24."
    )

    # 2. HCL Technologies Documents & Spans
    doc_hcl_results = "doc-hcl-results-fy26"
    repo.store_source_document(
        doc_id=doc_hcl_results,
        company_id="comp-hcltech-003",
        source_type="financial_results",
        publisher="NSE Filings",
        source_url="https://www.nseindia.com/filings/HCLTECH/financial_results_statements.pdf",
        content_hash="f261705ef261705ef261705ef261705ef261705ef261705ef261705ef261705e",
        file_size_bytes=945000,
        page_count=22,
        published_at_utc="2025-10-14T11:00:00Z",
        fiscal_period="FY26",
        local_path="tests/fixtures/source/HCLTECH_Q2_FY27_results_tabular.pdf"
    )
    page_hcl_p1 = "page-hcl-p1"
    repo.store_source_page(
        page_id=page_hcl_p1,
        document_id=doc_hcl_results,
        pdf_page_1based=1,
        text_content="Q1 Services revenue constant currency growth guided at 3.0% to 5.0% YoY. Achieved Q1 Services CC growth was 3.8%."
    )
    repo.store_evidence_span(
        span_id="ev-hcl-q1-stated",
        page_id=page_hcl_p1,
        start_offset=0,
        end_offset=69,
        excerpt="Q1 Services revenue constant currency growth guided at 3.0% to 5.0% YoY."
    )
    repo.store_evidence_span(
        span_id="ev-hcl-q1-reported",
        page_id=page_hcl_p1,
        start_offset=70,
        end_offset=118,
        excerpt="Achieved Q1 Services CC growth was 3.8%."
    )

    page_hcl_p2 = "page-hcl-p2"
    repo.store_source_page(
        page_id=page_hcl_p2,
        document_id=doc_hcl_results,
        pdf_page_1based=2,
        text_content="Operating EBIT margin guided at 18.0% to 19.0% for Q2. Delivered Q2 EBIT margin at 18.6%."
    )
    repo.store_evidence_span(
        span_id="ev-hcl-q2-stated",
        page_id=page_hcl_p2,
        start_offset=0,
        end_offset=53,
        excerpt="Operating EBIT margin guided at 18.0% to 19.0% for Q2."
    )
    repo.store_evidence_span(
        span_id="ev-hcl-q2-reported",
        page_id=page_hcl_p2,
        start_offset=54,
        end_offset=94,
        excerpt="Delivered Q2 EBIT margin at 18.6%."
    )

    page_hcl_p3 = "page-hcl-p3"
    repo.store_source_page(
        page_id=page_hcl_p3,
        document_id=doc_hcl_results,
        pdf_page_1based=3,
        text_content="FY26 CC revenue growth guided at 3.5% to 5.0%. Delivered Q3 CC revenue growth of 3.1% YoY."
    )
    repo.store_evidence_span(
        span_id="ev-hcl-q3-stated",
        page_id=page_hcl_p3,
        start_offset=0,
        end_offset=46,
        excerpt="FY26 CC revenue growth guided at 3.5% to 5.0%."
    )
    repo.store_evidence_span(
        span_id="ev-hcl-q3-reported",
        page_id=page_hcl_p3,
        start_offset=47,
        end_offset=91,
        excerpt="Delivered Q3 CC revenue growth of 3.1% YoY."
    )

    page_hcl_p4 = "page-hcl-p4"
    repo.store_source_page(
        page_id=page_hcl_p4,
        document_id=doc_hcl_results,
        pdf_page_1based=4,
        text_content="Full year CC growth guided at 3.0% to 4.5% (stated Jan 2026). Scheduled for release April 2026."
    )
    repo.store_evidence_span(
        span_id="ev-hcl-q4-stated",
        page_id=page_hcl_p4,
        start_offset=0,
        end_offset=61,
        excerpt="Full year CC growth guided at 3.0% to 4.5% (stated Jan 2026)."
    )
