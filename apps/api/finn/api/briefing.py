import os
import json
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException, Query, Request, status
from typing import Dict, Any, List, Optional
from finn.db.database import get_connection
from finn.db.repository import DataRepository

router = APIRouter(prefix="/briefing", tags=["Briefing"])

@router.get("")
def get_briefing(
    request: Request,
    start: Optional[str] = Query(None, description="ISO UTC start timestamp"),
    end: Optional[str] = Query(None, description="ISO UTC end timestamp"),
    cursor: Optional[str] = Query(None, description="Snapshot pagination cursor")
) -> Dict[str, Any]:
    conn = get_connection()
    try:
        now = datetime.now(timezone.utc)
        now_utc = now.isoformat()

        mode = os.getenv("FINN_MODE", "live").lower()
        is_replay = mode == "replay"

        # In replay mode, fix clock to historical Q2 FY25 cutoff (2024-10-18)
        if is_replay:
            replay_cutoff = "2024-10-18T23:59:59Z"
            if not end:
                end = replay_cutoff
            if not start:
                start = "2024-10-01T00:00:00Z"
        else:
            # Default to last 24 hours if window not provided
            if not end:
                end = now_utc
            if not start:
                start = (now - timedelta(days=1)).isoformat()

        try:
            start_dt = datetime.fromisoformat(start.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(end.replace("Z", "+00:00"))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="start and end must be ISO-8601 timestamps") from exc
        if start_dt > end_dt:
            raise HTTPException(status_code=422, detail="start must be before end")

        session_id = getattr(request.state, "session_id", "default_session")
        repo = DataRepository(conn)
        if not repo.get_session_watchlist(session_id):
            repo.seed_default_watchlist_for_session(session_id)

        event_rows = conn.execute("""
            SELECT eg.*, c.legal_name, s.symbol as nse_symbol,
                   (SELECT count(*) FROM announcements a WHERE a.event_group_id = eg.id) as filings_count,
                   (SELECT a.attachment_url FROM announcements a WHERE a.event_group_id = eg.id AND a.attachment_url IS NOT NULL LIMIT 1) as sample_attachment_url
            FROM event_groups eg
            JOIN companies c ON eg.company_id = c.id
            LEFT JOIN securities s ON s.company_id = c.id AND s.exchange = 'NSE'
            JOIN watchlist_members wm ON wm.company_id = eg.company_id AND wm.session_id = ?
            WHERE EXISTS (
                SELECT 1 FROM announcements wa
                WHERE wa.event_group_id = eg.id
                  AND datetime(wa.published_at_utc) >= datetime(?)
                  AND datetime(wa.published_at_utc) <= datetime(?)
            )
            ORDER BY eg.score DESC, eg.event_date DESC
        """, (session_id, start_dt.isoformat(), end_dt.isoformat())).fetchall()

        # Partition by tier
        needs_attention: List[Dict[str, Any]] = []
        worth_a_look: List[Dict[str, Any]] = []
        routine: List[Dict[str, Any]] = []

        total_filings = 0
        for r in event_rows:
            f_count = r["filings_count"] or 1
            total_filings += f_count
            reasons = json.loads(r["reasons_json"]) if r["reasons_json"] else []

            item = {
                "id": r["id"],
                "company_id": r["company_id"],
                "company_name": r["legal_name"],
                "symbol": r["nse_symbol"] or r["company_id"],
                "event_date": r["event_date"],
                "kind": r["kind"],
                "headline": r["headline"],
                "implication": r["implication"],
                "tier": r["ranked_tier"],
                "score": r["score"],
                "reasons": reasons,
                "filings_count": f_count,
                "attachment_url": r["sample_attachment_url"],
                "created_at_utc": r["created_at_utc"]
            }

            if r["ranked_tier"] == "needs_attention":
                needs_attention.append(item)
            elif r["ranked_tier"] == "worth_a_look":
                worth_a_look.append(item)
            else:
                routine.append(item)

        total_events = len(event_rows)

        # Get latest sync run for coverage metadata
        sync_row = conn.execute("""
            SELECT fetched_at_utc, status, error_message FROM sync_runs
            ORDER BY fetched_at_utc DESC LIMIT 1
        """).fetchone()

        coverage = {
            "requested_window": {"start_utc": start, "end_utc": end},
            "mode": mode,
            "is_replay": is_replay,
            "historical_label": "Historical Replay (Oct 18, 2024 — Q2 FY25 Results Season)" if is_replay else None,
            "last_updated_utc": "2024-10-18T18:00:00Z" if is_replay else (sync_row["fetched_at_utc"] if sync_row else now_utc),
            "source_status": "replay_snapshot" if is_replay else (sync_row["status"] if sync_row else "nominal"),
            "is_partial": False if is_replay else ((sync_row["status"] == "partial") if sync_row else False)
        }

        summary = {
            "needs_attention_count": len(needs_attention),
            "worth_a_look_count": len(worth_a_look),
            "routine_count": len(routine),
            "total_events": total_events,
            "total_source_filings": total_filings
        }

        return {
            "data": {
                "tiers": {
                    "needs_attention": needs_attention,
                    "worth_a_look": worth_a_look,
                    "routine": routine
                },
                "summary": summary
            },
            "meta": coverage
        }
    finally:
        conn.close()

@router.get("/events/{event_id}")
def get_event_detail_briefing(event_id: str) -> Dict[str, Any]:
    return get_event_detail(event_id)

events_router = APIRouter(prefix="/events", tags=["Events"])

@events_router.get("/{event_id}")
def get_event_detail(event_id: str) -> Dict[str, Any]:
    conn = get_connection()
    try:
        eg = conn.execute("""
            SELECT eg.*, c.legal_name, s.symbol as nse_symbol
            FROM event_groups eg
            JOIN companies c ON eg.company_id = c.id
            LEFT JOIN securities s ON s.company_id = c.id AND s.exchange = 'NSE'
            WHERE eg.id = ?
        """, (event_id,)).fetchone()

        if not eg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event '{event_id}' not found"
            )

        # Fetch underlying filings
        filings = conn.execute("""
            SELECT id, exchange, source_id, published_at_utc, original_title, attachment_url, category, subtype, stage
            FROM announcements
            WHERE event_group_id = ?
            ORDER BY published_at_utc DESC
        """, (event_id,)).fetchall()

        return {
            "data": {
                "id": eg["id"],
                "company_id": eg["company_id"],
                "company_name": eg["legal_name"],
                "symbol": eg["nse_symbol"] or eg["company_id"],
                "event_date": eg["event_date"],
                "kind": eg["kind"],
                "headline": eg["headline"],
                "implication": eg["implication"],
                "tier": eg["ranked_tier"],
                "score": eg["score"],
                "reasons": json.loads(eg["reasons_json"]) if eg["reasons_json"] else [],
                "filings": [dict(f) for f in filings]
            }
        }
    finally:
        conn.close()
