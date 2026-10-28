# FINN Build Status & Verification Ledger

**Last Updated:** 2026-10-28T09:59:00Z (Asia/Kolkata: 2026-10-28T15:29:00+05:30)  
**Current Milestone:** Completed T08 -> Proceeding to T09  
**Repository State:** Financial fact normalization (crore/lakh/million/billion), deterministic QoQ/YoY growth, margin percentage-point handling, bank sector EBITDA suppression, Q4 derivation linking operands, token/cost instrumentation, and 53 passing automated tests.

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
| **T08** | Structured extraction and financial facts | **COMPLETED** | 2026-10-28T09:59:00Z | Financial fact normalization to INR crore, deterministic growth deltas, margin percentage points (+3 pp), bank EBITDA suppression, Q4 = FY - 9M derivation citing both operands, token/cost instrumentation, and repeat-call caching passing. |
| **T09** | Guidance ledger and first research report | *NEXT* | Pending | 4-quarter ledger, stated vs reported assessment, dual citations. |
| **T10** | Generalization and bounded questions | *Queued* | Pending | 3-5 prepared cases, held-out evaluation on 3 unseen tickers. |
| **T11** | Replay and resilience | *Queued* | Pending | Historical replay clock, failure injection, session isolation. |

---

## 2. Details of Completed Packet: T08

### Changed / Created Files
- `apps/api/finn/finance/normalizer.py`: `FinancialFactModel` schema and `normalize_to_crore` implementing standard conversion ratios for INR crore (1 cr = 100 lakh = 10 million = 0.01 billion) and negative accounting parenthetical parsing.
- `apps/api/finn/finance/fact_engine.py`:
  - `calculate_growth_delta`: Deterministic growth calculation; margin changes return percentage point difference (`pp_delta`); non-positive priors produce absolute deltas with descriptive wording ("loss narrowed" / "loss widened") and percentage `None`.
  - `derive_q4_from_fy_and_9m`: Mathematical derivation of Q4 from Full Year minus 9-Month YTD, citing both operand fact IDs and preserving dual evidence spans.
  - `check_sector_metric`: Sector-aware metric policy suppressing EBITDA for Banking and Financial Institutions.
- `apps/api/finn/llm/client.py`: Provider-neutral `LLMClient` with Pydantic schema validation, in-memory/DB caching by input hash, and token usage and estimated cost instrumentation.
- `tests/unit/test_financial_facts.py`: 7 unit tests verifying unit normalization, bank EBITDA suppression, margin percentage point differences, non-positive prior handling, Q4 derivation, missing value preservation (missing is not zero), and token/cost tracking.

### Checks Actually Run & Results

1. **Financial Facts Unit Tests (`tests/unit/test_financial_facts.py`):**
   - Command: `python -m unittest tests/unit/test_financial_facts.py`
   - Result: 7 tests passed in 0.001s.
     - Verified unit normalization: 10,000 lakh = 100 crore; 1,000 million = 100 crore; 1 billion = 100 crore; (50.0) = -50.00.
     - Verified bank sector EBITDA is suppressed with explicit sector caveat.
     - Verified margin change (18% to 21%) is reported as +3.00 percentage points, not percent growth.
     - Verified prior loss (-200 to +150) produces absolute delta (+350) and percentage `None`.
     - Verified Q4 derivation cites both FY and 9M operands.
     - Verified missing values remain `None` and do not become `0`.
     - Verified LLM client calculates token cost and returns cached repeat calls with zero cost.
2. **Workspace Full Regression (`discover -s tests`):**
   - Command: `python -m unittest discover -s tests`
   - Result: 53 tests passed in 12.258s.

### Unresolved Issues & Known Gaps
- None. All T08 gate criteria satisfied.

---

## 3. Next Packet: T09 — Guidance ledger and first research report

**Objective:**
Implement the Management Guidance extraction pipeline (speaker, target period, conditions, original vs revised), deterministic outcome matching and assessment (*met*, *exceeded*, *missed*, *not yet due*, *not comparable*, *no guidance*), the 4-quarter Guidance Ledger for Infosys (`INFY`) and HCLTECH (`HCLTECH`), research job progress tracking, dual citations (stated quote + reported outcome), and Research screen UI integration.
