from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, Dict, Any
from finn.db.database import get_connection
from finn.db.resolver import CompanyResolver

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("")
def search_companies(
    q: str = Query(..., min_length=1, max_length=50, description="Company symbol, ISIN, or name"),
) -> Dict[str, Any]:
    conn = get_connection()
    try:
        resolver = CompanyResolver(conn)
        result = resolver.resolve(q)
        return {"data": result}
    finally:
        conn.close()
