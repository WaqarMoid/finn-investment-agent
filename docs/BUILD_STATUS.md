# FINN Build Status & Verification Ledger

**Last Updated:** 2026-10-28T09:39:00Z (Asia/Kolkata: 2026-10-28T15:09:00+05:30)  
**Current Milestone:** Completed T02 -> Proceeding to T03  
**Repository State:** Database migrations, foreign key constraints, company resolver (22 candidate companies, ISIN, BSE, aliases), immutable source document/page/evidence storage, and session-isolated watchlist completed and verified.

---

## 1. Work Packet History

| Packet | Description | Status | Completion Date (UTC) | Verification Gate Summary |
|---|---|---|---|---|
| **T00** | Source feasibility and runtime spike | **COMPLETED** | 2026-10-28T09:18:00Z | 3/3 source classes verified with real network calls; 3 fixtures saved; primary PDF downloaded and text extracted; hosting evaluated; gate passed. |
| **T01** | Repo, shell and first deployment | **COMPLETED** | 2026-10-28T09:29:00Z | React/TS frontend (Vite), FastAPI API, lockfiles, `.env.example`, Dockerfile/Compose, unit tests, Playwright 390px mobile navigation shell, deep-link reload passing. |
| **T02** | Database, identity and evidence backbone | **COMPLETED** | 2026-10-28T09:39:00Z | Clean DB migration & rerun; foreign keys enforced; 22 candidate holdings seeded; exact symbol, ISIN, BSE code & alias resolver; immutable document/evidence storage; session-isolated watchlists passing. |
| **T03** | Price adapter and deterministic calculations | *NEXT* | Pending | EOD daily-bar adapter, volume baseline, price move delta, zero/missing handling. |
| **T04** | Exchange ingestion and reliable jobs | *Queued* | Pending | NSE announcement adapter, attachment jobs, deduplication, worker leases. |
| **T05** | Materiality and alerts | *Queued* | Pending | 17-category taxonomy, ranking tiers, safety overrides, session rules, preview. |
| **T06** | Complete briefing vertical slice | *Queued* | Pending | Briefing UI, 24h/7d presets, priority groups, evidence drawer, alert inbox. |
| **T07** | Primary document discovery and parsing | *Queued* | Pending | Generic IR discovery, PDF page extraction, chunking, FTS5 index. |
| **T08** | Structured extraction and financial facts | *Queued* | Pending | Normalized financial facts, deterministic QoQ/YoY, token tracking. |
| **T09** | Guidance ledger and first research report | *Queued* | Pending | 4-quarter ledger, stated vs reported assessment, dual citations. |
| **T10** | Generalization and bounded questions | *Queued* | Pending | 3-5 prepared cases, held-out evaluation on 3 unseen tickers. |
| **T11** | Replay and resilience | *Queued* | Pending | Historical replay clock, failure injection, session isolation. |

---

## 2. Details of Completed Packet: T02

### Changed / Created Files
- `apps/api/finn/db/schema.sql`: Complete SQLite DDL with WAL mode, foreign keys, FTS5 virtual table (`chunks_fts`), and all core relational entities (`companies`, `securities`, `company_aliases`, `sessions`, `watchlist_members`, `source_documents`, `source_pages`, `evidence_spans`, `document_chunks`, `announcements`, `event_groups`, `price_bars`, `financial_facts`, `derivations`, `guidance_statements`, `guidance_assessments`, `notification_rules`, `alerts`, `jobs`, `sync_runs`).
- `apps/api/finn/db/database.py`: Connection manager (`get_connection`), SQLite busy timeout (5000ms), and idempotent migration executor (`init_db`).
- `apps/api/finn/db/seed_data.py`: Validated candidate master for the 18 portfolio holdings + 4 ad-hoc research test companies (`INFY`, `TCS`, `HCLTECH`, `RELIANCE`, `HDFCBANK`, `ICICIBANK`, `HINDUNILVR`, `ITC`, `LT`, `SUNPHARMA`, `DRREDDY`, `MARUTI`, `TITAN`, `ULTRACEMCO`, `NTPC`, `TATASTEEL`, `PERSISTENT`, `KAYNES`, `CERA`, `COFORGE`, `DIXON`, `ASTRAL`) with exact ISINs, official websites, and IR domains.
- `apps/api/finn/db/resolver.py`: `CompanyResolver` prioritizing exact symbol matches, ISIN, and BSE scrip codes before alias lookups; handles `.NS` and `.BO` suffixes cleanly; returns unambiguous match, ambiguous candidates list, or unknown.
- `apps/api/finn/db/repository.py`: `DataRepository` handling master seeding, session creation, session-isolated watchlist CRUD, immutable source document storage with SHA-256 hashes, 1-based page records, evidence spans, and evidence retrieval.
- `apps/api/finn/api/companies.py`: `GET /api/v1/companies?q=...` company resolution endpoint.
- `apps/api/finn/api/watchlist.py`: `GET /api/v1/watchlist`, `POST /api/v1/watchlist`, `DELETE /api/v1/watchlist/{company_id}` endpoints scoped by `finn_session_id`.
- `apps/api/finn/api/evidence.py`: `GET /api/v1/evidence/{evidence_id}` endpoint returning verified verbatim excerpts, PDF page numbers, and primary document metadata.
- `apps/api/finn/main.py`: Updated lifespan to initialize DB and seed master data on startup; registered new API routers.
- `tests/contracts/test_db_and_resolver.py`: 9 contract tests verifying migration idempotency, foreign key enforcement, symbol/ISIN/BSE/alias resolution, ambiguous/unknown handling, document/evidence provenance, and multi-session watchlist isolation.

### Checks Actually Run & Results

1. **Database & Resolver Contract Tests (`tests/contracts/test_db_and_resolver.py`):**
   - Command: `python -m unittest tests/contracts/test_db_and_resolver.py`
   - Result: 9 tests passed in 0.354s.
     - `test_migration_idempotency`: Rerun DDL on populated DB succeeded without errors.
     - `test_foreign_key_enforcement`: Inserting security for non-existent company raised `sqlite3.IntegrityError`.
     - `test_candidate_holdings_seeded`: Verified $\ge 18$ candidate companies populated.
     - `test_resolver_exact_symbol_and_suffixes`: Verified `INFY`, `infy.ns`, `TCS.BO` resolve to exact companies.
     - `test_resolver_bse_code_and_isin`: Verified BSE scrip `500209` and ISIN `INE009A01021` resolve directly.
     - `test_resolver_aliases`: Verified `HCL Tech` resolves to `INE860A01027`.
     - `test_resolver_unknown_and_ambiguous`: Verified unknown entities and ambiguous queries (`Limited`) return structured candidate lists rather than throwing or picking arbitrary records.
     - `test_evidence_backbone_and_provenance`: Verified immutable document insert, 1-based page index, and evidence span retrieval.
     - `test_session_watchlist_isolation`: Verified Session A and Session B maintain completely independent watchlists; edits in one do not mutate the other.
2. **Full Workspace Regression (`discover -s tests`):**
   - Command: `python -m unittest discover -s tests`
   - Result: 14 tests passed in 6.263s (Unit + Contracts + Playwright 390px E2E).

### Unresolved Issues & Known Gaps
- None. All T02 gate criteria satisfied.

---

## 3. Next Packet: T03 — Price adapter and deterministic calculations

**Objective:**
Implement the price adapter interface (`PriceAdapter`), live Yahoo Finance adapter, fixture adapter (`tests/fixtures/source/infy_eod_sample.json`), completed-session handling, volume baseline (mean of previous 20 completed sessions excluding today), price move delta calculation, corporate action adjustment policies, and unit tests covering edge cases (zero/negative/missing data, exactly-2x volume threshold, weekends, provider revision).
