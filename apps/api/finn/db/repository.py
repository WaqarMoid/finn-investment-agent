import json
import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from finn.db.seed_data import CANDIDATE_COMPANIES

DEFAULT_PORTFOLIO_COMPANY_IDS = [
    "comp-infy-001", "comp-tcs-002", "comp-hcltech-003", "comp-reliance-004",
    "comp-hdfcbank-005", "comp-icicibank-006", "comp-hul-007", "comp-itc-008",
    "comp-lt-009", "comp-sunpharma-010", "comp-drreddy-011", "comp-maruti-012",
    "comp-titan-013", "comp-ultracem-014", "comp-ntpc-015", "comp-tatasteel-016",
    "comp-persistent-017", "comp-kaynes-018",
]

class DataRepository:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def seed_master_data(self) -> int:
        """Seeds the 22 candidate companies, their exchange securities, and aliases."""
        inserted_count = 0
        for comp in CANDIDATE_COMPANIES:
            # Upsert company
            self.conn.execute("""
                INSERT OR IGNORE INTO companies (
                    id, legal_name, isin, sector, fiscal_calendar,
                    verified_ir_domains, identity_verified_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                comp["id"],
                comp["legal_name"],
                comp["isin"],
                comp.get("sector"),
                comp.get("fiscal_calendar", "APR_MAR"),
                json.dumps(comp.get("verified_ir_domains", [])),
                comp["identity_verified_at"]
            ))

            # Upsert securities
            for sec in comp.get("securities", []):
                sec_id = f"sec-{comp['id']}-{sec['exchange'].lower()}"
                self.conn.execute("""
                    INSERT OR IGNORE INTO securities (
                        id, company_id, exchange, symbol, series,
                        price_provider_symbol, valid_from
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    sec_id,
                    comp["id"],
                    sec["exchange"],
                    sec["symbol"],
                    sec.get("series", "EQ"),
                    sec["price_provider_symbol"],
                    sec.get("valid_from", "1990-01-01")
                ))

            # Upsert aliases
            for alias in comp.get("aliases", []):
                alias_id = f"alias-{comp['id']}-{alias.lower().replace(' ', '')}"
                self.conn.execute("""
                    INSERT OR IGNORE INTO company_aliases (id, company_id, alias)
                    VALUES (?, ?, ?)
                """, (alias_id, comp["id"], alias))

            inserted_count += 1
        self.conn.commit()
        return inserted_count

    # Session Management
    def ensure_session(self, session_id: str) -> None:
        now_utc = datetime.now(timezone.utc).isoformat()
        expires_utc = datetime.fromtimestamp(
            datetime.now(timezone.utc).timestamp() + 30 * 86400,
            tz=timezone.utc
        ).isoformat()
        self.conn.execute("""
            INSERT OR IGNORE INTO sessions (id, created_at_utc, expires_at_utc)
            VALUES (?, ?, ?)
        """, (session_id, now_utc, expires_utc))
        self.conn.commit()

    # Session-Scoped Watchlist
    def get_session_watchlist(self, session_id: str) -> List[Dict[str, Any]]:
        self.ensure_session(session_id)
        rows = self.conn.execute("""
            SELECT c.id, c.legal_name, c.isin, c.sector,
                   s.symbol as nse_symbol, s.price_provider_symbol,
                   wm.added_at_utc
            FROM watchlist_members wm
            JOIN companies c ON wm.company_id = c.id
            LEFT JOIN securities s ON s.company_id = c.id AND s.exchange = 'NSE'
            WHERE wm.session_id = ?
            ORDER BY wm.added_at_utc ASC
        """, (session_id,)).fetchall()

        return [
            {
                "company_id": r["id"],
                "legal_name": r["legal_name"],
                "symbol": r["nse_symbol"] or r["id"],
                "isin": r["isin"],
                "sector": r["sector"],
                "price_provider_symbol": r["price_provider_symbol"],
                "added_at_utc": r["added_at_utc"]
            }
            for r in rows
        ]

    def add_to_watchlist(self, session_id: str, company_id: str) -> bool:
        self.ensure_session(session_id)
        now_utc = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.execute("""
            INSERT OR IGNORE INTO watchlist_members (session_id, company_id, added_at_utc)
            VALUES (?, ?, ?)
        """, (session_id, company_id, now_utc))
        self.conn.commit()
        return cursor.rowcount > 0

    def remove_from_watchlist(self, session_id: str, company_id: str) -> bool:
        cursor = self.conn.execute("""
            DELETE FROM watchlist_members
            WHERE session_id = ? AND company_id = ?
        """, (session_id, company_id))
        self.conn.commit()
        return cursor.rowcount > 0

    def seed_default_watchlist_for_session(self, session_id: str) -> int:
        self.ensure_session(session_id)
        count = 0
        now_utc = datetime.now(timezone.utc).isoformat()
        for company_id in DEFAULT_PORTFOLIO_COMPANY_IDS:
            cursor = self.conn.execute("""
                INSERT OR IGNORE INTO watchlist_members (session_id, company_id, added_at_utc)
                VALUES (?, ?, ?)
            """, (session_id, company_id, now_utc))
            if cursor.rowcount > 0:
                count += 1
        self.conn.commit()
        return count

    # Provenance & Document Storage
    def store_source_document(
        self,
        doc_id: str,
        company_id: str,
        source_type: str,
        publisher: str,
        source_url: str,
        content_hash: str,
        file_size_bytes: int,
        page_count: int,
        published_at_utc: str,
        fiscal_period: Optional[str],
        local_path: Optional[str] = None,
        parser_version: str = "1.0.0",
        status: str = "verified"
    ) -> str:
        now_utc = datetime.now(timezone.utc).isoformat()
        resolved_path = local_path or f"data/filings/{doc_id}.pdf"
        self.conn.execute("""
            INSERT INTO source_documents (
                id, company_id, source_type, publisher, source_url, content_hash,
                file_size_bytes, page_count, published_at_utc, fiscal_period,
                local_path, fetched_at_utc, parser_version, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(content_hash, company_id) DO UPDATE SET
                fetched_at_utc = excluded.fetched_at_utc
        """, (
            doc_id, company_id, source_type, publisher, source_url, content_hash,
            file_size_bytes, page_count, published_at_utc, fiscal_period,
            resolved_path, now_utc, parser_version, status
        ))
        self.conn.commit()
        return doc_id

    def list_source_documents_for_company(self, company_id: str) -> List[Dict[str, Any]]:
        rows = self.conn.execute("""
            SELECT id, company_id, source_type, publisher, source_url,
                   published_at_utc, fiscal_period, page_count, local_path, status
            FROM source_documents
            WHERE company_id = ?
            ORDER BY published_at_utc DESC
        """, (company_id,)).fetchall()
        return [dict(r) for r in rows]

    def store_source_page(
        self,
        page_id: str,
        document_id: str,
        pdf_page_1based: int,
        text_content: str,
        printed_label: Optional[str] = None,
        ocr_flag: int = 0,
        text_hash: Optional[str] = None
    ) -> str:
        calc_hash = text_hash or str(hash(text_content))
        self.conn.execute("""
            INSERT OR REPLACE INTO source_pages (
                id, document_id, pdf_page_1based, printed_label,
                text_content, ocr_flag, text_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            page_id, document_id, pdf_page_1based, printed_label,
            text_content, ocr_flag, calc_hash
        ))
        self.conn.commit()
        return page_id

    def store_evidence_span(
        self,
        span_id: str,
        page_id: str,
        start_offset: int,
        end_offset: int,
        excerpt: str,
        verification_state: str = "verified"
    ) -> str:
        self.conn.execute("""
            INSERT OR REPLACE INTO evidence_spans (
                id, page_id, start_offset, end_offset, excerpt, verification_state
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (span_id, page_id, start_offset, end_offset, excerpt, verification_state))
        self.conn.commit()
        return span_id

    def get_evidence_by_id(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        row = self.conn.execute("""
            SELECT e.id as evidence_id, e.excerpt, e.verification_state,
                   p.pdf_page_1based, p.printed_label, p.ocr_flag,
                   d.id as document_id, d.source_type, d.publisher, d.source_url,
                   d.published_at_utc, d.fiscal_period,
                   c.id as company_id, c.legal_name, c.isin
            FROM evidence_spans e
            JOIN source_pages p ON e.page_id = p.id
            JOIN source_documents d ON p.document_id = d.id
            JOIN companies c ON d.company_id = c.id
            WHERE e.id = ?
        """, (evidence_id,)).fetchone()

        if not row:
            return None

        return {
            "evidence_id": row["evidence_id"],
            "excerpt": row["excerpt"],
            "verification_state": row["verification_state"],
            "pdf_page_1based": row["pdf_page_1based"],
            "printed_label": row["printed_label"],
            "ocr_flag": bool(row["ocr_flag"]),
            "document": {
                "id": row["document_id"],
                "source_type": row["source_type"],
                "publisher": row["publisher"],
                "source_url": row["source_url"],
                "published_at_utc": row["published_at_utc"],
                "fiscal_period": row["fiscal_period"]
            },
            "company": {
                "id": row["company_id"],
                "legal_name": row["legal_name"],
                "isin": row["isin"]
            }
        }

    # Price Bar Persistence
    def store_price_bars(self, security_id: str, bars: List[Any]) -> int:
        count = 0
        now_utc = datetime.now(timezone.utc).isoformat()
        for b in bars:
            bar_id = f"bar-{security_id}-{b.session_date}-{b.revision}"
            self.conn.execute("""
                INSERT OR REPLACE INTO price_bars (
                    id, security_id, provider, session_date,
                    open_price, high_price, low_price, close_price,
                    adjusted_close, volume, action_flags, fetched_at_utc, revision
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bar_id, security_id, b.provider, b.session_date,
                str(b.open), str(b.high), str(b.low), str(b.close),
                str(b.adjusted_close) if b.adjusted_close is not None else None,
                b.volume, b.action_flags, now_utc, b.revision
            ))
            count += 1
        self.conn.commit()
        return count

    def get_price_bars(self, security_id: str, limit: int = 60) -> List[Dict[str, Any]]:
        rows = self.conn.execute("""
            SELECT session_date, open_price, high_price, low_price, close_price,
                   adjusted_close, volume, action_flags, provider, revision
            FROM price_bars
            WHERE security_id = ?
            ORDER BY session_date DESC
            LIMIT ?
        """, (security_id, limit)).fetchall()

        return [
            {
                "session_date": r["session_date"],
                "open": r["open_price"],
                "high": r["high_price"],
                "low": r["low_price"],
                "close": r["close_price"],
                "adjusted_close": r["adjusted_close"],
                "volume": r["volume"],
                "action_flags": r["action_flags"],
                "provider": r["provider"],
                "revision": r["revision"]
            }
            for r in reversed(rows)
        ]

# Alias for backwards compatibility across modules
FinnRepository = DataRepository

