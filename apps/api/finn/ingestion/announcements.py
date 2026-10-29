import json
import uuid
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from finn.adapters.exchange_adapter import ExchangeAdapter, AnnouncementRecord
from finn.db.resolver import CompanyResolver
from finn.jobs.worker import JobManager

# Basic rule-based classification dictionary matching 17 reference categories
CATEGORY_KEYWORDS = {
    # Specific communication types must precede broad "results" phrases. An
    # earnings-call transcript often mentions financial results in its title.
    "earnings_call": ["earnings call", "concall", "conference call", "transcript", "analyst meet transcript"],
    "results": ["financial result", "financial results", "quarterly result", "audited result", "unaudited result"],
    "dividend": ["dividend", "interim dividend", "final dividend", "record date for dividend"],
    "investor_meetings": ["investor presentation", "analyst meet", "investor meet", "institutional investor"],
    "management_change": ["resignation", "appointment", "chief executive officer", "chief financial officer", "kmp", "cessation"],
    "m_and_a": ["acquisition", "amalgamation", "merger", "scheme of arrangement", "takeover"],
    "fund_raise": ["preferential issue", "qip", "qualified institutional placement", "rights issue", "debentures"],
    "press_release": ["press release", "media release"],
    "credit_rating": ["credit rating", "rating reaffirmation", "rating downgrade", "rating upgrade", "crisil", "icra", "care"],
    "bonus_split": ["bonus issue", "stock split", "sub-division of shares"],
    "litigation": ["litigation", "order received from tax", "gst notice", "penalty imposed", "dispute"],
    "insider_trading": ["insider trading", "pit regulations", "sast regulations", "trading window"],
    "capex": ["new plant", "capacity expansion", "capital expenditure", "commercial production"],
    "agm_egm": ["annual general meeting", "extraordinary general meeting", "postal ballot notice"],
    "postal_ballot": ["postal ballot"],
    "pledging": ["pledge", "encumbrance", "revocation of pledge"]
}

def classify_title(title: str, desc: Optional[str] = None) -> Dict[str, str]:
    text = f"{title} {desc or ''}".lower()
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in text:
                stage = "completed" if "outcome" in text or "approved" in text else "notice" if "intimation" in text or "notice" in text else "informational"
                return {"category": cat, "subtype": kw, "stage": stage}
    return {"category": "unclassified", "subtype": "general_announcement", "stage": "informational"}

class AnnouncementIngestionService:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.resolver = CompanyResolver(conn)
        self.job_manager = JobManager(conn)

    def ingest(
        self,
        adapter: ExchangeAdapter,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_pages: int = 3,
        allowed_symbols: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        sync_id = f"sync-{uuid.uuid4()}"
        now_utc = datetime.now(timezone.utc).isoformat()
        
        # 1. Fetch from adapter with exception safety
        try:
            result = adapter.fetch_announcements(start_date=start_date, end_date=end_date, max_pages=max_pages)
        except Exception as e:
            result = {
                "records": [],
                "pages_fetched": 0,
                "status": "failed",
                "error": f"Upstream adapter error: {str(e)}"
            }
        records: List[AnnouncementRecord] = result["records"]
        status = result["status"]
        error = result["error"]
        
        inserted_announcements = 0
        duplicate_announcements = 0
        unresolved_companies = 0
        filtered_out = 0
        queued_attachments = 0

        # If adapter failed or returned partial, record sync run and DO NOT advance watermark
        if status != "completed":
            self.conn.execute("""
                INSERT INTO sync_runs (
                    id, adapter, requested_start, requested_end, status,
                    counts_json, error_message, fetched_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sync_id, "exchange_announcements", start_date or "latest", end_date or "latest",
                status, json.dumps({"records_fetched": len(records)}), error, now_utc
            ))
            self.conn.commit()
            return {
                "sync_id": sync_id,
                "status": status,
                "error": error,
                "watermark_advanced": False,
                "records_ingested": 0
            }

        # 2. Process records
        allowed = {symbol.upper() for symbol in allowed_symbols} if allowed_symbols else None
        for rec in records:
            if allowed is not None and rec.symbol.upper() not in allowed:
                filtered_out += 1
                continue
            # Resolve company
            resolve_res = self.resolver.resolve(rec.symbol)
            if resolve_res["status"] != "resolved" and rec.isin:
                resolve_res = self.resolver.resolve(rec.isin)
            
            if resolve_res["status"] != "resolved":
                # Auto-register unmonitored exchange company so announcements are never discarded
                company_id = f"comp-unmonitored-{rec.symbol.lower()}"
                self.conn.execute("""
                    INSERT OR IGNORE INTO companies (
                        id, legal_name, isin, sector, fiscal_calendar, verified_ir_domains, identity_verified_at
                    ) VALUES (?, ?, ?, 'Unclassified', 'APR_MAR', '[]', ?)
                """, (
                    company_id, rec.company_name or rec.symbol, rec.isin or f"INE_UNVERIFIED_{rec.symbol}", now_utc
                ))
                self.conn.execute("""
                    INSERT OR IGNORE INTO securities (
                        id, company_id, exchange, symbol, series, price_provider_symbol, valid_from
                    ) VALUES (?, ?, ?, ?, 'EQ', ?, '2000-01-01')
                """, (
                    f"sec-{company_id}-{rec.exchange.lower()}", company_id, rec.exchange, rec.symbol, f"{rec.symbol}.NS"
                ))
                unresolved_companies += 1
            else:
                company_id = resolve_res["company"]["id"]
            classification = classify_title(rec.title, rec.description)

            # Insert announcement with conflict deduplication
            ann_id = f"ann-{rec.exchange.lower()}-{rec.source_id}"
            cursor = self.conn.execute("""
                INSERT OR IGNORE INTO announcements (
                    id, company_id, exchange, source_id, published_at_utc,
                    fetched_at_utc, original_title, attachment_url, category,
                    subtype, stage, parse_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'parsed')
            """, (
                ann_id, company_id, rec.exchange, rec.source_id, rec.published_at_utc,
                now_utc, rec.title, rec.attachment_url, classification["category"],
                classification["subtype"], classification["stage"]
            ))

            if cursor.rowcount == 0:
                duplicate_announcements += 1
                continue
            
            inserted_announcements += 1

            # If announcement has attachment, enqueue attachment download job
            if rec.attachment_url:
                dedup_key = f"attach-{rec.exchange}-{rec.source_id}"
                self.job_manager.enqueue_job(
                    job_type="download_attachment",
                    dedup_key=dedup_key,
                    company_id=company_id,
                    progress_detail={
                        "announcement_id": ann_id,
                        "url": rec.attachment_url,
                        "file_size": rec.attachment_size
                    }
                )
                queued_attachments += 1

            # Group into event_groups
            event_date = rec.published_at_utc[:10]
            group_id = f"evg-{company_id}-{event_date}-{classification['category']}"
            
            # Simple priority tier rule: results & m_and_a are needs_attention
            tier = "needs_attention" if classification["category"] in ["results", "m_and_a", "litigation"] else \
                   "worth_a_look" if classification["category"] in ["dividend", "management_change", "capex", "credit_rating"] else "routine"
            score = 65.0 if tier == "needs_attention" else 35.0 if tier == "worth_a_look" else 10.0

            self.conn.execute("""
                INSERT INTO event_groups (
                    id, company_id, kind, event_date, headline, implication,
                    ranked_tier, score, reasons_json, rule_version, created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, '1.0', ?)
                ON CONFLICT(id) DO UPDATE SET
                    reasons_json = excluded.reasons_json
            """, (
                group_id, company_id, classification["category"], event_date,
                rec.title, rec.description or rec.title, tier, score,
                json.dumps([f"Category: {classification['category']}", f"Stage: {classification['stage']}"]),
                now_utc
            ))

            # Link announcement to event group
            self.conn.execute("""
                UPDATE announcements SET event_group_id = ? WHERE id = ?
            """, (group_id, ann_id))

        counts = {
            "records_fetched": len(records),
            "inserted_announcements": inserted_announcements,
            "duplicate_announcements": duplicate_announcements,
            "unresolved_companies": unresolved_companies,
            "queued_attachments": queued_attachments,
            "filtered_outside_watchlist": filtered_out,
        }

        # 3. Record successful sync run
        self.conn.execute("""
            INSERT INTO sync_runs (
                id, adapter, requested_start, requested_end, status,
                counts_json, error_message, fetched_at_utc
            ) VALUES (?, ?, ?, ?, 'completed', ?, NULL, ?)
        """, (
            sync_id, "exchange_announcements", start_date or "latest", end_date or "latest",
            json.dumps(counts), now_utc
        ))
        self.conn.commit()

        return {
            "sync_id": sync_id,
            "status": "completed",
            "counts": counts,
            "watermark_advanced": True
        }
