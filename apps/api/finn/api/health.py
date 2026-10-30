import os
import sqlite3
from fastapi import APIRouter, Response, status
from finn import __version__
from finn.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/live", response_model=HealthResponse)
def get_liveness():
    """Liveness probe: returns OK if the API process is responsive."""
    return HealthResponse(
        status="ok",
        version=__version__,
        mode=os.getenv("FINN_MODE", "live"),
        details={"process": "alive", "git_commit": os.getenv("RENDER_GIT_COMMIT", "unknown")}
    )

@router.get("/ready", response_model=HealthResponse)
def get_readiness(response: Response):
    """Readiness probe: validates local SQLite and data directory availability."""
    data_dir = os.getenv("DATA_DIR", "./data")
    db_path = os.getenv("DATABASE_PATH", os.path.join(data_dir, "finn.db"))
    
    details = {
        "data_dir_exists": os.path.exists(data_dir),
        "database_accessible": False,
        "fts5_available": False,
    }
    
    # Check SQLite connection and FTS5 extension support
    try:
        os.makedirs(data_dir, exist_ok=True)
        conn = sqlite3.connect(db_path, timeout=2.0)
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        details["database_accessible"] = True
        
        # Test FTS5 support
        cursor.execute("CREATE VIRTUAL TABLE IF NOT EXISTS _health_fts USING fts5(dummy);")
        details["fts5_available"] = True
        conn.close()
    except Exception as e:
        details["error"] = str(e)
    
    is_ready = details["database_accessible"] and details["fts5_available"]
    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(
            status="degraded",
            version=__version__,
            mode=os.getenv("FINN_MODE", "live"),
            details=details
        )
        
    return HealthResponse(
        status="ok",
        version=__version__,
        mode=os.getenv("FINN_MODE", "live"),
        details=details
    )
