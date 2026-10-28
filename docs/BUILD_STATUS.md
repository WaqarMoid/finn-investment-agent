# FINN Build Status & Verification Ledger

**Last Updated:** 2026-10-28T09:51:00Z (Asia/Kolkata: 2026-10-28T15:21:00+05:30)  
**Current Milestone:** Completed T05 -> Proceeding to T06  
**Repository State:** Materiality classifier (17 reference categories, safety overrides, results notice vs actual ranking), session-isolated notification rules, alert deduplication, non-causal price movement alerts, non-notifying rule preview, and 37 passing tests.

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
| **T06** | Complete briefing vertical slice | *NEXT* | Pending | Briefing UI, 24h/7d presets, priority groups, evidence drawer, alert inbox. |
| **T07** | Primary document discovery and parsing | *Queued* | Pending | Generic IR discovery, PDF page extraction, chunking, FTS5 index. |
| **T08** | Structured extraction and financial facts | *Queued* | Pending | Normalized financial facts, deterministic QoQ/YoY, token tracking. |
| **T09** | Guidance ledger and first research report | *Queued* | Pending | 4-quarter ledger, stated vs reported assessment, dual citations. |
| **T10** | Generalization and bounded questions | *Queued* | Pending | 3-5 prepared cases, held-out evaluation on 3 unseen tickers. |
| **T11** | Replay and resilience | *Queued* | Pending | Historical replay clock, failure injection, session isolation. |

---

## 2. Details of Completed Packet: T05

### Changed / Created Files
- `apps/api/finn/ranking/materiality.py`: `MaterialityClassifier` with 17-category reference taxonomy, deterministic scoring, high-risk safety overrides (auditor resignation/qualification, CIRP/insolvency, regulatory enforcement), and distinction between meeting notices (Routine, score <25) and actual results (Needs Attention, score 65+).
- `apps/api/finn/alerts/engine.py`: `AlertEngine` implementing session-isolated notification rules (`notification_rules`), alert evaluation against filings, price moves, and volume spikes, dedup key generation (`{session}:{rule}:{company}:{event}`) to prevent duplicate notification spam, strict non-causal price movement alert wording, and non-notifying preview (`preview_rules`).
- `apps/api/finn/api/alerts.py`:
  - `GET /api/v1/notification-rules`: fetch session-scoped rules.
  - `PUT /api/v1/notification-rules`: update price threshold, volume multiple, categories, and min materiality tier.
  - `POST /api/v1/notification-rules/preview`: preview matching events from recent history without inserting inbox alerts.
  - `GET /api/v1/alerts`: fetch session alerts and unread count.
  - `PATCH /api/v1/alerts/{alert_id}`: acknowledge alert.
- `apps/api/finn/main.py`: Registered `alerts_router`.
- `tests/unit/test_materiality_and_alerts.py`: 6 unit tests verifying that results notices rank below actual results, auditor distress and insolvency trigger safety overrides, duplicate evaluations do not create duplicate alerts, price alerts use non-causal language, and rule previews do not insert inbox rows.

### Checks Actually Run & Results

1. **Materiality & Alerts Unit Tests (`tests/unit/test_materiality_and_alerts.py`):**
   - Command: `python -m unittest tests/unit/test_materiality_and_alerts.py`
   - Result: 6 tests passed in 0.224s.
     - Verified "Intimation of Board Meeting" scores 8.0 (Routine) while "Outcome of Board Meeting: Financial Results" scores 65.0 (Needs Attention).
     - Verified "Resignation of Statutory Auditor" and "Auditor's adverse remark" trigger safety overrides scoring 90+ in Needs Attention.
     - Verified "Commencement of CIRP" and "SEBI Search and Seizure" force Needs Attention.
     - Verified duplicate poll of the same announcement emits zero duplicate alerts.
     - Verified price alert states causal link is unverified, avoiding false causal attribution.
     - Verified `preview_rules` returns matches without altering the alerts count in database.
2. **Workspace Full Regression (`discover -s tests`):**
   - Command: `python -m unittest discover -s tests`
   - Result: 37 tests passed in 6.711s.

### Unresolved Issues & Known Gaps
- None. All T05 gate criteria satisfied.

---

## 3. Next Packet: T06 — Complete briefing vertical slice

**Objective:**
Connect the frontend Briefing screen to live `/api/v1/briefing` and `/api/v1/filings`, implement 24h/7d/custom time windows, live vs replay awareness, priority groups (Needs Attention, Worth a Look, Routine), event expansion, source-level filing list, real evidence drawer data loading, alert inbox badge, and settings form persistence.
