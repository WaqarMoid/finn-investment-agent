# FINN: Evidence-First Portfolio Briefing Engine

FINN is a mobile-first, evidence-linked portfolio briefing and primary-source research application designed for Indian equity investors.

It directly answers three daily investor questions:
1. **What changed?** (Priority-ranked corporate filings and unusual price/volume moves).
2. **Why does it matter?** (Concise 30-word implication and rule-based materiality classification).
3. **What supports that?** (Direct links to primary sources via an immutable Evidence Drawer with 1-based PDF page numbers and verbatim excerpts).

The research desk keeps an official-source catalog and exposes a Management Guidance Ledger only when both a management statement and a comparable outcome have inspectable evidence. Missing extraction remains visibly pending instead of being filled with sample claims.

---

## 1. Key Features

- **Mobile-First Responsive Shell (390px):** Built with 3 primary destinations (Briefing, Research, Watchlist), 44px touch targets, zero horizontal overflow, and deep-link browser navigation.
- **Priority-Ranked Briefing Digest:** Ingests exchange announcements, ranking them into *Needs Attention*, *Worth a Look*, and *Routine*. High-risk overrides guarantee auditor distress, insolvency, and corporate actions are never buried.
- **Count Reconciliation:** The briefing accounts for 100% of ingested filings; expanding *Routine* reveals the complete audit trail so nothing is silently discarded.
- **Deterministic Financial Arithmetic:**
  - Volume baseline calculated from prior 20 completed trading sessions (strictly > 2.0x, excluding current session).
  - Price movements strictly > 5.0% evaluated without attributing speculative causation to coincident news.
  - Operating margin comparisons evaluated strictly as percentage point deltas (`pp_delta`).
  - Non-positive prior baselines (losses) handled with descriptive text ("loss narrowed/widened"), not misleading percent growth.
  - Banking sector EBITDA explicitly suppressed with sector caveats.
  - Derived Q4 financial facts cite both operands (`FY - 9M`).
- **Evidence-Gated Guidance Ledger:**
  - Extracts forward guidance (metric, bounds, speaker, period) from official earnings call transcripts.
  - Evaluates actual outcomes (*Met*, *Exceeded*, *Missed*, *Not Due*, *Qualitative Supported*).
  - Future full-year targets protected against premature miss verdicts (`not_due`).
  - Dual-sided evidence inspector displaying verbatim primary source quotes for both sides when verified page spans exist.
  - Official investor links remain available while extraction is pending; link metadata is never presented as a verified financial fact.
- **SSRF-Protected Generic Ingestion & FTS5 Retrieval:**
  - SSRF validator blocking RFC 1918 private ranges, loopback, and cloud metadata endpoints.
  - Generic IR document discovery extracting annual reports and transcripts from official domains.
  - Multi-layout PDF parsing (conversational transcripts & tabular results) stored in SQLite FTS5 for porter-stemmed chunk retrieval.
- **Bounded Question Answering:** Scoped strictly to company primary documents; speculative queries return explicit policy limitations rather than hallucinated answers.
- **Session-Scoped Isolation:** Distinct anonymous browser sessions maintain independent watchlists and alert thresholds via `finn_session_id` cookies.
- **Dual Live & Replay Clock Modes:**
  - `FINN_MODE=live`: Live exchange announcements and EOD bars.
  - `FINN_MODE=replay`: Fixed historical clock (`2024-10-18T23:59:59Z`, Q2 FY25 results season) with visible UI label and offline resilience.

---

## 2. Architecture & Monorepo Structure

```text
├── apps/
│   ├── api/                     # Python 3.12 FastAPI backend
│   │   └── finn/
│   │       ├── adapters/        # Exchange & Price adapters (NSE, BSE, Yahoo EOD)
│   │       ├── alerts/          # Alert rule engine & deduplication
│   │       ├── api/             # REST endpoints (/briefing, /research, /watchlist, /prices)
│   │       ├── db/              # SQLite schema, repository layer, company resolver
│   │       ├── extraction/      # PDF parser, SSRF validator
│   │       ├── finance/         # Fact normalizer, deterministic calculations
│   │       ├── ingestion/       # Announcements sync, generic IR discovery
│   │       ├── jobs/            # Durable SQLite worker queue with atomic leases
│   │       ├── llm/             # Token/cost instrumentation, Pydantic client
│   │       ├── ranking/         # 17-category materiality taxonomy & safety rules
│   │       └── research/        # Guidance ledger engine & primary evidence seeding
│   └── web/                     # React 18 + Vite + TypeScript SPA
│       └── src/
│           ├── components/      # EvidenceDrawer, Shell, Navigation
│           ├── features/        # BriefingScreen, ResearchScreen, WatchlistScreen
│           └── styles/          # Design tokens, responsive layout
├── data/                        # Persistent SQLite WAL database & downloaded PDFs
├── tests/
│   ├── contracts/               # DB migrations, schema, resolver contracts
│   ├── e2e/                     # Playwright mobile 390px E2E workflows
│   ├── fixtures/source/         # Real primary PDF transcripts, tabular results, EOD samples
│   ├── integration/             # Live smoke checks (isolated from unit suite)
│   └── unit/                    # 58 offline unit tests
├── compose.yaml                 # Docker Compose configuration
├── Dockerfile                   # Multi-stage production container
└── docs/                        # Build status ledger & feasibility reports
```

---

## 3. Quickstart & Local Setup

### Prerequisites
- Python 3.12+
- Node.js v20+ / v25+ and npm 10+
- SQLite 3.38+ with FTS5 extension

### Step 1: Install Dependencies & Build Frontend
```bash
# Build React frontend
cd apps/web
npm install
npm run build
cd ../..

# Install Python backend dependencies
pip install -r apps/api/requirements.txt
```

### Step 2: Configure Environment
```bash
cp .env.example .env
```

### Step 3: Run Application
```bash
python -m uvicorn finn.main:app --app-dir apps/api --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in a browser.

---

## 4. Docker Deployment

To build and run the unified container with persistent storage:
```bash
docker compose up --build
```
Access the application at **`http://localhost:8000`**.

---

## 5. Running the Automated Test Suite

### Full Workspace Regression
```bash
python -m pytest -q
```

### Running Test Subsets
- **Unit Tests (58 tests):**
  ```bash
  python -m unittest discover -s tests/unit
  ```
- **Contract Tests (9 tests):**
  ```bash
  python -m unittest discover -s tests/contracts
  ```
- **Mobile Playwright E2E Tests (3 tests):**
  ```bash
  # Ensure browser binary is installed
  python -m playwright install chromium
  python -m unittest discover -s tests/e2e
  ```

---

## 6. Verified Data Sources & Known Limitations

| Source | Status | Implementation Details & Upstream Behavior |
|---|---|---|
| **NSE Announcements** | **Verified Live** | Ingests corporate announcements with attachment URLs via session cookies. |
| **BSE Announcements** | **Documented Limitation** | Returns HTTP 403 (Cloudflare bot protection). Gracefully logged as a known limitation; NSE is primary filing exchange. |
| **Yahoo Finance EOD** | **Verified Live** | Daily price/volume bars with split/dividend adjustment history. |
| **Primary IR Documents** | **Source catalog active** | Official issuer links are registered for INFY, HCLTECH, TCS, and RELIANCE. Page facts and guidance appear only after extraction produces inspectable evidence spans. |

## Public mobile deployment

The repository includes a Render Blueprint in `render.yaml`. Open the link below, connect the GitHub repository, and Render will build the Docker image and provide a normal HTTPS `onrender.com` address with no tunnel password or IP prompt:

[Deploy FINN on Render](https://render.com/deploy?repo=https://github.com/WaqarMoid/finn-investment-agent)

Render's free web-service filesystem is ephemeral and may spin down after inactivity. FINN recreates its database, official source catalog, and current NSE feed at startup. Use a paid persistent disk or managed database if watchlists must survive service replacement.

---

## 7. AI Build History & Planning Records

- **Architecture & Planning Conversation (ChatGPT):** [https://chatgpt.com/s/cx_6ae2e567879881919375559c9eedc46e](https://chatgpt.com/s/cx_6ae2e567879881919375559c9eedc46e)
- **Implementation & Verification Transcript (Antigravity):** [`docs/ai_build_history_transcript.jsonl`](docs/ai_build_history_transcript.jsonl)
- **Packet-by-Packet Build Status Ledger:** [`docs/BUILD_STATUS.md`](docs/BUILD_STATUS.md)
- **Submission Document & Demo Script:** [`SUBMISSION_DRAFT.md`](SUBMISSION_DRAFT.md)
