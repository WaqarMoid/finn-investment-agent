from fastapi import APIRouter, HTTPException, Query, status
from typing import Dict, Any, Optional
from finn.db.database import get_connection
from finn.db.repository import DataRepository
from finn.adapters.price_adapter import FixturePriceAdapter, PriceBar
from finn.finance.calculations import calculate_price_move, calculate_volume_spike
from pathlib import Path

router = APIRouter(prefix="/companies", tags=["Prices"])

FIXTURE_PATH = Path(__file__).resolve().parent.parent.parent.parent / "tests" / "fixtures" / "source" / "infy_eod_sample.json"

@router.get("/{company_id}/prices")
def get_company_prices(
    company_id: str,
    limit: int = Query(default=60, ge=2, le=250),
) -> Dict[str, Any]:
    conn = get_connection()
    try:
        repo = DataRepository(conn)
        sec_row = conn.execute("""
            SELECT id, symbol, price_provider_symbol
            FROM securities
            WHERE company_id = ? AND exchange = 'NSE'
            LIMIT 1
        """, (company_id,)).fetchone()

        if not sec_row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No NSE listing found for company '{company_id}'"
            )

        security_id = sec_row["id"]
        bars = repo.get_price_bars(security_id, limit=limit)

        # If database has no bars yet, load from fixture adapter for demonstration
        if not bars and FIXTURE_PATH.exists():
            adapter = FixturePriceAdapter(fixture_path=str(FIXTURE_PATH))
            fetched = adapter.fetch_daily_bars(sec_row["price_provider_symbol"], range_days=90)
            repo.store_price_bars(security_id, fetched)
            bars = repo.get_price_bars(security_id, limit=limit)

        # Reconstruct PriceBar list for calculations
        bar_objs = [
            PriceBar(
                session_date=b["session_date"],
                open=b["open"],
                high=b["high"],
                low=b["low"],
                close=b["close"],
                adjusted_close=b["adjusted_close"],
                volume=b["volume"],
                provider=b["provider"]
            )
            for b in bars
        ]

        price_move = calculate_price_move(bar_objs) if len(bar_objs) >= 2 else None
        volume_spike = calculate_volume_spike(bar_objs) if len(bar_objs) > 20 else None

        return {
            "data": {
                "company_id": company_id,
                "security_id": security_id,
                "symbol": sec_row["symbol"],
                "bars_count": len(bars),
                "latest_session": bars[-1] if bars else None,
                "price_move": price_move,
                "volume_spike": volume_spike,
                "bars": bars
            },
            "meta": {
                "provider": bars[0]["provider"] if bars else "none",
                "adjustment_policy": "split_and_dividend_adjusted"
            }
        }
    finally:
        conn.close()
