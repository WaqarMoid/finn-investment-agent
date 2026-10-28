from fastapi import APIRouter, HTTPException, Query, Request, status
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path

from finn.db.database import get_connection
from finn.ingestion.announcements import AnnouncementIngestionService
from finn.adapters.exchange_adapter import FixtureExchangeAdapter, NSEExchangeAdapter

router = APIRouter(tags=["Filings & Ingestion"])

FIXTURE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "tests" / "fixtures" / "source" / "nse_announcements_sample.json"

# In-memory rate limiting tracker: session_id -> last_refresh_timestamp
_LAST_REFRESH_MAP: Dict[str, float] = {}

@router.get("/api/v1/filings")
def get_filings(
    company_id: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
) -> Dict[str, Any]:
    conn = get_connection()
    try:
        where_clauses = ["1=1"]
        params = []

        if company_id:
            where_clauses.append("a.company_id = ?")
            params.append(company_id)
        if category:
            where_clauses.append("a.category = ?")
            params.append(category)

        where_str = " AND ".join(where_clauses)

        # Count total matching
        total_count = conn.execute(
            f"SELECT count(*) FROM announcements a WHERE {where_str}", params
        ).fetchone()[0]

        # Fetch page
        query = f"""
            SELECT a.id, a.company_id, c.legal_name, s.symbol as nse_symbol,
                   a.exchange, a.source_id, a.published_at_utc,
                   a.original_title, a.attachment_url, a.category,
                   a.subtype, a.stage, a.event_group_id
            FROM announcements a
            JOIN companies c ON a.company_id = c.id
            LEFT JOIN securities s ON s.company_id = c.id AND s.exchange = 'NSE'
            WHERE {where_str}
            ORDER BY a.published_at_utc DESC
            LIMIT ? OFFSET ?
        """
        rows = conn.execute(query, params + [limit, offset]).fetchall()

        items = [
            {
                "id": r["id"],
                "company_id": r["company_id"],
                "company_name": r["legal_name"],
                "symbol": r["nse_symbol"] or r["company_id"],
                "exchange": r["exchange"],
                "published_at_utc": r["published_at_utc"],
                "title": r["original_title"],
                "category": r["category"],
                "subtype": r["subtype"],
                "stage": r["stage"],
                "attachment_url": r["attachment_url"],
                "event_group_id": r["event_group_id"]
            }
            for r in rows
        ]

        return {
            "data": items,
            "meta": {
                "total": total_count,
                "limit": limit,
                "offset": offset
            }
        }
    finally:
        conn.close()

@router.post("/api/v1/refresh")
def refresh_sources(request: Request) -> Dict[str, Any]:
    session_id = getattr(request.state, "session_id", "default_session")
    now_ts = datetime.now(timezone.utc).timestamp()

    # Rate limiting: max 1 refresh every 10 seconds per session
    last_ts = _LAST_REFRESH_MAP.get(session_id, 0.0)
    if (now_ts - last_ts) < 10.0:
        remaining = round(10.0 - (now_ts - last_ts), 1)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Refresh rate limit exceeded. Please wait {remaining}s before refreshing again."
        )

    _LAST_REFRESH_MAP[session_id] = now_ts

    conn = get_connection()
    try:
        service = AnnouncementIngestionService(conn)
        # Use fixture adapter if offline / local testing, or live if configured
        if FIXTURE_PATH.exists():
            adapter = FixtureExchangeAdapter(fixture_path=str(FIXTURE_PATH))
        else:
            adapter = NSEExchangeAdapter()

        res = service.ingest(adapter)
        return {
            "status": "success",
            "message": "Ingestion refresh completed",
            "result": res
        }
    finally:
        conn.close()
