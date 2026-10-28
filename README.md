# FINN: Evidence-First Portfolio Briefing Engine

FINN is a mobile-first, evidence-linked portfolio briefing and on-demand primary-source research application designed for Indian equity investors.

It addresses three daily investor questions:
1. **What changed?** (Priority-ranked corporate announcements & material price/volume developments).
2. **Why does it matter?** (Concise 30-word implication and materiality classification).
3. **What supports that?** (Direct links to primary sources via an immutable evidence drawer).

The signature research capability is a **Four-Quarter Management Guidance Ledger**, matching stated forward-looking management targets against audited results in deterministic code.

---

## 1. Architecture

```text
apps/web/       -> React 18 + TypeScript + Vite SPA
apps/api/finn/  -> FastAPI Python 3.12 Backend + Lifespan Worker
data/           -> Local SQLite WAL database (with FTS5) + PDF Document Store
tests/          -> Unit, Integration, Contract, and Playwright E2E suites
docs/           -> Build status ledger, feasibility reports, architectural specs
```

- **Unified Single Deployable Container:** FastAPI serves `/api/v1/*` routes and static assets compiled from `apps/web/dist`, with SPA fallback for client-side deep links.
- **Session-Isolated Preferences:** Watchlist holdings and alert thresholds are isolated per anonymous browser session cookie (`finn_session_id`).
- **Primary-Source Grounding:** Research pulls only from verified official IR annual reports and earnings call transcripts; no news summaries or broker notes.

---

## 2. Quickstart

### Prerequisites
- Python 3.12+
- Node.js v20+ / v25+ and npm 10+
- SQLite 3.38+ with FTS5 enabled

### Step 1: Install Dependencies & Build Frontend
```bash
# Install frontend dependencies
cd apps/web
npm install
npm run build
cd ../..

# Install backend dependencies
pip install -r apps/api/requirements.txt
```

### Step 2: Configure Environment
```bash
copy .env.example .env
```

### Step 3: Run the Unified Application
```bash
python -m uvicorn finn.main:app --app-dir apps/api --host 0.0.0.0 --port 8000
```
Open **`http://localhost:8000`** in a browser (or mobile viewport at 390px).

---

## 3. Docker Deployment

Run with Docker Compose:
```bash
docker compose up --build
```
The application will be accessible on port 8000, with SQLite data persisted in the `finn_data` volume mounted at `/data`.

---

## 4. Test Suite

Run unit tests:
```bash
python -m unittest discover tests/unit
```

Run Playwright mobile E2E tests (verifying 390px mobile viewport, navigation, and deep-link reload):
```bash
python -m unittest tests/e2e/test_mobile_shell.py
```

---

## 5. Development Status

See [`docs/BUILD_STATUS.md`](docs/BUILD_STATUS.md) for the live build status ledger and verified milestone gates.
See [`docs/source-feasibility.md`](docs/source-feasibility.md) for the verified data source feasibility spike.
