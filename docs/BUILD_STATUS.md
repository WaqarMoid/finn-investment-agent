# FINN Build Status & Verification Ledger

**Last Updated:** 2026-10-28T09:54:00Z (Asia/Kolkata: 2026-10-28T15:24:00+05:30)  
**Current Milestone:** Completed T06 -> Proceeding to T07  
**Repository State:** Complete Briefing vertical slice connected to live backend APIs (`/api/v1/briefing`, `/api/v1/events/{id}`, `/api/v1/evidence/{id}`, `/api/v1/watchlist`, `/api/v1/notification-rules`), real evidence drawer loading, date window filtering (24h/7d/custom), session alert settings with non-notifying preview, and 41 passing automated tests.

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
| **T07** | Primary document discovery and parsing | *NEXT* | Pending | Generic IR discovery, PDF page extraction, chunking, FTS5 index. |
| **T08** | Structured extraction and financial facts | *Queued* | Pending | Normalized financial facts, deterministic QoQ/YoY, token tracking. |
| **T09** | Guidance ledger and first research report | *Queued* | Pending | 4-quarter ledger, stated vs reported assessment, dual citations. |
| **T10** | Generalization and bounded questions | *Queued* | Pending | 3-5 prepared cases, held-out evaluation on 3 unseen tickers. |
| **T11** | Replay and resilience | *Queued* | Pending | Historical replay clock, failure injection, session isolation. |

---

## 2. Details of Completed Packet: T06

### Changed / Created Files
- `apps/api/finn/api/briefing.py`:
  - `GET /api/v1/briefing`: Date-windowed event query (`[start_utc, end_utc)`), tier partitioning (*Needs Attention*, *Worth a Look*, *Routine*), summary counts bar with exact reconciliation to records (`total_events == sum(tiers)`), and source freshness/coverage metadata.
  - `GET /api/v1/events/{event_id}`: Canonical event group details and associated raw filings list.
- `apps/api/finn/main.py`: Registered `briefing_router` and `events_router`; added lifespan seeding for verified primary evidence spans.
- `apps/web/src/components/evidence/EvidenceDrawer.tsx`: Converted to live API integration, querying `GET /api/v1/evidence/{evidenceId}`, rendering verbatim excerpt, issuer, publisher, 1-based PDF page index, and direct PDF link button.
- `apps/web/src/features/briefing/BriefingScreen.tsx`: Converted to live API integration with 24h/7d/custom presets, summary counts bar, manual refresh trigger, and evidence drawer invocation.
- `apps/web/src/features/watchlist/WatchlistScreen.tsx`: Connected to live `GET /api/v1/watchlist`, `GET /api/v1/notification-rules`, and `PUT /api/v1/notification-rules`; added "Test on recent data" preview caller and session alerts inbox.
- `tests/unit/test_briefing_api.py`: 3 unit tests verifying briefing response structure, count reconciliation, custom date window filtering, and evidence lookup.
- `tests/e2e/test_briefing_vertical_slice.py`: Playwright mobile E2E test verifying changing date range presets (24h to 7d), opening Evidence Drawer and verifying exact quote & page number, saving custom notification thresholds, and running non-notifying rule preview.

### Checks Actually Run & Results

1. **Frontend Production Build:**
   - Command: `cd apps/web; npm run build`
   - Result: `tsc` typecheck passed with 0 errors; Vite bundle built in 693ms.
2. **Briefing API Unit Tests (`tests/unit/test_briefing_api.py`):**
   - Command: `python -m unittest tests/unit/test_briefing_api.py`
   - Result: 3 tests passed in 0.869s. Verified summary counts equal sum of tier counts, custom date window accepted, and evidence lookup returns Page 4 verbatim guidance excerpt.
3. **Playwright Mobile E2E Vertical Slice Test (`tests/e2e/test_briefing_vertical_slice.py`):**
   - Command: `python -m unittest tests/e2e/test_briefing_vertical_slice.py`
   - Result: 1 test passed in 4.355s at 390x844 mobile viewport.
     - Verified date window toggle to "7 Days".
     - Verified clicking "Inspect Source" opens Evidence Drawer showing Page 4 verbatim guidance quote.
     - Verified closing drawer restores view.
     - Verified navigating to Watchlist, saving custom threshold (6.5%), and seeing "Rules saved for this session!".
     - Verified clicking "Test on recent data" returns preview matches without creating alerts.
4. **Workspace Full Regression (`discover -s tests`):**
   - Command: `python -m unittest discover -s tests`
   - Result: 41 tests passed in 11.713s.

### Unresolved Issues & Known Gaps
- None. All T06 gate criteria satisfied.

---

## 3. Next Packet: T07 — Primary document discovery and parsing

**Objective:**
Implement generic company IR discovery (annual reports and transcripts acquisition), PDF page extraction and text chunking, SQLite FTS5 index population, source quality/coverage manifest, bounded source URL validation (SSRF-safe, rejecting private IP ranges), and multi-layout PDF test fixtures.
