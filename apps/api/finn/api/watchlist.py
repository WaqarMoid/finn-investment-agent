from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List
from finn.db.database import get_connection
from finn.db.repository import DataRepository

router = APIRouter(prefix="/watchlist", tags=["Watchlist"])

class AddWatchlistRequest(BaseModel):
    company_id: str = Field(..., description="Target company ID to add to watchlist")

@router.get("")
def get_watchlist(request: Request) -> Dict[str, Any]:
    session_id = getattr(request.state, "session_id", "default_session")
    conn = get_connection()
    try:
        repo = DataRepository(conn)
        items = repo.get_session_watchlist(session_id)
        if not items:
            # Seed default 18 companies for newly connected session
            repo.seed_default_watchlist_for_session(session_id)
            items = repo.get_session_watchlist(session_id)
        return {
            "data": items,
            "meta": {"session_id": session_id, "count": len(items)}
        }
    finally:
        conn.close()

@router.post("", status_code=status.HTTP_201_CREATED)
def add_to_watchlist(payload: AddWatchlistRequest, request: Request) -> Dict[str, Any]:
    session_id = getattr(request.state, "session_id", "default_session")
    conn = get_connection()
    try:
        repo = DataRepository(conn)
        success = repo.add_to_watchlist(session_id, payload.company_id)
        if not success:
            return {"status": "already_exists", "message": "Company already in watchlist"}
        return {"status": "added", "company_id": payload.company_id}
    finally:
        conn.close()

@router.delete("/{company_id}")
def remove_from_watchlist(company_id: str, request: Request) -> Dict[str, Any]:
    session_id = getattr(request.state, "session_id", "default_session")
    conn = get_connection()
    try:
        repo = DataRepository(conn)
        removed = repo.remove_from_watchlist(session_id, company_id)
        return {"status": "removed" if removed else "not_found", "company_id": company_id}
    finally:
        conn.close()
