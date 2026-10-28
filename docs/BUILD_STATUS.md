# FINN Build Status & Verification Ledger

**Last Updated:** 2026-10-28T10:30:00Z (Asia/Kolkata: 2026-10-28T16:00:00Z)  
**Current Milestone:** Completed T11 -> Proceeding to T12 / T13 & Final Release  
**Repository State:** Historical replay clock (`FINN_MODE=replay`), rate limiting (HTTP 429 cooldown), crash recovery of expired leases, failure injection resilience, session isolation, and 70 passing automated tests.

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
| **T09** | Guidance ledger and first research report | **COMPLETED** | 2026-10-28T10:15:00Z | 4-quarter verified guidance ledger for INFY & HCLTECH; deterministic match verdicts (met/exceeded/missed/not_due/qualitative_supported); dual evidence drawer inspection; bounded Q&A; mobile Research screen passing. |
| **T10** | Generalization and bounded questions | **COMPLETED** | 2026-10-28T10:20:00Z | Generalization evaluation across 3 held-out tickers (COFORGE, DIXON, ASTRAL); generic FTS5 chunk retrieval; bounded question answering with exact page citations; honest empty ledger and missing data limitations passing. |
| **T11** | Replay and resilience | **COMPLETED** | 2026-10-28T10:30:00Z | Fixed historical replay clock, visible UI replay banner, 10s refresh rate limit (HTTP 429), worker lease crash recovery, HTTP 503 failure injection tolerance, and session isolation passing. |
| **T12 / T13** | Design refinement, final evaluation and release | *NEXT* | In Progress | Full release verification, tested clean-clone instructions, SUBMISSION_DRAFT.md completion. |

---

## 2. Details of Completed Packet: T11

### Changed / Created Files
- `apps/api/finn/api/briefing.py`: Added support for `FINN_MODE=replay` with fixed historical cutoff clock (`2024-10-18T23:59:59Z`), `coverage.is_replay = True`, and historical label metadata.
- `apps/api/finn/api/filings.py`: Rate limiting cooldown check (10 seconds) and replay mode interceptor bypassing live network polling.
- `apps/api/finn/ingestion/announcements.py`: Exception-safe ingestion catching network failures and recording failed sync runs gracefully.
- `apps/api/finn/main.py`: Session middleware ensuring session row exists in database for relational integrity.
- `apps/web/src/features/briefing/BriefingScreen.tsx`: Added visible Historical Replay banner when `meta.is_replay` is active.
- `tests/unit/test_resilience.py`: 5 unit tests verifying replay mode with fixed clock, refresh rate limiting (HTTP 429), failure injection without crashing, worker crash recovery via stale lease reclamation, and session isolation across independent cookies.

### Checks Actually Run & Results
1. **Replay & Resilience Unit Tests (`tests/unit/test_resilience.py`):**
   - Command: `python -m unittest tests/unit/test_resilience.py`
   - Result: 5 tests passed in 1.482s.
     - Verified replay mode sets fixed cutoff date `2024-10-18` and returns `replay_active` without outbound network calls.
     - Verified rapid consecutive calls to `/api/v1/refresh` trigger HTTP 429.
     - Verified HTTP 503 failure injection is handled gracefully without crashing the service or corrupting SQLite state.
     - Verified dead worker lease is reclaimed and job returned to queued state upon recovery.
     - Verified concurrent sessions maintain completely isolated watchlists and alert thresholds.
2. **All Unit & Contract Tests:**
   - Command: `python -m unittest discover -s tests/unit` & `python -m unittest discover -s tests/contracts`
   - Result: 67 tests passed.
3. **Full Playwright Mobile E2E Suite (`tests/e2e/`):**
   - Command: `python -m unittest discover -s tests/e2e`
   - Result: 3 tests passed in 13.098s.
4. **Total Automated Tests Passing:** 70 tests across the workspace.

### Unresolved Issues & Known Gaps
- None. All T11 gate criteria satisfied.

---

## 3. Next Packet: T12 / T13 — Design refinement, final evaluation and release

---

## 2. Details of Completed Packet: T10

### Changed / Created Files
- `apps/api/finn/research/engine.py`: Enhanced `answer_bounded_question` with generic FTS5 search across document chunks and keyword-targeted sentence extraction, while enforcing strict fallback limitations for unsupported queries.
- `apps/api/finn/retrieval/indexer.py`: Added `FTSIndexer = DocumentIndexer` alias for consistent retriever access.
- `tests/unit/test_generalization.py`: 4 unit tests verifying held-out company resolution across three distinct sectors (`COFORGE` - IT, `DIXON` - EMS, `ASTRAL` - Building Products), generic HTML IR discovery identifying missing document classes, indexing and grounded question answering with exact page citations ($516M order intake on Page 1), and honest empty ledger and limitation responses when data is unavailable.

### Checks Actually Run & Results
1. **Held-Out Generalization Tests (`tests/unit/test_generalization.py`):**
   - Command: `python -m unittest tests/unit/test_generalization.py`
   - Result: 4 tests passed in 0.214s.
     - Verified COFORGE, DIXON, ASTRAL resolve without hardcoded ticker narrative code.
     - Verified generic discovery identifies available annual reports and flags missing transcripts.
     - Verified indexing an unseen holding (`COFORGE`) allows querying and returns grounded answers with exact Page 1 citations.
     - Verified that unseen holding with missing transcripts (`DIXON`) returns an empty guidance ledger and an explicit policy limitation notice, rejecting ungrounded speculation.
2. **All Unit & Contract Tests:**
   - Command: `python -m unittest discover -s tests/unit` & `python -m unittest discover -s tests/contracts`
   - Result: 62 tests passed in 7.578s.
3. **Full Playwright Mobile E2E Suite (`tests/e2e/`):**
   - Command: `python -m unittest discover -s tests/e2e`
   - Result: 3 tests passed in 12.687s (`test_mobile_shell.py`, `test_briefing_vertical_slice.py`, `test_research_vertical_slice.py`).
4. **Total Automated Tests Passing:** 65 tests.

### Unresolved Issues & Known Gaps
- None. All T10 gate criteria satisfied.

---

## 3. Next Packet: T11 — Replay and resilience

---

## 2. Details of Completed Packet: T09

### Changed / Created Files
- `apps/api/finn/research/guidance_ledger.py`: `GuidanceStatementModel`, `GuidanceLedgerRow`, and `assess_guidance_outcome` enforcing deterministic math rules (future period -> `not_due`, qualitative -> `qualitative_supported`, margin comparisons -> `pp_delta`). Contains manually verified 4-quarter ledgers for INFY and HCLTECH.
- `apps/api/finn/research/seed_evidence.py`: Primary source documents and verbatim evidence spans for all 4 quarters of INFY and HCLTECH, ensuring dual-sided citations resolve to stored pages.
- `apps/api/finn/research/engine.py`: `ResearchEngine` generating corporate profiles, 4-quarter ledgers, source coverage, bounded Q&A, and transparent data limitations.
- `apps/api/finn/api/research.py`: API routes for `/api/v1/research/{query}`, `POST /api/v1/research`, and `POST /api/v1/research/{query}/ask`.
- `apps/api/finn/db/repository.py`: Added `list_source_documents_for_company`, default fallback for `local_path`, and `FinnRepository` backward-compatibility alias.
- `apps/web/src/features/research/ResearchScreen.tsx`: Complete mobile Research Desk UI connecting to live research and bounded Q&A endpoints, progressive stage indicator, 4-quarter ledger with Met/Exceeded/Missed/Not Due badges, Stated/Reported columns with dual [Inspect Evidence] buttons, question chips, and limitations banner.
- `apps/web/src/components/evidence/EvidenceDrawer.tsx`: Added `.evidence-drawer` dialog marker and verified page/excerpt inspection.
- `tests/unit/test_guidance_ledger.py`: 8 unit tests verifying future target `not_due` protection, qualitative statement handling without invented numbers, range evaluation (met/exceeded/missed), withdrawn status retention, verified ledger integrity, research API, and evidence resolution.
- `tests/e2e/test_research_vertical_slice.py`: Full Playwright E2E mobile test at 390x844 exercising company switching, ledger inspection, opening Evidence Drawer to verify PDF Page 4 verbatim quote, closing drawer, and asking a bounded question.

### Checks Actually Run & Results
1. **Guidance Ledger Unit Tests (`tests/unit/test_guidance_ledger.py`):**
   - Command: `python -m unittest tests/unit/test_guidance_ledger.py`
   - Result: 8 tests passed in 0.186s.
2. **Mobile Research Desk Playwright E2E (`tests/e2e/test_research_vertical_slice.py`):**
   - Command: `python -m unittest tests/e2e/test_research_vertical_slice.py`
   - Result: 1 test passed in 3.211s.
3. **Full Playwright Mobile E2E Suite (`tests/e2e/`):**
   - Command: `python -m unittest discover -s tests/e2e`
   - Result: 3 tests passed in 9.885s (`test_mobile_shell.py`, `test_briefing_vertical_slice.py`, `test_research_vertical_slice.py`).
4. **All Unit & Contract Tests:**
   - Command: `python -m unittest discover -s tests/unit` & `python -m unittest discover -s tests/contracts`
   - Result: 58 tests passed. Total 61 tests in repository passing.
5. **Frontend Production Build:**
   - Command: `npm --prefix apps/web run build`
   - Result: `tsc && vite build` completed with 0 errors.

### Unresolved Issues & Known Gaps
- None. All T09 gate criteria satisfied.

---

## 3. Next Packet: T10 — Generalization and bounded questions

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
