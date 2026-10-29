"""Evidence-bound research reports built from indexed primary sources."""

import json
import re
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
            if not stated_ids or not (stated_evidence := self.repo.get_evidence_by_id(stated_ids[0])):
                continue
            if stated_evidence["company"]["id"] != row["company_id"]:
                continue
            if outcome_ids and not self.repo.get_evidence_by_id(outcome_ids[0]):
                outcome_ids = []
            low, high = row["low_decimal"], row["high_decimal"]
            if low and high:
                value = low if low == high else f"{low}–{high}"
                target = f"{value}%" if row["unit"] == "percentage" else f"{value} {row['unit']}"
            else:
                target = row["qualitative_text"] or "Disclosed target"
            label = {"fcf_to_pat": "FCF / PAT", "ebitda_margin": "EBITDA margin"}.get(
                row["metric"], row["metric"].replace("_", " ").title())
            ledger.append({
                "target_period": row["target_period"],
                "metric_label": label,
                "stated_summary": target,
                "stated_evidence_id": stated_ids[0],
                "reported_summary": row["explanation"] or "Awaiting a comparable reported outcome",
                "reported_evidence_id": outcome_ids[0] if outcome_ids else None,
                "assessment": row["assessment"] or "not_due",
                "explanation": row["explanation"] or "The target period has not been assessed against a reported outcome.",
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
            limitations.append("No management guidance statement with inspectable evidence is indexed for this company yet.")
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
            "modules": None,
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
        """Return an exact primary-source excerpt with a real, inspectable citation.

        This is extractive search, not open-ended synthesis. A question with no
        relevant passage is answered as a coverage gap instead of guessed.
        """
        resolved = self.resolver.resolve(query)
        if not resolved or resolved.get("status") != "resolved":
            return {"error": "COMPANY_NOT_FOUND", "message": f"Company '{query}' could not be resolved."}
        company_id = resolved["company"]["id"]
        raw_tokens = set(re.findall(r"[a-z0-9]+", question.lower()))
        aliases = {"fcf": "cash", "pat": "profit", "turnover": "revenue", "sales": "revenue",
                   "revenues": "revenue", "margins": "margin", "growth": "grow"}
        stop = {"what", "which", "when", "where", "why", "how", "is", "are", "was", "were",
                "the", "a", "an", "of", "for", "in", "on", "to", "with", "and", "or", "does",
                "did", "do", "can", "you", "tell", "me", "about", "company", "management",
                "latest", "across", "quarter", "quarters", "year", "years", "five", "5",
                "fy27", "fy26", "outlook", "guidance", "target", "targets", "statement",
                "statements", "give", "show", "please"}
        topics = {aliases.get(token, token) for token in raw_tokens - stop if len(token) >= 3}
        wants_guidance = bool(raw_tokens & {"guidance", "target", "targets", "outlook", "forecast", "promise"})
        rows = self.conn.execute(
            """SELECT es.id, es.excerpt, sp.pdf_page_1based, sd.publisher, sd.source_type
               FROM evidence_spans es
               JOIN source_pages sp ON sp.id = es.page_id
               JOIN source_documents sd ON sd.id = sp.document_id
               WHERE sd.company_id = ? AND es.verification_state = 'verified'""",
            (company_id,),
        ).fetchall()
        candidates = []
        for row in rows:
            text_tokens = set(re.findall(r"[a-z0-9]+", row["excerpt"].lower()))
            normalized = {aliases.get(token, token) for token in text_tokens}
            overlap = topics & normalized
            if not overlap and not (wants_guidance and not topics and row["source_type"] == "earnings_transcript"):
                continue
            # Prefer transcripts for management guidance, financial snapshots for figures.
            score = len(overlap) * 3 + (2 if wants_guidance and row["source_type"] == "earnings_transcript" else 0)
            candidates.append((score, row))
        if candidates:
            candidates.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
            chosen = candidates[0][1]
            return {
                "question": question,
                "answer": chosen["excerpt"],
                "evidence_citations": [{"citation_num": 1, "evidence_id": chosen["id"],
                                        "label": f"{chosen['publisher']} · Page {chosen['pdf_page_1based']}"}],
                "limitation": "Exact indexed excerpt from an issuer source. Open the citation for context; no broader conclusion is implied.",
            }

        # Generic parsed PDFs may have searchable chunks before explicit evidence
        # spans are extracted. Search their substantive terms and persist the quote.
        from finn.retrieval.indexer import FTSIndexer
        search_terms = [token for token in re.findall(r"[a-z0-9]+", question.lower()) if token not in stop]
        hits = []
        if search_terms:
            try:
                hits = FTSIndexer(self.conn).search_chunks(company_id, " ".join(search_terms), limit=3)
            except sqlite3.OperationalError:
                hits = []
        for hit in hits:
            page = self.conn.execute(
                """SELECT id, text_content FROM source_pages
                   WHERE document_id = ? AND pdf_page_1based = ?""",
                (hit["document_id"], hit["page_start"]),
            ).fetchone()
            if not page:
                continue
            sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", page["text_content"]) if part.strip()]
            excerpt = next((part for part in sentences if any(word in part.lower() for word in search_terms)), "")
            if not excerpt:
                continue
            offset = page["text_content"].find(excerpt)
            evidence_id = f"ev-{hit['chunk_id']}-{hit['page_start']}"
            self.repo.store_evidence_span(evidence_id, page["id"], offset, offset + len(excerpt), excerpt)
            return {
                "question": question, "answer": excerpt,
                "evidence_citations": [{"citation_num": 1, "evidence_id": evidence_id,
                                        "label": f"Primary filing · Page {hit['page_start']}"}],
                "limitation": "Exact indexed excerpt from a primary document; open the citation for context.",
            }
        return {
            "question": question,
            "answer": "FINN cannot answer this from the currently indexed primary-source evidence.",
            "evidence_citations": [],
            "limitation": "No verified page excerpt directly answers the question.",
        }
