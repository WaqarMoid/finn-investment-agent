# FINN Build Status & Verification Ledger

**Last Updated:** 2026-10-28T09:57:00Z (Asia/Kolkata: 2026-10-28T15:27:00+05:30)  
**Current Milestone:** Completed T07 -> Proceeding to T08  
**Repository State:** Primary document pipeline operational: SSRF-safe URL validation, multi-layout PDF parsing, scanned/corrupt file detection, text chunking with page boundary preservation, SQLite FTS5 full-text indexing, generic IR link discovery, and 46 passing tests.

---

## 1. Work Packet History

| Packet | Description | Status | Completion Date (UTC) | Verification Gate Summary |
|---|---|---|---|---|
| **T00** | Source feasibility and runtime spike | **COMPLETED** | 2026-10-28T09:18:00Z | 3/3 source classes verified with real network calls; 3 fixtures saved; primary PDF downloaded and text extracted; hosting evaluated; gate passed. |
| **T01** | Repo, shell and first deployment | **COMPLETED** | 2026-10-28T09:29:00Z | React/TS frontend (Vite), FastAPI API, lockfiles, `.env.example`, Dockerfile/Compose, unit tests, Playwright 390px mobile navigation shell, deep-link reload passing. |
| **T02** | Database, identity and evidence backbone | **COMPLETED** | 2026-10-28T09:39:00Z | Clean DB migration & rerun; foreign keys enforced; 22 candidate holdings seeded; exact symbol, ISIN, BSE code & alias resolver; immutable document/evidence storage; session-isolated watchlists passing. |
| **T03** | Price adapter and deterministic calculations | **COMPLETED** | 2026-10-28T09:43:00Z | Price adapter interface, live & fixture adapters; volume baseline (prior 20 completed sessions excluding today); price delta; zero/negative/missing data; strictly-greater-than 5% and 2.0x threshold gates; stock split adjustment; live integration smoke check passing. |
| **T04** | Exchange ingestion and reliable jobs | **COMPLETED** | 2026-10-28T09:47:00Z | NSE announcement adapter, attachment download jobs, durable SQLite worker leases, crash recovery, duplicate poll dedup, partial pagination watermark protection, 403/429 visible error state, rate-limited refresh passing. |
| **T05** | Materiality and alerts | **COMPLETED** | 2026-10-28T09:51:00Z | 17-category taxonomy, deterministic ranking tiers (Needs Attention, Worth a Look, Routine), critical safety overrides (insolvency, auditor resignation/qualification, regulatory seizure), results notice below actual results, alert dedup, non-causal price alert language, non-notifying preview passing. |
| **T06** | Complete briefing vertical slice | **COMPLETED** | 2026-10-28T09:54:00Z | End-to-end Briefing screen connected to live API; 24h/7d/custom windows; count reconciliation; live evidence drawer data; alert inbox & session threshold persistence; Playwright mobile E2E workflow passing. |
| **T07** | Primary document discovery and parsing | **COMPLETED** | 2026-10-28T09:57:00Z | SSRF-safe URL validation (RFC 1918, loopback, cloud metadata blocked), multi-layout PDF parsing (conversational transcript & tabular results), scanned/corrupt detection, SQLite FTS5 chunk indexing with exact page attribution, generic IR link discovery passing. |
| **T08** | Structured extraction and financial facts | *NEXT* | Pending | Normalized financial facts, deterministic QoQ/YoY, token tracking. |
| **T09** | Guidance ledger and first research report | *Queued* | Pending | 4-quarter ledger, stated vs reported assessment, dual citations. |
| **T10** | Generalization and bounded questions | *Queued* | Pending | 3-5 prepared cases, held-out evaluation on 3 unseen tickers. |
| **T11** | Replay and resilience | *Queued* | Pending | Historical replay clock, failure injection, session isolation. |

---

## 2. Details of Completed Packet: T07

### Changed / Created Files
- `apps/api/finn/extraction/url_validator.py`: SSRF validator blocking private networks (10/8, 172.16/12, 192.168/16), loopback (127/8, localhost), cloud metadata (169.254/16), IPv6 link-local/unique-local, and non-HTTP schemes.
- `apps/api/finn/extraction/pdf_parser.py`: PDF parser validating magic `%PDF-` header, computing SHA-256 checksums, extracting text per 1-based page, and identifying scanned / low-text documents.
- `apps/api/finn/retrieval/indexer.py`: Text chunker (`chunk_document_pages`) preserving 1-based page bounds and section headers; `DocumentIndexer` inserting pages into `source_pages`, chunks into `document_chunks`, and index into virtual table `chunks_fts`; `search_chunks` executing Porter-stemmed FTS5 search with snippet generation.
- `apps/api/finn/ingestion/discovery.py`: `GenericIRDiscoveryService` parsing HTML links on company domains into classified primary classes (`annual_report`, `earnings_transcript`, `quarterly_results`) with SSRF checks.
- `tests/fixtures/source/HCLTECH_Q2_FY27_results_tabular.pdf`: Second PDF layout fixture representing 1-page tabular financial results with comparative columns.
- `tests/unit/test_document_pipeline.py`: 5 unit tests verifying SSRF protection, multi-layout parsing across both fixtures, corrupt/scanned handling, FTS5 indexing with exact page attribution, and generic HTML IR discovery.

### Checks Actually Run & Results

1. **Document Pipeline Unit Tests (`tests/unit/test_document_pipeline.py`):**
   - Command: `python -m unittest tests/unit/test_document_pipeline.py`
   - Result: 5 tests passed in 1.471s.
     - Verified SSRF validation blocks `127.0.0.1`, `localhost`, `169.254.169.254`, `10.0.0.5`, `192.168.1.1`, `file:///etc/passwd`, and permits public HTTPS.
     - Verified Layout 1 (INFY 28-page transcript) and Layout 2 (HCLTECH 1-page tabular results) parsed cleanly.
     - Verified non-PDF / HTML error pages produce `status: "corrupt_or_invalid"`.
     - Verified document indexing stores chunks and FTS5 search retrieves exact page numbers with Porter stemming.
     - Verified generic HTML IR link discovery categorizes reports and transcripts.
2. **Workspace Full Regression (`discover -s tests`):**
   - Command: `python -m unittest discover -s tests`
   - Result: 46 tests passed in 12.389s.

### Unresolved Issues & Known Gaps
- None. All T07 gate criteria satisfied.

---

## 3. Next Packet: T08 — Structured extraction and financial facts

**Objective:**
Implement the structured model adapter / extraction interface with Pydantic schema validation, financial-fact normalization (units, currency, periods, scopes), deterministic QoQ / YoY percentage and absolute change calculation, EBITDA derivation checks (explicit disclosure vs formula label), token/cost instrumentation, and gold-set test cases.
