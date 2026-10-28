# FINN Build Status & Verification Ledger

**Last Updated:** 2026-10-28T09:47:00Z (Asia/Kolkata: 2026-10-28T15:17:00+05:30)  
**Current Milestone:** Completed T04 -> Proceeding to T05  
**Repository State:** Exchange announcement ingestion pipeline, durable SQLite job manager with atomic lease claims, attachment job queues, duplicate poll deduplication, watermark protection on middle-page failures, rate-limited refresh API, and 31 passing tests.

---

## 1. Work Packet History

| Packet | Description | Status | Completion Date (UTC) | Verification Gate Summary |
|---|---|---|---|---|
| **T00** | Source feasibility and runtime spike | **COMPLETED** | 2026-10-28T09:18:00Z | 3/3 source classes verified with real network calls; 3 fixtures saved; primary PDF downloaded and text extracted; hosting evaluated; gate passed. |
| **T01** | Repo, shell and first deployment | **COMPLETED** | 2026-10-28T09:29:00Z | React/TS frontend (Vite), FastAPI API, lockfiles, `.env.example`, Dockerfile/Compose, unit tests, Playwright 390px mobile navigation shell, deep-link reload passing. |
| **T02** | Database, identity and evidence backbone | **COMPLETED** | 2026-10-28T09:39:00Z | Clean DB migration & rerun; foreign keys enforced; 22 candidate holdings seeded; exact symbol, ISIN, BSE code & alias resolver; immutable document/evidence storage; session-isolated watchlists passing. |
| **T03** | Price adapter and deterministic calculations | **COMPLETED** | 2026-10-28T09:43:00Z | Price adapter interface, live & fixture adapters; volume baseline (prior 20 completed sessions excluding today); price delta; zero/negative/missing data; strictly-greater-than 5% and 2.0x threshold gates; stock split adjustment; live integration smoke check passing. |
| **T04** | Exchange ingestion and reliable jobs | **COMPLETED** | 2026-10-28T09:47:00Z | NSE announcement adapter, attachment download jobs, durable SQLite worker leases, crash recovery, duplicate poll dedup, partial pagination watermark protection, 403/429 visible error state, rate-limited refresh passing. |
| **T05** | Materiality and alerts | *NEXT* | Pending | 17-category taxonomy, ranking tiers, safety overrides, session rules, preview. |
| **T06** | Complete briefing vertical slice | *Queued* | Pending | Briefing UI, 24h/7d presets, priority groups, evidence drawer, alert inbox. |
| **T07** | Primary document discovery and parsing | *Queued* | Pending | Generic IR discovery, PDF page extraction, chunking, FTS5 index. |
| **T08** | Structured extraction and financial facts | *Queued* | Pending | Normalized financial facts, deterministic QoQ/YoY, token tracking. |
| **T09** | Guidance ledger and first research report | *Queued* | Pending | 4-quarter ledger, stated vs reported assessment, dual citations. |
| **T10** | Generalization and bounded questions | *Queued* | Pending | 3-5 prepared cases, held-out evaluation on 3 unseen tickers. |
| **T11** | Replay and resilience | *Queued* | Pending | Historical replay clock, failure injection, session isolation. |

---

## 2. Details of Completed Packet: T04

### Changed / Created Files
- `apps/api/finn/adapters/exchange_adapter.py`: `AnnouncementRecord` model, `ExchangeAdapter` abstract interface, `FixtureExchangeAdapter` (parses NSE announcements fixture), `NSEExchangeAdapter` (live HTTPX client), and `BSEExchangeAdapter` (explicitly documented HTTP 403 Cloudflare contingency state).
- `apps/api/finn/jobs/worker.py`: `JobManager` providing durable SQLite-backed background job queue with atomic lease claims (`BEGIN IMMEDIATE; SELECT ... UPDATE ... COMMIT;`), heartbeats, bounded retries, and automatic crash recovery (`recover_stale_jobs`).
- `apps/api/finn/ingestion/announcements.py`: `AnnouncementIngestionService` coordinating announcement fetching, company resolution, category classification (17-category reference taxonomy), deduplication by `(exchange, source_id)`, attachment job enqueueing, canonical `event_groups` grouping, and watermark protection.
- `apps/api/finn/api/filings.py`: `GET /api/v1/filings` paginated announcement endpoint and `POST /api/v1/refresh` rate-limited manual trigger (10-second cooldown per session).
- `apps/api/finn/main.py`: Registered `filings_router`.
- `tests/unit/test_jobs_and_ingestion.py`: 6 unit tests verifying that middle-page failures do not advance watermarks, duplicate polls emit zero duplicate rows, BSE 403 and rate limit 429 become visible partial states, worker leases recover stale jobs after simulated crash, and revised attachments retain previous versions in `supersedes_id`.
- `tests/unit/test_filings_api.py`: 1 unit test verifying filings pagination and refresh rate-limiting (HTTP 429).

### Checks Actually Run & Results

1. **Jobs & Ingestion Unit Tests (`tests/unit/test_jobs_and_ingestion.py`):**
   - Command: `python -m unittest tests/unit/test_jobs_and_ingestion.py`
   - Result: 6 tests passed in 0.242s.
     - Verified partial page failure records `status: "partial"` in `sync_runs` and leaves `watermark_advanced == False`.
     - Verified duplicate poll of 20 announcements inserts 0 new rows and increments duplicate count.
     - Verified BSE 403 Cloudflare block is captured as visible partial state without crashing.
     - Verified HTTP 429 rate limit is captured cleanly.
     - Verified atomic job lease claim and recovery of stale running jobs after simulated worker crash.
     - Verified revised PDF document retains prior document ID in `supersedes_id`.
2. **Filings & Refresh API Test (`tests/unit/test_filings_api.py`):**
   - Command: `python -m unittest tests/unit/test_filings_api.py`
   - Result: 1 test passed in 0.857s, verifying `/api/v1/filings` returns paginated records and rapid second refresh triggers HTTP 429.
3. **Workspace Full Regression (`discover -s tests`):**
   - Command: `python -m unittest discover -s tests`
   - Result: 31 tests passed in 6.727s.

### Unresolved Issues & Known Gaps
- None. All T04 gate criteria satisfied.

---

## 3. Next Packet: T05 — Materiality and alerts

**Objective:**
Implement the 17-category taxonomy mapping, subtype classification, deterministic ranking tiers (*Needs Attention*, *Worth a Look*, *Routine*), safety overrides (insolvency, auditor resignation/qualification, severe regulatory action), persisted session-scoped notification rules, alert evaluation & deduplication, and non-notifying rules preview.
