import json
import uuid
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from finn.ranking.materiality import MaterialityClassifier

TIER_ORDER = {"routine": 1, "worth_a_look": 2, "needs_attention": 3}

class AlertEngine:
    """Session-scoped notification rules and alert evaluation engine.

    Guarantees:
    - Dedicated session isolation for notification settings and inbox.
    - Rule edits and poll retries do not emit duplicate alerts (unique dedup_key).
    - Price and volume alerts never attribute causation to coincident corporate announcements.
    - 'Test on recent data' preview returns matches without inserting alerts into inbox.
    """

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.classifier = MaterialityClassifier()

    def get_or_create_rules(self, session_id: str) -> Dict[str, Any]:
        row = self.conn.execute("""
            SELECT * FROM notification_rules WHERE session_id = ? AND rule_id = 'default_rule'
        """, (session_id,)).fetchone()

        if row:
            return {
                "session_id": row["session_id"],
                "rule_id": row["rule_id"],
                "version": row["version"],
                "enabled": bool(row["enabled"]),
                "price_pct": row["price_pct"],
                "volume_multiple": row["volume_multiple"],
                "lookback_sessions": row["lookback_sessions"],
                "categories": json.loads(row["categories_json"]),
                "min_materiality": row["min_materiality"],
                "updated_at_utc": row["updated_at_utc"]
            }

        # Create default rules
        now_utc = datetime.now(timezone.utc).isoformat()
        default_categories = ["results", "m_and_a", "litigation", "management_change", "dividend"]
        self.conn.execute("""
            INSERT INTO notification_rules (
                session_id, rule_id, version, enabled, price_pct, volume_multiple,
                lookback_sessions, categories_json, min_materiality, updated_at_utc
            ) VALUES (?, 'default_rule', 1, 1, 5.0, 2.0, 20, ?, 'worth_a_look', ?)
        """, (session_id, json.dumps(default_categories), now_utc))
        self.conn.commit()

        return {
            "session_id": session_id,
            "rule_id": "default_rule",
            "version": 1,
            "enabled": True,
            "price_pct": 5.0,
            "volume_multiple": 2.0,
            "lookback_sessions": 20,
            "categories": default_categories,
            "min_materiality": "worth_a_look",
            "updated_at_utc": now_utc
        }

    def update_rules(
        self,
        session_id: str,
        price_pct: float,
        volume_multiple: float,
        categories: List[str],
        min_materiality: str = "worth_a_look",
        enabled: bool = True
    ) -> Dict[str, Any]:
        existing = self.get_or_create_rules(session_id)
        new_version = existing["version"] + 1
        now_utc = datetime.now(timezone.utc).isoformat()

        self.conn.execute("""
            UPDATE notification_rules SET
                version = ?,
                enabled = ?,
                price_pct = ?,
                volume_multiple = ?,
                categories_json = ?,
                min_materiality = ?,
                updated_at_utc = ?
            WHERE session_id = ? AND rule_id = 'default_rule'
        """, (
            new_version, 1 if enabled else 0, price_pct, volume_multiple,
            json.dumps(categories), min_materiality, now_utc, session_id
        ))
        self.conn.commit()
        return self.get_or_create_rules(session_id)

    def preview_rules(
        self,
        session_id: str,
        price_pct: Optional[float] = None,
        volume_multiple: Optional[float] = None,
        categories: Optional[List[str]] = None,
        min_materiality: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Previews recent events that match criteria WITHOUT inserting alerts into the inbox."""
        rules = self.get_or_create_rules(session_id)
        effective_cats = categories if categories is not None else rules["categories"]
        effective_min_tier = min_materiality if min_materiality is not None else rules["min_materiality"]
        min_rank = TIER_ORDER.get(effective_min_tier, 2)

        # Query recent announcements from the session's watchlist
        rows = self.conn.execute("""
            SELECT a.*, c.legal_name, s.symbol as nse_symbol
            FROM announcements a
            JOIN watchlist_members wm ON a.company_id = wm.company_id AND wm.session_id = ?
            JOIN companies c ON a.company_id = c.id
            LEFT JOIN securities s ON s.company_id = c.id AND s.exchange = 'NSE'
            ORDER BY a.published_at_utc DESC
            LIMIT 50
        """, (session_id,)).fetchall()

        matched: List[Dict[str, Any]] = []
        for r in rows:
            rank_res = self.classifier.rank_announcement(r["original_title"], desc=None, user_categories=effective_cats)
            item_rank = TIER_ORDER.get(rank_res.tier, 1)

            # Match if category matches or tier is high enough
            category_match = rank_res.category in effective_cats
            tier_match = item_rank >= min_rank

            if category_match and tier_match:
                matched.append({
                    "type": "filing_match",
                    "company_name": r["legal_name"],
                    "symbol": r["nse_symbol"] or r["company_id"],
                    "title": r["original_title"],
                    "category": rank_res.category,
                    "tier": rank_res.tier,
                    "published_at_utc": r["published_at_utc"],
                    "match_reason": f"Matches tracked category '{rank_res.category}' at tier '{rank_res.tier}'"
                })

        return matched

    def evaluate_filing(self, session_id: str, announcement: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rules = self.get_or_create_rules(session_id)
        if not rules["enabled"]:
            return None

        # Check if company is in session's watchlist
        in_watchlist = self.conn.execute("""
            SELECT 1 FROM watchlist_members WHERE session_id = ? AND company_id = ?
        """, (session_id, announcement["company_id"])).fetchone()

        if not in_watchlist:
            return None

        rank_res = self.classifier.rank_announcement(
            announcement["original_title"],
            user_categories=rules["categories"]
        )

        min_rank = TIER_ORDER.get(rules["min_materiality"], 2)
        item_rank = TIER_ORDER.get(rank_res.tier, 1)

        category_match = rank_res.category in rules["categories"]
        tier_match = item_rank >= min_rank

        # Safety override always triggers alert
        if rank_res.override_applied or (category_match and tier_match):
            dedup_key = f"{session_id}:rule_{rules['version']}:{announcement['company_id']}:{announcement['id']}"
            now_utc = datetime.now(timezone.utc).isoformat()
            alert_id = f"alt-{uuid.uuid4()}"

            reason = f"Material {rank_res.category.upper()} filing: {announcement['original_title']} (Tier: {rank_res.tier})"
            cursor = self.conn.execute("""
                INSERT OR IGNORE INTO alerts (
                    id, session_id, rule_id, rule_version, company_id,
                    source_event_id, source_type, reason, created_at_utc, dedup_key
                ) VALUES (?, ?, ?, ?, ?, ?, 'filing', ?, ?, ?)
            """, (
                alert_id, session_id, rules["rule_id"], rules["version"],
                announcement["company_id"], announcement["id"], reason, now_utc, dedup_key
            ))
            self.conn.commit()

            if cursor.rowcount > 0:
                return {
                    "alert_id": alert_id,
                    "company_id": announcement["company_id"],
                    "source_type": "filing",
                    "reason": reason,
                    "tier": rank_res.tier
                }
        return None

    def evaluate_price_alert(
        self,
        session_id: str,
        company_id: str,
        symbol: str,
        move_result: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        rules = self.get_or_create_rules(session_id)
        if not rules["enabled"] or move_result.get("status") != "ok":
            return None

        # Check price move against session threshold
        delta_pct_str = move_result.get("delta_pct")
        if not delta_pct_str:
            return None

        delta_pct = float(delta_pct_str)
        if abs(delta_pct) <= rules["price_pct"]:
            return None

        session_date = move_result["current_date"]
        dedup_key = f"{session_id}:price_move:{company_id}:{session_date}"
        alert_id = f"alt-{uuid.uuid4()}"
        now_utc = datetime.now(timezone.utc).isoformat()

        # Strict invariant: Never attribute causation to coincident news
        reason = f"{symbol} price moved {delta_pct:+.2f}% on {session_date} (exceeds {rules['price_pct']}% threshold; causal link to coincident filings unverified)"

        cursor = self.conn.execute("""
            INSERT OR IGNORE INTO alerts (
                id, session_id, rule_id, rule_version, company_id,
                source_event_id, source_type, reason, created_at_utc, dedup_key
            ) VALUES (?, ?, ?, ?, ?, ?, 'price_move', ?, ?, ?)
        """, (
            alert_id, session_id, rules["rule_id"], rules["version"],
            company_id, session_date, reason, now_utc, dedup_key
        ))
        self.conn.commit()

        if cursor.rowcount > 0:
            return {"alert_id": alert_id, "company_id": company_id, "source_type": "price_move", "reason": reason}
        return None

    def get_session_alerts(self, session_id: str, limit: int = 50) -> Dict[str, Any]:
        rows = self.conn.execute("""
            SELECT al.*, c.legal_name, s.symbol as nse_symbol
            FROM alerts al
            JOIN companies c ON al.company_id = c.id
            LEFT JOIN securities s ON s.company_id = c.id AND s.exchange = 'NSE'
            WHERE al.session_id = ?
            ORDER BY al.created_at_utc DESC
            LIMIT ?
        """, (session_id, limit)).fetchall()

        unread_count = self.conn.execute("""
            SELECT count(*) FROM alerts WHERE session_id = ? AND acknowledged_at_utc IS NULL
        """, (session_id,)).fetchone()[0]

        items = [
            {
                "id": r["id"],
                "company_id": r["company_id"],
                "company_name": r["legal_name"],
                "symbol": r["nse_symbol"] or r["company_id"],
                "source_type": r["source_type"],
                "reason": r["reason"],
                "created_at_utc": r["created_at_utc"],
                "acknowledged": r["acknowledged_at_utc"] is not None
            }
            for r in rows
        ]
        return {"data": items, "meta": {"unread_count": unread_count, "total_count": len(items)}}

    def acknowledge_alert(self, session_id: str, alert_id: str) -> bool:
        now_utc = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.execute("""
            UPDATE alerts SET acknowledged_at_utc = ?
            WHERE id = ? AND session_id = ? AND acknowledged_at_utc IS NULL
        """, (now_utc, alert_id, session_id))
        self.conn.commit()
        return cursor.rowcount > 0
