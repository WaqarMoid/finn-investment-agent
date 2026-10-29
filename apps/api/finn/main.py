import os
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from finn.db.database import init_db, get_connection
from finn.db.repository import DataRepository
from finn.api.health import router as health_router
from finn.api.companies import router as companies_router
from finn.api.watchlist import router as watchlist_router
from finn.api.evidence import router as evidence_router
from finn.api.prices import router as prices_router
from finn.api.filings import router as filings_router, FIXTURE_PATH as ANNOUNCEMENTS_FIXTURE_PATH
from finn.api.alerts import router as alerts_router
from finn.api.briefing import router as briefing_router, events_router
from finn.api.research import router as research_router
from finn.research.seed_evidence import seed_verified_research_evidence

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize SQLite WAL database and seed candidate companies master
    init_db()
    conn = get_connection()
    try:
        repo = DataRepository(conn)
        repo.seed_master_data()

        # Replay uses deterministic fixtures. A live NSE request is deliberately
        # opt-in at startup: deployment platforms need the HTTP port to open
        # promptly, and upstream availability must never decide whether FINN boots.
        # Live date-window requests still sync from NSE in the API layer.
        has_events = conn.execute("SELECT count(*) FROM announcements").fetchone()[0]
        if has_events == 0:
            from finn.adapters.exchange_adapter import FixtureExchangeAdapter, NSEExchangeAdapter
            from finn.ingestion.announcements import AnnouncementIngestionService
            service = AnnouncementIngestionService(conn)
            if os.getenv("FINN_MODE", "live").lower() == "replay":
                if ANNOUNCEMENTS_FIXTURE_PATH.exists():
                    service.ingest(FixtureExchangeAdapter(fixture_path=str(ANNOUNCEMENTS_FIXTURE_PATH)))
            elif os.getenv("FINN_STARTUP_SYNC", "false").lower() in {"1", "true", "yes"}:
                today_ist = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).date().isoformat()
                service.ingest(NSEExchangeAdapter(), start_date=today_ist, end_date=today_ist)

        # Seed primary document and verified guidance evidence
        seed_verified_research_evidence(repo)
    finally:
        conn.close()
    yield

app = FastAPI(
    title="FINN Portfolio Briefing API",
    description="Evidence-First Portfolio Briefing & Management Guidance Ledger Engine",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session isolation middleware
@app.middleware("http")
async def session_middleware(request: Request, call_next):
    # Ensure every user session has an isolated anonymous session ID cookie
    session_id = request.cookies.get("finn_session_id")
    is_new = False
    if not session_id:
        session_id = str(uuid.uuid4())
        is_new = True
    
    # Ensure session exists in SQLite sessions table
    now_utc = datetime.now(timezone.utc).isoformat()
    expires_utc = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
    conn = get_connection()
    try:
        conn.execute("INSERT OR IGNORE INTO sessions (id, created_at_utc, expires_at_utc) VALUES (?, ?, ?)", (session_id, now_utc, expires_utc))
        conn.commit()
    finally:
        conn.close()

    # Store session_id on request state for endpoint handlers
    request.state.session_id = session_id
    
    response: Response = await call_next(request)
    if is_new:
        response.set_cookie(
            key="finn_session_id",
            value=session_id,
            httponly=True,
            samesite="lax",
            max_age=30 * 24 * 3600,
        )
    return response

# API v1 routes
app.include_router(health_router, prefix="/api/v1")
app.include_router(companies_router, prefix="/api/v1")
app.include_router(watchlist_router, prefix="/api/v1")
app.include_router(evidence_router, prefix="/api/v1")
app.include_router(prices_router, prefix="/api/v1")
app.include_router(filings_router)
app.include_router(alerts_router)
app.include_router(briefing_router, prefix="/api/v1")
app.include_router(events_router, prefix="/api/v1")
app.include_router(research_router, prefix="/api/v1")

# Static frontend serving. Resolve both the repository layout
# (`apps/web/dist`) and the production image layout (`/app/web/dist`).
def _resolve_web_dist_path() -> Path:
    override = os.getenv("WEB_DIST_PATH")
    if override:
        return Path(override).expanduser().resolve()

    candidates = [Path.cwd() / "web" / "dist", Path.cwd() / "apps" / "web" / "dist"]
    for parent in Path(__file__).resolve().parents:
        candidates.extend((parent / "web" / "dist", parent / "apps" / "web" / "dist"))
    return next((candidate for candidate in candidates if candidate.is_dir()), candidates[0])


web_dist_path = _resolve_web_dist_path()

if web_dist_path.exists():
    # Mount static assets
    assets_path = web_dist_path / "assets"
    if assets_path.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_path)), name="assets")

    # SPA Fallback for all other non-API routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Don't hijack API routes
        if full_path.startswith("api/"):
            return Response(status_code=404)
        
        file_path = web_dist_path / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(web_dist_path / "index.html")
else:
    @app.get("/")
    def index_placeholder():
        return {
            "name": "FINN API",
            "status": "ready",
            "message": "Frontend not yet built. Run 'npm run build' inside apps/web.",
            "health": "/api/v1/health/ready"
        }
