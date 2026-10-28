# FINN Build Status & Verification Ledger

**Last Updated:** 2026-10-28T09:43:00Z (Asia/Kolkata: 2026-10-28T15:13:00+05:30)  
**Current Milestone:** Completed T03 -> Proceeding to T04  
**Repository State:** Price adapter interface, offline fixture adapter, live Yahoo Finance adapter, deterministic price/volume calculations with exact threshold boundary logic, split adjustments, and price bar database storage completed and verified.

---

## 1. Work Packet History

| Packet | Description | Status | Completion Date (UTC) | Verification Gate Summary |
|---|---|---|---|---|
| **T00** | Source feasibility and runtime spike | **COMPLETED** | 2026-10-28T09:18:00Z | 3/3 source classes verified with real network calls; 3 fixtures saved; primary PDF downloaded and text extracted; hosting evaluated; gate passed. |
| **T01** | Repo, shell and first deployment | **COMPLETED** | 2026-10-28T09:29:00Z | React/TS frontend (Vite), FastAPI API, lockfiles, `.env.example`, Dockerfile/Compose, unit tests, Playwright 390px mobile navigation shell, deep-link reload passing. |
| **T02** | Database, identity and evidence backbone | **COMPLETED** | 2026-10-28T09:39:00Z | Clean DB migration & rerun; foreign keys enforced; 22 candidate holdings seeded; exact symbol, ISIN, BSE code & alias resolver; immutable document/evidence storage; session-isolated watchlists passing. |
| **T03** | Price adapter and deterministic calculations | **COMPLETED** | 2026-10-28T09:43:00Z | Price adapter interface, live & fixture adapters; volume baseline (prior 20 completed sessions excluding today); price delta; zero/negative/missing data; strictly-greater-than 5% and 2.0x threshold gates; stock split adjustment; live integration smoke check passing. |
| **T04** | Exchange ingestion and reliable jobs | *NEXT* | Pending | NSE announcement adapter, attachment jobs, deduplication, worker leases. |
| **T05** | Materiality and alerts | *Queued* | Pending | 17-category taxonomy, ranking tiers, safety overrides, session rules, preview. |
| **T06** | Complete briefing vertical slice | *Queued* | Pending | Briefing UI, 24h/7d presets, priority groups, evidence drawer, alert inbox. |
| **T07** | Primary document discovery and parsing | *Queued* | Pending | Generic IR discovery, PDF page extraction, chunking, FTS5 index. |
| **T08** | Structured extraction and financial facts | *Queued* | Pending | Normalized financial facts, deterministic QoQ/YoY, token tracking. |
| **T09** | Guidance ledger and first research report | *Queued* | Pending | 4-quarter ledger, stated vs reported assessment, dual citations. |
| **T10** | Generalization and bounded questions | *Queued* | Pending | 3-5 prepared cases, held-out evaluation on 3 unseen tickers. |
| **T11** | Replay and resilience | *Queued* | Pending | Historical replay clock, failure injection, session isolation. |

---

## 2. Details of Completed Packet: T03

### Changed / Created Files
- `apps/api/finn/adapters/price_adapter.py`: `PriceBar` schema (session date, OHLCV, adjusted close, provider, revision), `PriceAdapter` abstract interface, `FixturePriceAdapter` (reads offline fixture JSON), and `YahooPriceAdapter` (HTTPX client hitting Yahoo Finance `/v8/finance/chart`).
- `apps/api/finn/finance/calculations.py`:
  - `calculate_price_move`: Deterministic Decimal calculation, strictly-greater-than 5.0% threshold check, handles zero/negative baseline and insufficient history.
  - `calculate_volume_spike`: Excludes today's bar, calculates mean of prior 20 completed sessions, strictly-greater-than 2.0x threshold check, handles zero baseline and insufficient history (<20 sessions).
  - `adjust_for_stock_split`: Historical price/volume adjustment for corporate actions (e.g. 2:1 split).
- `apps/api/finn/db/repository.py`: Added `store_price_bars` and `get_price_bars` with revision-based deduplication and session date indexing.
- `apps/api/finn/api/prices.py`: `GET /api/v1/companies/{company_id}/prices` endpoint returning daily bars, price delta, and volume spike analysis.
- `apps/api/finn/main.py`: Registered `prices_router`.
- `tests/unit/test_price_calculations.py`: 9 offline unit tests covering normal price move, exactly-5% threshold, exactly-2x volume multiple, prior-20 volume exclusion, insufficient history, zero/negative baseline, weekend session gaps, stock split adjustment, and fixture parsing.
- `tests/integration/test_price_live_smoke.py`: Separately marked integration test exercising the live Yahoo Finance endpoint for `INFY.NS`.

### Checks Actually Run & Results

1. **Price Calculation Unit Tests (`tests/unit/test_price_calculations.py`):**
   - Command: `python -m unittest tests/unit/test_price_calculations.py`
   - Result: 9 tests passed in 0.005s (zero network requests, fully offline).
     - Verified move of 5.00% is NOT an alert; 5.01% is an alert (strictly greater rule).
     - Verified volume multiple of 2.00x is NOT an alert; 2.01x is an alert (strictly greater rule).
     - Verified today's volume is excluded from the 20-day mean baseline.
     - Verified insufficient history returns `is_alert: False`.
     - Verified zero/negative baseline close returns `status: "invalid_baseline"`, `delta_pct: None`.
     - Verified 20-day zero volume returns `status: "zero_baseline"`, `volume_multiple: None`.
     - Verified weekend gap between Friday (2026-10-23) and Monday (2026-10-26) correctly computes delta without missing-day alert.
     - Verified 2:1 stock split adjustment prevents false -47.5% price crash.
2. **Separately Marked Live Smoke Test (`tests/integration/test_price_live_smoke.py`):**
   - Command: `python -m unittest tests/integration/test_price_live_smoke.py`
   - Result: 1 test passed in 1.209s. Fetched live INFY daily sessions, verified >21 bars returned, Decimal close price > 0, calculations executed without error.
3. **Workspace Full Regression (`discover -s tests`):**
   - Command: `python -m unittest discover -s tests`
   - Result: 24 tests passed in 6.379s.

### Unresolved Issues & Known Gaps
- None. All T03 gate criteria satisfied.

---

## 3. Next Packet: T04 — Exchange ingestion and reliable jobs

**Objective:**
Implement the NSE corporate announcement adapter, attachment download jobs, announcement deduplication (within exchange and cross-source), durable background worker leases in SQLite, retries with exponential backoff/circuit breaker, and manual refresh endpoint with rate limiting.
