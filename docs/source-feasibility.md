# Source Feasibility and Runtime Spike Report (T00)

**Date & Time:** 2026-10-28T09:17:00Z (Asia/Kolkata: 2026-10-28T14:47:00+05:30)  
**Execution Phase:** Packet T00 — Source feasibility and runtime spike  
**Status:** PASSED (All 3 source classes verified with working live paths and fixtures)

---

## 1. Runtime Environment & Pinned Dependencies

| Component | Tested Version | Status / Notes |
|---|---|---|
| **Python** | 3.12.0 | Active runtime verified |
| **Node.js** | v25.9.0 | Active runtime verified |
| **npm** | 11.12.1 | Active package manager |
| **SQLite** | 3.42.0 (with FTS5) | FTS5 virtual table support compiled & tested |
| **FastAPI** | 0.115.12 | Available in runtime |
| **Pydantic** | 2.11.4 | Available in runtime |
| **HTTPX** | 0.28.1 | Available in runtime; async HTTP client |
| **pypdf** | 5.5.0 | Available in runtime; PDF parser & text extraction |
| **pdfplumber** | 0.11.9 | Available in runtime; table/layout extraction |
| **PyMuPDF (fitz)** | 1.28.2 | Available in runtime |
| **Playwright** | 1.62.0 | Available in runtime |
| **Git** | 2.45.1.windows.1 | Available |

---

## 2. Source Classes: Feasibility Matrix & Test Results

Each data source has been directly exercised and classified as **TESTED (working)**, **BLOCKED**, or **UNVERIFIED**.

| Source Class | Provider / Endpoint | Result / Status | Timestamp (UTC) | Findings / Notes |
|---|---|---|---|---|
| **Class 1: Price / EOD** | Yahoo Finance Chart API (`/v8/finance/chart/INFY.NS?range=3mo&interval=1d`) | **TESTED (PASSED)** | 2026-10-28T09:14:50Z | Returned HTTP 200 with 64 daily completed trading sessions, OHLCV, currency `INR`, timezone `Asia/Kolkata`. Fixture saved to `tests/fixtures/source/infy_eod_sample.json`. Zero external library required (pure HTTPX / requests). |
| **Class 2: Exchange Metadata** | NSE India Corporate Announcements (`/api/corporate-announcements?index=equities`) | **TESTED (PASSED)** | 2026-10-28T09:15:05Z | Returned HTTP 200 with 20 real corporate announcements. Rich schema includes `symbol`, `sm_name`, `sm_isin`, `desc`, `attchmntText`, `an_dt`, and direct PDF link on `nsearchives.nseindia.com`. Fixture saved to `tests/fixtures/source/nse_announcements_sample.json`. |
| **Class 2: Exchange Attachments** | NSE Archives (`nsearchives.nseindia.com/corporate/...pdf`) | **TESTED (PASSED)** | 2026-10-28T09:15:21Z | HEAD request returned HTTP 200, Content-Type `application/pdf`, valid attachment stream verified. |
| **Class 2: Exchange Metadata (Alternative)** | BSE India Announcements API (`api.bseindia.com/...`) | **BLOCKED** | 2026-10-28T09:15:05Z | Returned HTTP 403 (Cloudflare bot protection blocks automated fetch without browser emulation). Retained as contingency / documented limitation per planning spec. |
| **Class 3: Primary Documents (IR)** | Infosys Investor Relations (`infosys.com/investors/...`) | **TESTED (PASSED)** | 2026-10-28T09:15:52Z | Annual report & quarterly earnings pages returned HTTP 200. Over 137 PDF documents discovered, including annual reports (`infosys-ar-24.pdf`), quarterly press releases, and earnings call transcripts. |
| **Class 3: Primary Documents (Transcripts)** | Infosys Q4 FY24 Earnings Call Transcript (`.../transcripts/earningscall.pdf`) | **TESTED (PASSED)** | 2026-10-28T09:16:12Z | Successfully downloaded 284,498-byte PDF, extracted text across all 28 pages using `pypdf`. Located exact FY25 guidance on Page 4 (revenue 1% to 3% constant currency, operating margin 20% to 22%). Fixture and manifest saved. |
| **Class 3: Primary Documents (Candidate 2)** | HCL Technologies IR (`hcltech.com/investors/results-reports`) | **TESTED (PASSED)** | 2026-10-28T09:16:28Z | Returned HTTP 200; 314 PDF links and 44 earnings call transcripts directly discovered with transparent URLs. |
| **Class 3: Primary Documents (Candidate 3)** | TCS IR (`tcs.com/investor-relations/financial-statements`) | **UNVERIFIED (Partial)** | 2026-10-28T09:16:20Z | HTTP 200 on parent IR page, but financial statement links load dynamically via client-side script; requires browser automation or direct asset lookup. Infosys and HCLTECH are preferred primary demo candidates. |

---

## 3. Verified Company Identity

Primary Demo Company: **Infosys Limited**
- **Company Name:** Infosys Limited
- **NSE Symbol:** `INFY`
- **BSE Scrip Code:** `500209`
- **ISIN:** `INE009A01021`
- **Industry / Sector:** Information Technology / Software & Services
- **Fiscal Calendar:** April 1 to March 31 (Q1: Jun 30, Q2: Sep 30, Q3: Dec 31, Q4: Mar 31)
- **Primary IR Base URL:** `https://www.infosys.com/investors/`
- **Official Reports Base URL:** `https://www.infosys.com/investors/reports-filings/`
- **Candidate Secondary Verification Company:** HCL Technologies Limited (`HCLTECH`, ISIN: `INE860A01027`, BSE: `532281`).

---

## 4. Primary Document Manifest & Checksum Verification

The primary PDF fixture was downloaded and verified:

```json
{
  "manifest_version": "1.0.0",
  "created_at_utc": "2026-10-28T09:16:00Z",
  "company": {
    "name": "Infosys Limited",
    "symbol_nse": "INFY",
    "isin": "INE009A01021",
    "bse_scrip": "500209"
  },
  "documents": [
    {
      "document_id": "doc_infy_q4_fy24_transcript",
      "title": "Infosys Limited Earnings Conference Call Transcript Q4 FY24",
      "document_type": "transcript",
      "fiscal_period": "Q4_FY24",
      "fiscal_year": "FY2024",
      "source_url": "https://www.infosys.com/investors/reports-filings/quarterly-results/2023-2024/q4/documents/transcripts/earningscall.pdf",
      "local_path": "tests/fixtures/source/INFY_Q4_FY24_earningscall.pdf",
      "sha256": "ab268076b83ea82b4293f77341399cb633fa38318b32ba364379ca2fcbb571bc",
      "file_size_bytes": 284498,
      "page_count": 28,
      "event_date": "2024-04-18",
      "extracted_verification": {
        "key_speakers": ["Salil Parekh (CEO)", "Jayesh Sanghrajka (CFO)"],
        "guidance_excerpt_page": 4,
        "guidance_excerpt": "revenue growth guidance for FY 25 is 1% to 3% growth in constant currency. Our operating margin guidance for FY 25 is 20% to 22%."
      }
    }
  ]
}
```

Stored files:
- Manifest: `data/manifests/primary_pdf_manifest.json` and `tests/fixtures/source/primary_pdf_manifest.json`
- Downloaded PDF: `tests/fixtures/source/INFY_Q4_FY24_earningscall.pdf` (284,498 bytes)
- EOD Fixture: `tests/fixtures/source/infy_eod_sample.json` (64 completed sessions)
- Exchange Fixture: `tests/fixtures/source/nse_announcements_sample.json` (20 live announcements)

---

## 5. Deployment & Hosting Feasibility Analysis

Requirements from `IMPLEMENTATION_PLAN.md` Section 4:
1. **Background Worker:** Needs support for long-running or periodic background polling / ingestion worker.
2. **Persistent Volume:** SQLite database file (`finn.db` with WAL mode and FTS5) and downloaded PDF repository require durable persistence across restarts.
3. **HTTPS:** Secure SSL/TLS termination for mobile browser access.

### Host Platform Evaluations

| Platform | Background Worker | Persistent Volume | HTTPS Support | Free / Hobby Tier Viability | Risk & Mitigation |
|---|---|---|---|---|---|
| **Render** | Supported (Background Worker service or combined process in Web Service) | Supported ($7/mo disk add-on); free tier disk is ephemeral | Native automatic Let's Encrypt | Free tier web services spin down after 15 min and wipe ephemeral disks | Use single web container running worker thread; configure SQLite to persist to mounted disk or keep replay snapshot seeded on startup. |
| **Railway** | Supported (Service worker or background task) | Supported (`/data` volume mount) | Native automatic SSL | Trial credit / usage-based | Excellent fit for unified container (FastAPI + Vite static + volume). |
| **Fly.io** | Supported (Fly Machines / multiple processes) | Supported (`fly volumes create`) | Native automatic SSL | Low-cost hobby tier | First-class SQLite support with persistent volume mount. |
| **Local Docker / Docker Compose / VPS** | Supported (multi-process or systemd) | Supported (host directory mount `./data:/data`) | Caddy / Nginx reverse proxy | Zero third-party hosting cost; 100% reproducible | **Baseline reproduction guarantee.** The repository will include a clean `Dockerfile` and `compose.yaml` so any evaluator can launch the full stack with one command. |

**Architectural Decision:**
The application will be packaged as a single unified deployable container:
- The React / Vite frontend compiles to static assets served by FastAPI at root `/`.
- All API routes are isolated under `/api/v1/*`.
- Background tasks (polling and ingestion) run via FastAPI lifespan background workers using SQLite leases, so a separate worker container is optional rather than mandatory.
- Storage defaults to `./data` (or environment variable `DATA_DIR`), which mounts to `/data` in Docker.
- A built-in seed/replay mode loads verified fixtures automatically if running in an offline or read-only demonstration environment.

---

## 6. Gate Assessment for T00

- [x] **Source Class 1 (Price/EOD):** Verified with live Yahoo Finance fetch of 64 INFY sessions; fixture saved.
- [x] **Source Class 2 (Exchange Announcements):** Verified with live NSE announcements API (20 records, PDF attachments accessible); fixture saved. BSE 403 documented.
- [x] **Source Class 3 (Primary Documents):** Verified with live Infosys IR transcript download (284 KB, 28 pages); text extracted, page 4 guidance excerpt verified; manifest and PDF fixture saved.
- [x] **Hosting Requirements:** Assessed; single-container architecture with mounted persistent volume and lifespan background worker specified.
- [x] **Timebox:** Completed well within 90 minutes.

**Result: GATE PASSED. Proceeding to T01.**
