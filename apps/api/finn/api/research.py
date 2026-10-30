"""API router for FINN Research Desk and Management Guidance Ledger.
Provides grounded corporate profiles, 4-quarter ledgers, and bounded Q&A.
"""

import os
import time
import re
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Depends

from finn.db.database import get_connection
from finn.research.engine import ResearchEngine
from finn.ingestion.nse_research import refresh_company_sources, sync_nse_master

router = APIRouter(prefix="/research", tags=["Research"])
_AUTO_ATTEMPTS = {}

class ResearchRequest(BaseModel):
    query: str = Field(..., description="NSE symbol, ISIN, or company name")
    as_of: Optional[str] = Field(None, description="Historical as-of date (YYYY-MM-DD)")

class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=1000, description="Question about the issuer's sources")


def _live_research_enabled():
    return (os.getenv("FINN_MODE", "live").lower() == "live"
            and os.getenv("FINN_EXCHANGE_SOURCE", "fixture").lower() == "nse")


def _prepare(conn, query, force=False):
    engine = ResearchEngine(conn)
    resolved = engine.resolve_company(query)
    if (not resolved or resolved.get("status") != "resolved") and _live_research_enabled():
        try:
            sync_nse_master(conn)
        except Exception:
            pass  # An upstream outage is reported as an unresolved identity.
        resolved = engine.resolve_company(query)
    if not resolved or resolved.get("status") != "resolved":
        raise HTTPException(status_code=404, detail=f"No NSE-listed company matched '{query}'.")
    company = resolved["company"]
    has_pages = conn.execute(
        "SELECT 1 FROM source_documents WHERE company_id = ? AND page_count > 0 LIMIT 1",
        (company["id"],),
    ).fetchone()
    refresh = None
    last_attempt = _AUTO_ATTEMPTS.get(company["id"], 0)
    if _live_research_enabled() and (force or (not has_pages and time.monotonic() - last_attempt > 300)):
        _AUTO_ATTEMPTS[company["id"]] = time.monotonic()
        refresh = refresh_company_sources(conn, company)
    return engine, refresh

@router.get("/{query}")
def get_research_report(query: str, as_of: Optional[str] = None) -> Dict[str, Any]:
    conn = get_connection()
    try:
        engine, refresh = _prepare(conn, query)
        report = engine.build_report(query, as_of=as_of)
        if refresh:
            report["refresh"] = refresh
        if "error" in report and report["error"] == "COMPANY_NOT_FOUND":
            raise HTTPException(status_code=404, detail=report["message"])
        return report
    finally:
        conn.close()

@router.post("")
def create_research_report(payload: ResearchRequest) -> Dict[str, Any]:
    conn = get_connection()
    try:
        engine, refresh = _prepare(conn, payload.query)
        report = engine.build_report(payload.query, as_of=payload.as_of)
        if refresh:
            report["refresh"] = refresh
        if "error" in report and report["error"] == "COMPANY_NOT_FOUND":
            raise HTTPException(status_code=404, detail=report["message"])
        return report
    finally:
        conn.close()

@router.post("/{query}/ask")
def ask_company_question(query: str, payload: QuestionRequest) -> Dict[str, Any]:
    conn = get_connection()
    try:
        engine, _ = _prepare(conn, query)
        if re.search(r"\b(?:compare|versus|vs\.?|against)\b", payload.question, re.I):
            companies = [engine.resolve_company(query)["company"]]
            for token in re.findall(r"\b[A-Za-z][A-Za-z0-9&-]{2,}\b", payload.question):
                match = engine.resolve_company(token)
                if match and match.get("status") == "resolved":
                    company = match["company"]
                    if all(company["id"] != prior["id"] for prior in companies):
                        companies.append(company)
                if len(companies) >= 2:
                    break
            if len(companies) >= 2:
                second = companies[1]
                _prepare(conn, second["symbol"])
                focus = payload.question
                for company in companies:
                    focus = re.sub(rf"\b{re.escape(company['symbol'])}\b", "", focus, flags=re.I)
                focus = re.sub(r"\b(?:compare|versus|vs|against|and)\b", "", focus, flags=re.I).strip()
                answers = [engine.answer_bounded_question(company["symbol"], focus or payload.question)
                           for company in companies]
                if all(answer.get("evidence_citations") for answer in answers):
                    return {"question": payload.question,
                            "answer": "\n\n".join(f"{company['symbol']}: {answer['answer']}"
                                                   for company, answer in zip(companies, answers)),
                            "evidence_citations": [{**citation, "label": f"{company['symbol']} · {citation['label']}"}
                                                   for company, answer in zip(companies, answers)
                                                   for citation in answer["evidence_citations"]],
                            "limitation": "Side-by-side source excerpts; reporting periods and units may differ. No numerical comparison is inferred."}
                return {"question": payload.question,
                        "answer": "Comparable cited evidence is not indexed for both issuers yet.",
                        "evidence_citations": [],
                        "limitation": "Refresh each issuer's NSE filings and try a narrower metric question."}
        res = engine.answer_bounded_question(query, payload.question)
        if "error" in res and res["error"] == "COMPANY_NOT_FOUND":
            raise HTTPException(status_code=404, detail=res["message"])
        return res
    finally:
        conn.close()


@router.post("/{query}/refresh")
def refresh_research(query: str) -> Dict[str, Any]:
    conn = get_connection()
    try:
        engine, refresh = _prepare(conn, query, force=True)
        report = engine.build_report(query)
        report["refresh"] = refresh or {"errors": ["Live NSE retrieval is disabled in this environment."]}
        return report
    finally:
        conn.close()
