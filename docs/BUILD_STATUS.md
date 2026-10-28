# FINN Build Status & Verification Ledger

**Last Updated:** 2026-10-28T09:29:00Z (Asia/Kolkata: 2026-10-28T14:59:00+05:30)  
**Current Milestone:** Completed T01 -> Proceeding to T02  
**Repository State:** Scaffolding complete; React 18 / Vite 5 frontend built; FastAPI backend operational; Playwright mobile E2E tests at 390px passing; Docker / Compose configured.

---

## 1. Work Packet History

| Packet | Description | Status | Completion Date (UTC) | Verification Gate Summary |
|---|---|---|---|---|
| **T00** | Source feasibility and runtime spike | **COMPLETED** | 2026-10-28T09:18:00Z | 3/3 source classes verified with real network calls; 3 fixtures saved; primary PDF downloaded and text extracted; hosting evaluated; gate passed. |
| **T01** | Repo, shell and first deployment | **COMPLETED** | 2026-10-28T09:29:00Z | React/TS frontend (Vite), FastAPI API, lockfiles, `.env.example`, Dockerfile/Compose, unit tests, Playwright 390px mobile navigation shell, deep-link reload passing. |
| **T02** | Database, identity and evidence backbone | *NEXT* | Pending | Migrations, company resolver, 18 candidate holdings, session watchlist, FTS5 schema. |
| **T03** | Price adapter and deterministic calculations | *Queued* | Pending | EOD daily-bar adapter, volume baseline, price move delta, zero/missing handling. |
| **T04** | Exchange ingestion and reliable jobs | *Queued* | Pending | NSE announcement adapter, attachment jobs, deduplication, worker leases. |
| **T05** | Materiality and alerts | *Queued* | Pending | 17-category taxonomy, ranking tiers, safety overrides, session rules, preview. |
| **T06** | Complete briefing vertical slice | *Queued* | Pending | Briefing UI, 24h/7d presets, priority groups, evidence drawer, alert inbox. |
| **T07** | Primary document discovery and parsing | *Queued* | Pending | Generic IR discovery, PDF page extraction, chunking, FTS5 index. |
| **T08** | Structured extraction and financial facts | *Queued* | Pending | Normalized financial facts, deterministic QoQ/YoY, token tracking. |
| **T09** | Guidance ledger and first research report | *Queued* | Pending | 4-quarter ledger, stated vs reported assessment, dual citations. |
| **T10** | Generalization and bounded questions | *Queued* | Pending | 3-5 prepared cases, held-out evaluation on 3 unseen tickers. |
| **T11** | Replay and resilience | *Queued* | Pending | Historical replay clock, failure injection, session isolation. |

---

## 2. Details of Completed Packet: T01

### Changed / Created Files
- `apps/web/package.json` & `apps/web/package-lock.json`: Frontend workspace dependencies (React 18.3.1, Vite 5.4.11, TypeScript 5.6.3).
- `apps/web/tsconfig.json` & `apps/web/vite.config.ts`: TypeScript compiler configuration and Vite build/proxy configuration.
- `apps/web/index.html`: Responsive viewport configuration (`viewport-fit=cover`), IBM Plex Sans font linking.
- `apps/web/src/styles/tokens.css`: Shared design tokens (`--canvas`, `--surface`, `--ink`, `--muted`, `--accent`, `--positive`, `--negative`, `--space-*`, `--radius-*`).
- `apps/web/src/styles/layout.css`: Mobile-first shell layout, sticky header, bottom navigation bar (60px height, >=44px touch targets), desktop rail media queries.
- `apps/web/src/features/briefing/BriefingScreen.tsx`: Briefing destination with severity tiers (Needs Attention, Worth a Look, Routine), time presets (24h, 7d, Custom), and labeled synthetic preview fixtures.
- `apps/web/src/features/research/ResearchScreen.tsx`: Research destination featuring the signature 4-quarter Management Guidance Ledger (Stated / Reported / Assessment), search input, and dual evidence inspection triggers.
- `apps/web/src/features/watchlist/WatchlistScreen.tsx`: Session-isolated alert threshold form (Price move %, Volume multiple) and 18-company monitored holdings table.
- `apps/web/src/components/evidence/EvidenceDrawer.tsx`: Accessible evidence drawer sheet with focus trap, Escape key listener, verbatim excerpt quote, PDF page indicator, and primary PDF link.
- `apps/web/src/App.tsx` & `apps/web/src/main.tsx`: Root application shell coordinating hash-based deep links and API readiness detection.
- `apps/api/finn/__init__.py`: API package initialization.
- `apps/api/finn/schemas/health.py`: Pydantic health schema with version, ISO-8601 UTC timestamp, operational mode, and readiness flags.
- `apps/api/finn/api/health.py`: `/api/v1/health/live` and `/api/v1/health/ready` endpoints checking local SQLite accessibility and FTS5 availability.
- `apps/api/finn/main.py`: FastAPI application entrypoint with anonymous session cookie middleware (`finn_session_id`), CORS, `/api/v1` routes, and static SPA serving for `apps/web/dist`.
- `apps/api/requirements.txt` & `apps/api/requirements.lock`: Python dependencies and pinned versions.
- `Dockerfile`: Multi-stage production container build (Stage 1: Node 20 SPA build, Stage 2: Python 3.12 slim runner with curl healthcheck).
- `compose.yaml`: Docker Compose service configuration with persistent `/data` volume.
- `.env.example`: Safe configuration template.
- `.gitignore`: Ignoring build artifacts, node_modules, `data/*.db`, and secrets.
- `package.json`: Monorepo root workspace scripts.
- `README.md`: Architecture overview, local setup, Docker deployment, and testing instructions.
- `tests/unit/test_health.py`: Unit tests for health routes, session cookie isolation, and SPA serving.
- `tests/e2e/test_mobile_shell.py`: Playwright mobile E2E test verifying 390px viewport, navigation touch targets (>=44px), deep-link reload, and Evidence Drawer modal.

### Checks Actually Run & Results

1. **Frontend Typecheck & Build:**
   - Command: `cd apps/web; npm run build`
   - Result: `tsc` typecheck passed with zero errors; Vite built production bundle (`dist/index.html` 0.78 kB, `dist/assets/index-*.css` 4.47 kB, `dist/assets/index-*.js` 167.99 kB in 608ms).
2. **Backend Unit Tests:**
   - Command: `python -m unittest discover -s tests`
   - Result: 4 unit tests passed in 0.076s.
     - `test_health_live`: Status 200, status "ok", version "0.1.0", UTC timestamp present, process alive.
     - `test_health_ready`: Status 200, database accessible, FTS5 extension available.
     - `test_session_cookie_isolation`: Status 200, `finn_session_id` cookie emitted.
     - `test_spa_serving`: Status 200, SPA HTML served at root `/`.
3. **Playwright Mobile E2E Test at 390px Viewport:**
   - Command: `python -m unittest tests/e2e/test_mobile_shell.py`
   - Result: 1 E2E test passed in 5.752s.
     - Viewport set to 390x844 (iPhone standard).
     - Verified zero horizontal overflow (`scrollWidth == clientWidth`).
     - Verified all 3 bottom navigation items have bounding box height >= 44px (WCAG/FINN mobile touch target requirement).
     - Verified navigation to Research tab updates URL to `#/research` and renders Guidance Ledger.
     - Verified clicking "Inspect Dual Evidence" opens Evidence Drawer sheet.
     - Verified drawer closes on close button.
     - Verified direct deep-link reload (`/#/research`) restores the Research destination.

### Unresolved Issues & Known Gaps
- None for T01. All T01 gate criteria are satisfied.

---

## 3. Next Packet: T02 — Database, identity and evidence backbone

**Objective:**
Implement database migrations, SQLite WAL schema, company/security resolver for candidate holdings (including INFY, TCS, HCLTECH, etc.), immutable source document & source page storage, evidence span lookup, and session-scoped watchlist repository.
