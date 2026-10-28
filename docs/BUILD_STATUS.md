# FINN Build Status & Verification Ledger

**Last Updated:** 2026-10-28T09:18:00Z (Asia/Kolkata: 2026-10-28T14:48:00+05:30)  
**Current Milestone:** Completed T00 -> Proceeding to T01  
**Repository State:** Initialized workspace, fixtures captured, feasibility established, ready for application scaffolding.

---

## 1. Work Packet History

| Packet | Description | Status | Completion Date (UTC) | Verification Gate Summary |
|---|---|---|---|---|
| **T00** | Source feasibility and runtime spike | **COMPLETED** | 2026-10-28T09:18:00Z | 3/3 source classes verified with real network calls; 3 fixtures saved; primary PDF downloaded and text extracted; hosting evaluated; gate passed. |
| **T01** | Repo, shell and first deployment | *NEXT* | Pending | React/TS frontend, FastAPI API, health routes, mobile shell at 390px, preview build. |
| **T02** | Database, identity and evidence backbone | *Queued* | Pending | Migrations, company resolver, 18 candidate holdings, session watchlist, FTS5 schema. |
| **T03** | Price adapter and deterministic calculations | *Queued* | Pending | EOD daily-bar adapter, volume baseline, price move delta, zero/missing handling. |
| **T04** | Exchange ingestion and reliable jobs | *Queued* | Pending | NSE announcement adapter, attachment jobs, deduplication, worker leases. |
| **T05** | Materiality and alerts | *Queued* | Pending | 17-category taxonomy, ranking tiers, safety overrides, session rules, preview. |
| **T06** | Complete briefing vertical slice | *Queued* | Pending | Briefing UI, 24h/7d presets, priority groups, evidence drawer, alert inbox. |
| **T07** | Primary document discovery and parsing | *Queued* | Pending | Generic IR discovery, PDF page extraction, chunking, FTS5 index. |
| **T08** | Structured extraction and financial facts | *Queued* | Pending | Normalized financial facts, deterministic QoQ/YoY, token tracking. |
| **T09** | Guidance ledger and first research report | *Queued* | Pending | 4-quarter ledger, stated vs reported assessment, dual citations. |
| **T10** | Generalization and bounded questions | *Queued* | Pending | 3-5 prepared cases, held-out evaluation on 3 unseen tickers. |
| **T11** | Replay and resilience | *Queued* | Pending | Historical replay clock, failure injection, session isolation. |

---

## 2. Details of Completed Packet: T00

### Changed / Created Files
- `docs/source-feasibility.md`: Full feasibility report covering runtime, all 3 source classes, host platform evaluation, and verified company identity.
- `docs/BUILD_STATUS.md`: Build tracking ledger and status record.
- `data/manifests/primary_pdf_manifest.json`: Verified primary PDF metadata, SHA256 checksum, page count, and extracted verification excerpt.
- `tests/fixtures/source/primary_pdf_manifest.json`: Mirror copy for automated tests.
- `tests/fixtures/source/INFY_Q4_FY24_earningscall.pdf`: Real downloaded 28-page earnings call transcript from Infosys IR (284,498 bytes, SHA256: `ab268076b83ea82b4293f77341399cb633fa38318b32ba364379ca2fcbb571bc`).
- `tests/fixtures/source/nse_announcements_sample.json`: Real response fixture from NSE corporate announcements API (20 records with attachment links).
- `tests/fixtures/source/infy_eod_sample.json`: Real EOD session fixture from Yahoo Finance Chart API for INFY.NS (64 daily sessions, OHLCV).

### Checks Actually Run & Results

1. **Runtime Verification:**
   - Command: `python --version; node --version; npm --version; git --version`
   - Result: Python 3.12.0, Node.js v25.9.0, npm 11.12.1, git 2.45.1.
2. **SQLite FTS5 Support:**
   - Command: Python script creating virtual table `test USING fts5(content)` and running `MATCH 'FINN'`.
   - Result: Passed (SQLite 3.42.0 with active FTS5).
3. **EOD Price Ingestion (Source Class 1):**
   - Command: HTTP GET `https://query1.finance.yahoo.com/v8/finance/chart/INFY.NS?range=3mo&interval=1d` via `httpx`.
   - Result: HTTP 200, 64 daily candles, currency INR, timezone Asia/Kolkata. Saved to `tests/fixtures/source/infy_eod_sample.json`.
4. **Exchange Announcements (Source Class 2):**
   - Command: HTTP GET `https://www.nseindia.com/api/corporate-announcements?index=equities` via `httpx`.
   - Result: HTTP 200, parsed 20 real corporate announcements with symbols, descriptions, timestamps, and direct PDF attachments.
   - Command: HTTP HEAD `https://nsearchives.nseindia.com/corporate/JETFREIGHT_...pdf`.
   - Result: HTTP 200, Content-Type `application/pdf`, 3,172,563 bytes.
   - Alternative Check: HTTP GET `https://api.bseindia.com/...`.
   - Result: HTTP 403 (Cloudflare protection confirmed; documented as limitation/contingency).
5. **Primary IR & Transcript Discovery (Source Class 3):**
   - Command: Crawled Infosys IR (`infosys.com/investors/...`) and HCLTECH IR (`hcltech.com/investors/results-reports`).
   - Result: Discovered 137+ PDF links on Infosys (including annual reports and quarterly transcripts) and 314+ links on HCLTECH (including 44 transcripts).
6. **Primary PDF Download & Parsing:**
   - Command: Downloaded `https://www.infosys.com/investors/reports-filings/quarterly-results/2023-2024/q4/documents/transcripts/earningscall.pdf` (284,498 bytes). Extracted text using `pypdf.PdfReader`.
   - Result: 28 pages extracted. Found exact FY25 guidance excerpt on Page 4: *"revenue growth guidance for FY '25 is 1% to 3% growth in constant currency. Our operating margin guidance for FY '25 is 20% to 22%."*
   - Generated SHA256 checksum: `ab268076b83ea82b4293f77341399cb633fa38318b32ba364379ca2fcbb571bc`.

### Unresolved Issues & Known Gaps
- **BSE API Access:** BSE returned HTTP 403. Ingestion will prioritize NSE as the primary exchange adapter, treating BSE as an unverified/optional secondary source as provided for in `IMPLEMENTATION_PLAN.md`.
- **TCS IR Dynamic Loading:** TCS IR uses client-side rendering for document listings; Infosys and HCL Technologies provide transparent static URLs and are designated as primary demonstration companies for transcripts and annual reports.

---

## 3. Next Packet: T01 — Repo, shell and first deployment

**Objective:**
Set up the React/TypeScript frontend (Vite), FastAPI backend, mobile shell navigation at 390px width with 3 destinations (Briefing, Research, Watchlist), health endpoints (`/api/v1/health`), lockfiles, and container / runner configuration.
