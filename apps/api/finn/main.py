import os
import uuid
from pathlib import Path
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from finn.api.health import router as health_router

app = FastAPI(
    title="FINN Portfolio Briefing API",
    description="Evidence-First Portfolio Briefing & Management Guidance Ledger Engine",
    version="0.1.0",
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

# Static frontend serving
web_dist_path = Path(__file__).resolve().parent.parent.parent / "web" / "dist"

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
