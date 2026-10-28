import re
import json
import sqlite3
from typing import Optional, Dict, Any, List

class CompanyResolver:
    """Resolves ticker symbols, ISINs, BSE scrip codes, and company aliases

    Guarantees:
    - Normalizes symbol input (.NS, .BO suffixes, whitespace, case).
    - Prioritizes exact NSE symbol / ISIN / BSE code match over fuzzy name search.
    - Resolves renamed/aliased companies without hardcoding narrative responses.
    - Distinguishes exact match, ambiguous choices, and unknown entity.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def resolve(self, query: str) -> Dict[str, Any]:
        cleaned = query.strip()
        if not cleaned:
            return {"status": "unknown", "query": query, "message": "Empty search query"}

        # Strip common exchange suffixes like INFY.NS or INFY.BO
        normalized_sym = re.sub(r"\.(NS|BO|NSE|BSE)$", "", cleaned, flags=re.IGNORECASE).strip().upper()

        # 1. Exact match against NSE/BSE security symbol
        row = self.conn.execute("""
            SELECT c.*, s.exchange, s.symbol as matched_symbol, s.price_provider_symbol
            FROM securities s
            JOIN companies c ON s.company_id = c.id
            WHERE UPPER(s.symbol) = ?
            ORDER BY CASE WHEN s.exchange = 'NSE' THEN 1 ELSE 2 END
            LIMIT 1
        """, (normalized_sym,)).fetchone()

        if row:
            return self._format_resolved(row, match_type="symbol")

        # 2. Exact match against ISIN (e.g. INE009A01021)
        row_isin = self.conn.execute("""
            SELECT c.*, s.exchange, s.symbol as matched_symbol, s.price_provider_symbol
            FROM companies c
            LEFT JOIN securities s ON s.company_id = c.id AND s.exchange = 'NSE'
            WHERE UPPER(c.isin) = ?
            LIMIT 1
        """, (cleaned.upper(),)).fetchone()

        if row_isin:
            return self._format_resolved(row_isin, match_type="isin")

        # 3. Exact match against known aliases
        row_alias = self.conn.execute("""
            SELECT c.*, s.exchange, s.symbol as matched_symbol, s.price_provider_symbol
            FROM company_aliases a
            JOIN companies c ON a.company_id = c.id
            LEFT JOIN securities s ON s.company_id = c.id AND s.exchange = 'NSE'
            WHERE UPPER(a.alias) = ?
            LIMIT 1
        """, (cleaned.upper(),)).fetchone()

        if row_alias:
            return self._format_resolved(row_alias, match_type="alias")

        # 4. Substring / Prefix match against legal name or aliases (ambiguity detection)
        like_pattern = f"%{cleaned.upper()}%"
        candidates = self.conn.execute("""
            SELECT DISTINCT c.id, c.legal_name, c.isin, c.sector, s.symbol as nse_symbol
            FROM companies c
            LEFT JOIN securities s ON s.company_id = c.id AND s.exchange = 'NSE'
            LEFT JOIN company_aliases a ON a.company_id = c.id
            WHERE UPPER(c.legal_name) LIKE ? OR UPPER(a.alias) LIKE ?
            LIMIT 5
        """, (like_pattern, like_pattern)).fetchall()

        if len(candidates) == 1:
            # Single unambiguous substring match
            full_row = self.conn.execute("""
                SELECT c.*, s.exchange, s.symbol as matched_symbol, s.price_provider_symbol
                FROM companies c
                LEFT JOIN securities s ON s.company_id = c.id AND s.exchange = 'NSE'
                WHERE c.id = ?
            """, (candidates[0]["id"],)).fetchone()
            return self._format_resolved(full_row, match_type="fuzzy_single")

        if len(candidates) > 1:
            return {
                "status": "ambiguous",
                "query": query,
                "candidates": [
                    {
                        "id": c["id"],
                        "legal_name": c["legal_name"],
                        "isin": c["isin"],
                        "sector": c["sector"],
                        "symbol": c["nse_symbol"]
                    } for c in candidates
                ]
            }

        return {
            "status": "unknown",
            "query": query,
            "message": f"Company '{query}' not found in securities master"
        }

    def _format_resolved(self, row: sqlite3.Row, match_type: str) -> Dict[str, Any]:
        ir_domains = json.loads(row["verified_ir_domains"]) if row["verified_ir_domains"] else []
        return {
            "status": "resolved",
            "match_type": match_type,
            "company": {
                "id": row["id"],
                "legal_name": row["legal_name"],
                "isin": row["isin"],
                "sector": row["sector"],
                "fiscal_calendar": row["fiscal_calendar"],
                "verified_ir_domains": ir_domains,
                "identity_verified_at": row["identity_verified_at"],
                "symbol": row["matched_symbol"],
                "price_provider_symbol": row["price_provider_symbol"]
            }
        }
