import os
from fastapi import APIRouter, HTTPException, Query, Request, status
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timezone, timedelta
from pathlib import Path

from finn.db.database import get_connection
from finn.db.repository import DataRepository
from finn.ingestion.announcements import AnnouncementIngestionService
from finn.adapters.exchange_adapter import FixtureExchangeAdapter, NSEExchangeAdapter

router = APIRouter(tags=["Filings & Ingestion"])


def _resolve_fixture_path() -> Path:
    """Find replay data without assuming a particular checkout/container depth."""
    override = os.getenv("FINN_ANNOUNCEMENTS_FIXTURE")
    if override:
        return Path(override).expanduser().resolve()

    relative = Path("tests") / "fixtures" / "source" / "nse_announcements_sample.json"
    candidates = [Path.cwd() / relative]
    candidates.extend(parent / relative for parent in Path(__file__).resolve().parents)
    return next((candidate for candidate in candidates if candidate.exists()), candidates[0])


FIXTURE_PATH = _resolve_fixture_path()

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
def refresh_sources(
    request: Request,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
) -> Dict[str, Any]:
    session_id = getattr(request.state, "session_id", "default_session")

    # In replay mode, bypass external network polling
    if os.getenv("FINN_MODE", "live").lower() == "replay":
        return {
            "status": "replay_active",
            "message": "FINN is running in historical replay mode (clock fixed at 2024-10-18). Live exchange synchronization is disabled.",
            "mode": "replay"
        }

    today_ist = (datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)).date()
    resolved_end = end_date or today_ist
    resolved_start = start_date or resolved_end
    if resolved_start > resolved_end:
        raise HTTPException(status_code=422, detail="start_date must be on or before end_date")
    if (resolved_end - resolved_start).days > 31:
        raise HTTPException(status_code=422, detail="A refresh window may span at most 32 calendar days")

    now_ts = datetime.now(timezone.utc).timestamp()

    # Rate limiting: max 1 refresh every 10 seconds per session
    refresh_key = f"{session_id}:{resolved_start}:{resolved_end}"
    last_ts = _LAST_REFRESH_MAP.get(refresh_key, 0.0)
    if (now_ts - last_ts) < 10.0:
        remaining = round(10.0 - (now_ts - last_ts), 1)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Refresh rate limit exceeded. Please wait {remaining}s before refreshing again."
        )

    _LAST_REFRESH_MAP[refresh_key] = now_ts

    conn = get_connection()
    try:
        service = AnnouncementIngestionService(conn)
        repo = DataRepository(conn)
        watchlist = repo.get_session_watchlist(session_id)
        if not watchlist:
            repo.seed_default_watchlist_for_session(session_id)
            watchlist = repo.get_session_watchlist(session_id)
        # Fixtures are deterministic replay/test inputs. Their presence in the
        # repository must never silently replace the production exchange feed.
        source = os.getenv("FINN_EXCHANGE_SOURCE", "nse").lower()
        if source == "fixture":
            adapter = FixtureExchangeAdapter(fixture_path=str(FIXTURE_PATH))
        else:
            adapter = NSEExchangeAdapter()

        res = service.ingest(
            adapter,
            start_date=resolved_start.isoformat(),
            end_date=resolved_end.isoformat(),
            allowed_symbols=[item["symbol"] for item in watchlist],
        )
        return {
            "status": res.get("status", "completed"),
            "message": "Exchange synchronization completed",
            "requested_window": {"start_date": resolved_start.isoformat(), "end_date": resolved_end.isoformat()},
            "result": res
        }
    finally:
        conn.close()
