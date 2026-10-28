from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from finn.db.database import get_connection
from finn.db.repository import DataRepository

router = APIRouter(prefix="/evidence", tags=["Evidence"])

@router.get("/{evidence_id}")
def get_evidence(evidence_id: str) -> Dict[str, Any]:
    conn = get_connection()
    try:
        repo = DataRepository(conn)
        item = repo.get_evidence_by_id(evidence_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Evidence span '{evidence_id}' not found"
            )
        return {"data": item}
    finally:
        conn.close()
