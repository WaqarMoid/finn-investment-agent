# FINN Submission Materials & Evaluation Report

**Status:** Ready for final review. All bracketed placeholders have been replaced with authentic, verified implementation outcomes from tests and live execution.

---

## 1. Candidate Covering Note

**To:** assessment@enam.com  
**Subject:** ENAM - IIT screening - 2027

Hello ENAM team,

I built FINN, a mobile-first, evidence-first portfolio briefing and primary-source research engine for Indian equity investors. It focuses on two core workflows:

1. **Evidence-First Portfolio Briefing:** A priority-ranked digest that syncs the selected 24-hour, seven-day, or custom interval from NSE and scopes results to the session's 18-company watchlist. Each event opens its actual NSE attachment. Counts reconcile to the source filings in the selected time window.
2. **Evidence-Gated Research Desk:** Official issuer source libraries and current verified financial snapshots are registered for INFY, HCLTECH, TCS, and RELIANCE. Every displayed fact opens an inspectable first-party excerpt. Management-guidance verdicts appear only when a statement and comparable outcome are both verified; missing extraction is shown as a coverage gap.

- **Mobile-First Prototype URL:** [https://burner-trips-sell-murphy.trycloudflare.com](https://burner-trips-sell-murphy.trycloudflare.com) *(No password or IP verification required; opens directly on phone and desktop)*
- **Permanent-hosting setup:** [one-click Render Blueprint](https://render.com/deploy?repo=https://github.com/WaqarMoid/finn-investment-agent)
- **GitHub Repository:** [https://github.com/WaqarMoid/finn-investment-agent](https://github.com/WaqarMoid/finn-investment-agent)
- **AI Build History:**
  - Architecture & Planning (ChatGPT): [https://chatgpt.com/s/cx_6ae2e567879881919375559c9eedc46e](https://chatgpt.com/s/cx_6ae2e567879881919375559c9eedc46e)
  - Implementation Transcript (Antigravity): [`docs/ai_build_history_transcript.jsonl`](docs/ai_build_history_transcript.jsonl)
  - Verification & Status Ledger: [`docs/BUILD_STATUS.md`](docs/BUILD_STATUS.md)

### Key Product & Technical Choices
- **Deterministic Financial Logic:** Large Language Models are strictly confined to identifying candidates and formatting. All math (YoY growth, percentage-point deltas on operating margins, 20-session volume baselines, Q4 derivations as `FY - 9M`, and guidance band evaluations) is computed in deterministic, audited Python code. Bank EBITDA is explicitly suppressed.
- **Session-Scoped Isolation:** Watchlists and alert thresholds are strictly isolated per anonymous browser session cookie (`finn_session_id`), preventing multi-user cross-contamination without requiring mandatory sign-in friction.
- **Primary-Source Grounding:** Research pulls exclusively from official company IR annual reports and earnings call transcripts; secondary blogs, news aggregator summaries, and broker notes are forbidden.
- **Unified Container Architecture:** React 18 + Vite frontend compiles into static assets served directly by FastAPI from `apps/web/dist`, with client-side SPA fallback and `/api/v1/*` routing.

### Verification & Testing
- **Automated Test Suite:** 70 automated tests passing across the workspace:
  - 58 Unit tests (`tests/unit/`): price arithmetic, volume baselines, exchange ingestion, materiality ranking, financial fact normalization, guidance ledger logic, generalization, and resilience.
  - 9 Contract tests (`tests/contracts/`): database migrations, foreign keys, identity resolver, and source page provenance.
  - 3 Playwright Mobile E2E tests (`tests/e2e/`): 390x844 mobile viewport navigation, Briefing vertical slice, and Research Desk Guidance Ledger dual-evidence inspection.
- **Generalization Gate:** Evaluated across 3 held-out tickers representing different sectors: `COFORGE` (IT Services), `DIXON` (Electronics Manufacturing), and `ASTRAL` (Building Products). Successfully resolved identities without ticker-specific code, identified missing document classes via generic HTML discovery, indexed and answered questions with exact Page 1 citations ($516M order intake for Coforge), and returned honest policy limitations when transcripts were unavailable.
- **Data Freshness & Replay:** Supports both `FINN_MODE=live` (fetching live NSE announcements and EOD bars) and `FINN_MODE=replay` (fixed historical clock at `2024-10-18T23:59:59Z`, Q2 FY25 results season, with visible UI badge and offline fixture resilience).

### Deliberate Tradeoffs & Known Limitations
- **BSE Cloudflare Block:** Automated requests to BSE India endpoints return HTTP 403 (Cloudflare bot detection). In accordance with instructions, BSE is documented as an authentic upstream limitation; NSE serves as the primary exchange feed.
- **No Generative Chatbot Hero:** Omitted conversational free-form chatbots in favor of an actionable 3-tab mobile shell (Briefing, Research, Watchlist) and bounded question inputs with cited evidence.
- **Future Targets:** In-progress full-year guidance (e.g. Q4 FY25) is classified as `not_due` rather than marked missed or met prematurely.

Regards,  
Antigravity & Candidate Engineer

---

## 2. Three-Minute Evaluator Demo Script

- **0:00–0:20 — Opening & Mode Setup:**
  - Launch application on mobile viewport (390x844).
  - Note header displaying `Mode: Live / IST` or `Historical Replay (Oct 18, 2024)`.
  - Point out 18 default monitored Indian equity holdings across diverse sectors.
- **0:20–1:00 — Portfolio Briefing & Evidence Inspection:**
  - View priority-ranked digest: notice *Needs Attention* item (e.g., Q2 FY25 Financial Results) elevated above routine notices.
  - Click "Inspect Stated Evidence [1]": Evidence Drawer slides in showing exact document title, publisher, PDF Page 4, and verbatim excerpt.
  - Expand *Routine Filings* section to confirm all 20 ingested exchange records are accounted for; none were silently discarded.
- **1:00–1:25 — Unusual Price & Volume Calculations:**
  - View alerts inbox: notice price move alert (>5.0%) and volume spike alert (>2.0x).
  - Highlight that price movements are stated factually with signed values and never attribute speculative causation to coincident news.
- **1:25–2:20 — Signature Feature: 4-Quarter Guidance Ledger:**
  - Switch to the **Research** tab and load `INFY` (Infosys Limited).
  - Inspect the 4-Quarter Management Guidance Ledger:
    - Q1 FY25: Guided 1.0%–3.0% CC growth, reported 2.5% -> **MET**.
    - Q2 FY25: Upward revision to 3.0%–4.0%, reported 3.8% -> **MET** (badge indicates revised target).
    - Q3 FY25: Tightened band 3.75%–4.50%, reported 4.2% -> **MET**.
    - Q4 FY25: Full-year target 4.5%–5.0% -> **NOT YET DUE** (safeguarded against premature verdict).
  - Click dual inspect buttons to verify both stated transcript quotes and reported filing figures.
- **2:20–2:45 — Held-Out Generalization & Bounded Questions:**
  - Switch ticker to `HCLTECH`: inspect operating margin EBIT ledger row (guided 18.0%–19.0%, reported 18.6% -> MET).
  - Use bounded question suggestion: "What changed in guidance?" -> Answer returns exact guided revision history with citations.
  - Enter speculative question on an unseen holding (`DIXON`) -> Engine cleanly responds: *"The available primary filing records... do not contain explicit commentary directly answering this inquiry without speculative extrapolation."*
- **2:45–3:00 — Wrap-Up & Architecture:**
  - Highlight reproducible single Docker container, WAL-mode SQLite database with FTS5, and 70 passing automated tests.

---

## 3. Final Submission Inventory Check

- [x] Tested clean-clone README with quickstart commands.
- [x] Environment configuration template (`.env.example`) present without secrets.
- [x] Dockerfile and `compose.yaml` verified.
- [x] SQLite WAL migrations and seed data intact.
- [x] Primary source fixtures saved in `tests/fixtures/source/`.
- [x] 70/70 automated tests passing (`tests/unit`, `tests/contracts`, `tests/e2e`).
- [x] Mobile viewport responsive at 390px with zero horizontal scroll overflow.
- [x] Complete packet history documented in `docs/BUILD_STATUS.md`.
