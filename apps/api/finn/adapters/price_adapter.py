import json
from abc import ABC, abstractmethod
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel, Field

class PriceBar(BaseModel):
    session_date: str = Field(..., description="ISO Date YYYY-MM-DD")
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    adjusted_close: Optional[Decimal] = None
    volume: int
    action_flags: Optional[str] = None
    provider: str = Field(default="yahoo")
    fetched_at_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    revision: int = 1

class PriceAdapter(ABC):
    @abstractmethod
    def fetch_daily_bars(self, provider_symbol: str, range_days: int = 90) -> List[PriceBar]:
        """Fetch daily completed price bars for the given security symbol."""
        pass

class FixturePriceAdapter(PriceAdapter):
    """Offline adapter reading deterministic fixture JSON for unit tests and local reproduction."""
    def __init__(self, fixture_path: Optional[str] = None, fixture_data: Optional[Dict[str, Any]] = None):
        self.fixture_data = fixture_data
        if fixture_path and not fixture_data:
            with open(fixture_path, "r", encoding="utf-8") as f:
                self.fixture_data = json.load(f)

    def fetch_daily_bars(self, provider_symbol: str, range_days: int = 90) -> List[PriceBar]:
        if not self.fixture_data:
            return []
        
        result = self.fixture_data["chart"]["result"][0]
        timestamps = result.get("timestamp", [])
        quote = result["indicators"]["quote"][0]
        adjclose_list = result.get("indicators", {}).get("adjclose", [{}])[0].get("adjclose", [])

        bars: List[PriceBar] = []
        for i, ts in enumerate(timestamps):
            c = quote["close"][i]
            v = quote["volume"][i]
            if c is None or v is None:
                continue

            dt = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
            adj = Decimal(str(round(adjclose_list[i], 4))) if i < len(adjclose_list) and adjclose_list[i] is not None else None
            
            bars.append(PriceBar(
                session_date=dt,
                open=Decimal(str(round(quote["open"][i], 4))),
                high=Decimal(str(round(quote["high"][i], 4))),
                low=Decimal(str(round(quote["low"][i], 4))),
                close=Decimal(str(round(c, 4))),
                adjusted_close=adj,
                volume=int(v),
                provider="fixture_eod"
            ))
        return bars

class YahooPriceAdapter(PriceAdapter):
    """Live EOD adapter using Yahoo Finance Chart API with strict timeouts and error isolation."""
    def __init__(self, timeout_seconds: float = 12.0):
        self.timeout = timeout_seconds

    def fetch_daily_bars(self, provider_symbol: str, range_days: int = 90) -> List[PriceBar]:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{provider_symbol}?range={range_days}d&interval=1d"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json"
        }
        with httpx.Client(headers=headers, timeout=self.timeout, follow_redirects=True) as client:
            r = client.get(url)
            if r.status_code != 200:
                raise RuntimeError(f"Yahoo Finance returned status {r.status_code}: {r.text[:200]}")
            data = r.json()
            fixture_adapter = FixturePriceAdapter(fixture_data=data)
            return fixture_adapter.fetch_daily_bars(provider_symbol, range_days)
