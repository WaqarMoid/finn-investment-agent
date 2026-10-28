"""API router for FINN Research Desk and Management Guidance Ledger.
Provides grounded corporate profiles, 4-quarter ledgers, and bounded Q&A.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends

from finn.db.database import get_connection
from finn.research.engine import ResearchEngine

router = APIRouter(prefix="/research", tags=["Research"])

class ResearchRequest(BaseModel):
    query: str = Field(..., description="NSE symbol, ISIN, or company name")
    as_of: Optional[str] = Field(None, description="Historical as-of date (YYYY-MM-DD)")

class QuestionRequest(BaseModel):
    question: str = Field(..., description="Focused question about management promises, cash flow, or risk")

@router.get("/{query}")
def get_research_report(query: str, as_of: Optional[str] = None) -> Dict[str, Any]:
    conn = get_connection()
    try:
        engine = ResearchEngine(conn)
        report = engine.build_report(query, as_of=as_of)
        if "error" in report and report["error"] == "COMPANY_NOT_FOUND":
            raise HTTPException(status_code=404, detail=report["message"])
        return report
    finally:
        conn.close()

@router.post("")
def create_research_report(payload: ResearchRequest) -> Dict[str, Any]:
    conn = get_connection()
    try:
        engine = ResearchEngine(conn)
        report = engine.build_report(payload.query, as_of=payload.as_of)
        if "error" in report and report["error"] == "COMPANY_NOT_FOUND":
            raise HTTPException(status_code=404, detail=report["message"])
        return report
    finally:
        conn.close()

@router.post("/{query}/ask")
def ask_company_question(query: str, payload: QuestionRequest) -> Dict[str, Any]:
    conn = get_connection()
    try:
        engine = ResearchEngine(conn)
        res = engine.answer_bounded_question(query, payload.question)
        if "error" in res and res["error"] == "COMPANY_NOT_FOUND":
            raise HTTPException(status_code=404, detail=res["message"])
        return res
    finally:
        conn.close()
