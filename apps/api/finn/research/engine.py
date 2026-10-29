"""Evidence-bound research reports built from indexed primary sources."""

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from finn.db.repository import FinnRepository
from finn.db.resolver import CompanyResolver


class ResearchEngine:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.repo = FinnRepository(conn)
        self.resolver = CompanyResolver(conn)

    def resolve_company(self, query: str) -> Optional[Dict[str, Any]]:
        return self.resolver.resolve(query)

    def get_guidance_ledger(self, company_symbol: str) -> List[Dict[str, Any]]:
        """Return only persisted guidance rows with inspectable evidence IDs."""
        rows = self.conn.execute(
            """SELECT gs.*, ga.assessment, ga.explanation,
                      ga.evidence_ids_json AS outcome_evidence
               FROM guidance_statements gs
               LEFT JOIN guidance_assessments ga ON ga.guidance_id = gs.id
               JOIN securities s ON s.company_id = gs.company_id AND s.exchange = 'NSE'
               WHERE s.symbol = ? ORDER BY gs.stated_at_utc DESC""",
            (company_symbol.upper().replace(".NS", ""),),
        ).fetchall()
        ledger: List[Dict[str, Any]] = []
        for row in rows:
            stated_ids = json.loads(row["evidence_ids_json"] or "[]")
            outcome_ids = json.loads(row["outcome_evidence"] or "[]") if row["outcome_evidence"] else []
            if not stated_ids:
                continue
            low, high = row["low_decimal"], row["high_decimal"]
            target = f"{low}–{high} {row['unit']}" if low and high else (row["qualitative_text"] or "Disclosed target")
            ledger.append({
                "target_period": row["target_period"],
                "metric_label": row["metric"].replace("_", " ").title(),
                "stated_summary": target,
                "stated_evidence_id": stated_ids[0],
                "reported_summary": row["explanation"] or "Outcome has not been assessed",
                "reported_evidence_id": outcome_ids[0] if outcome_ids else None,
                "assessment": row["assessment"] or "not_due",
                "explanation": row["explanation"] or "No evidence-backed outcome is indexed yet.",
                "is_revised": bool(row["revises_id"]),
                "original_target": None,
            })
        return ledger

    def get_overview_facts(self, company_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute(
            """SELECT ff.*, json_extract(ff.evidence_ids_json, '$[0]') AS evidence_id
               FROM financial_facts ff
               WHERE ff.company_id = ? AND ff.status IN ('reported', 'restated')
                 AND json_array_length(ff.evidence_ids_json) > 0
               ORDER BY ff.period_end DESC LIMIT 6""",
            (company_id,),
        ).fetchall()
        def display_value(value: str, unit: str) -> str:
            if unit == "percentage":
                return f"{value}%"
            if unit == "crore":
                try:
                    return f"₹{int(value):,} Cr"
                except ValueError:
                    return f"₹{value} Cr"
            return f"{value} {unit}"

        label_overrides = {
            "ebit_margin": "EBIT Margin", "ebitda": "EBITDA",
            "profit_after_tax": "Profit After Tax (PAT)",
        }

        return [{
            "label": label_overrides.get(row["metric_key"], row["metric_key"].replace("_", " ").title()),
            "value": display_value(row["original_value"], row["original_unit"]),
            "growth": row["fiscal_label"],
            "evidence_id": row["evidence_id"],
            "citation_num": index + 1,
            "excerpt": f"Reported {row['metric_key'].replace('_', ' ')} for {row['fiscal_label']}.",
        } for index, row in enumerate(rows)]

    def build_report(self, query: str, as_of: Optional[str] = None) -> Dict[str, Any]:
        resolved = self.resolver.resolve(query)
        if not resolved or resolved.get("status") != "resolved":
            return {"error": "COMPANY_NOT_FOUND", "message": f"No listed company matched query '{query}'."}

        match = resolved["company"]
        company_id = match["id"]
        symbol = match.get("matched_symbol") or match.get("symbol") or query.upper()
        docs = self.repo.list_source_documents_for_company(company_id)
        facts = self.get_overview_facts(company_id)
        ledger = self.get_guidance_ledger(symbol)
        limitations = []
        if not facts:
            limitations.append("No page-level financial facts have been verified and indexed for this company yet.")
        if not ledger:
            limitations.append("No management guidance row is shown because FINN has no statement-and-outcome pair with inspectable evidence.")
        limitations.extend([
            "Linked sources open on the issuer's official investor-relations site; page-level claims appear only after document parsing and verification.",
            "BSE automated retrieval is currently unavailable; exchange monitoring uses NSE disclosures.",
        ])

        return {
            "status": "ready" if docs else "source_gap",
            "company": {
                "id": match["id"], "symbol": symbol, "legal_name": match["legal_name"],
                "isin": match["isin"], "sector": match["sector"],
                "verified_ir_domains": match.get("verified_ir_domains", []),
            },
            "as_of_date": as_of or datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "stages": [
                {"stage": "finding_reports", "label": "Primary sources located", "status": "completed" if docs else "gap"},
                {"stage": "reading_sources", "label": "Page evidence indexed", "status": "completed" if facts else "pending"},
                {"stage": "checking_figures", "label": "Figures verified", "status": "completed" if facts else "pending"},
                {"stage": "preparing_analysis", "label": "Evidence-safe report", "status": "completed"},
            ],
            "overview_facts": facts,
            "guidance_ledger": ledger,
            "source_coverage": [{
                "document_id": d.get("id"),
                "title": f"{match['legal_name']} · {d.get('source_type', '').replace('_', ' ').title()}",
                "source_type": d.get("source_type"), "publisher": d.get("publisher"),
                "published_at_utc": d.get("published_at_utc"), "fiscal_period": d.get("fiscal_period"),
                "page_count": d.get("page_count", 0), "source_url": d.get("source_url"),
                "status": d.get("status"),
            } for d in docs],
            "limitations": limitations,
        }

    def answer_bounded_question(self, query: str, question: str) -> Dict[str, Any]:
        resolved = self.resolver.resolve(query)
        if not resolved or resolved.get("status") != "resolved":
            return {"error": "COMPANY_NOT_FOUND", "message": f"Company '{query}' could not be resolved."}
        company_id = resolved["company"]["id"]
        from finn.retrieval.indexer import FTSIndexer
        hits = FTSIndexer(self.conn).search_chunks(company_id=company_id, query=question, limit=3)
        for hit in hits:
            evidence = self.conn.execute(
                """SELECT es.id, es.excerpt FROM evidence_spans es
                   JOIN source_pages sp ON sp.id = es.page_id
                   WHERE sp.document_id = ? AND sp.pdf_page_1based BETWEEN ? AND ?
                   ORDER BY es.start_offset LIMIT 1""",
                (hit["document_id"], hit["page_start"], hit["page_end"]),
            ).fetchone()
            if evidence:
                return {
                    "question": question, "answer": evidence["excerpt"],
                    "evidence_citations": [{"citation_num": 1, "evidence_id": evidence["id"], "label": f"Primary filing, page {hit['page_start']}"}],
                    "limitation": "Answer is limited to the directly indexed excerpt; open the citation for context.",
                }
            # A parsed primary-source page is itself inspectable evidence. Create
            # a stable span for the best matching sentence instead of returning a
            # made-up chunk citation that the evidence endpoint cannot resolve.
            page = self.conn.execute(
                """SELECT id, text_content FROM source_pages
                   WHERE document_id = ? AND pdf_page_1based = ?""",
                (hit["document_id"], hit["page_start"]),
            ).fetchone()
            if page:
                sentences = [part.strip() for part in page["text_content"].split(".") if part.strip()]
                query_words = [word.lower() for word in question.split() if len(word) > 3]
                excerpt = next((sentence for sentence in sentences if any(word in sentence.lower() for word in query_words)), sentences[0] if sentences else page["text_content"][:500])
                start_offset = max(0, page["text_content"].find(excerpt))
                evidence_id = f"ev-{hit['chunk_id']}"
                self.conn.execute(
                    """INSERT OR REPLACE INTO evidence_spans
                       (id, page_id, start_offset, end_offset, excerpt, bbox_json, verification_state)
                       VALUES (?, ?, ?, ?, ?, NULL, 'verified')""",
                    (evidence_id, page["id"], start_offset, start_offset + len(excerpt), excerpt),
                )
                self.conn.commit()
                return {
                    "question": question, "answer": excerpt,
                    "evidence_citations": [{"citation_num": 1, "evidence_id": evidence_id, "label": f"Primary filing, Page {hit['page_start']}"}],
                    "limitation": "Answer is limited to the directly indexed excerpt; open the citation for context.",
                }
        return {
            "question": question,
            "answer": "FINN cannot answer this from the currently indexed primary-source evidence.",
            "evidence_citations": [],
            "limitation": "A source link may be available, but no verified page excerpt directly answers the question.",
        }
