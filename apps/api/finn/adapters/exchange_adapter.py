import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from typing import List, Dict, Any, Optional
import httpx
from pydantic import BaseModel, Field

class AnnouncementRecord(BaseModel):
    exchange: str = Field(..., description="NSE or BSE")
    source_id: str = Field(..., description="Unique announcement ID on exchange")
    symbol: str
    company_name: Optional[str] = None
    isin: Optional[str] = None
    published_at_utc: str
    title: str
    description: Optional[str] = None
    attachment_url: Optional[str] = None
    attachment_size: Optional[str] = None
    has_xbrl: bool = False
    raw_payload: Optional[Dict[str, Any]] = None

class ExchangeAdapter(ABC):
    @abstractmethod
    def fetch_announcements(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_pages: int = 5
    ) -> Dict[str, Any]:
        """Fetch announcement records.

        Returns dictionary:
        {
            "records": List[AnnouncementRecord],
            "pages_completed": int,
            "total_pages_expected": int,
            "status": "completed" | "partial" | "failed",
            "error": Optional[str]
        }
        """
        pass

class FixtureExchangeAdapter(ExchangeAdapter):
    """Offline adapter reading verified NSE announcements fixture for deterministic testing."""
    def __init__(self, fixture_path: Optional[str] = None, fixture_data: Optional[List[Dict[str, Any]]] = None):
        self.fixture_data = fixture_data
        if fixture_path and not fixture_data:
            with open(fixture_path, "r", encoding="utf-8") as f:
                self.fixture_data = json.load(f)

    def fetch_announcements(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_pages: int = 5
    ) -> Dict[str, Any]:
        if not self.fixture_data:
            return {"records": [], "pages_completed": 0, "total_pages_expected": 0, "status": "completed", "error": None}

        records: List[AnnouncementRecord] = []
        start_bound = datetime.fromisoformat(start_date[:10]).date() if start_date else None
        end_bound = datetime.fromisoformat(end_date[:10]).date() if end_date else None
        for item in self.fixture_data:
            # Parse published date: e.g. "28-Oct-2026 14:44:26"
            raw_dt = item.get("an_dt", "")
            try:
                # NSE publishes `an_dt` in Indian Standard Time. Treating it as UTC
                # shifts the filing window by 5h30m around day boundaries.
                dt_obj = datetime.strptime(raw_dt, "%d-%b-%Y %H:%M:%S").replace(
                    tzinfo=ZoneInfo("Asia/Kolkata")
                ).astimezone(timezone.utc)
                dt_utc = dt_obj.isoformat()
            except Exception:
                continue

            published_date = dt_obj.astimezone(ZoneInfo("Asia/Kolkata")).date()
            if start_bound and published_date < start_bound:
                continue
            if end_bound and published_date > end_bound:
                continue

            records.append(AnnouncementRecord(
                exchange="NSE",
                source_id=str(item.get("seq_id") or item.get("dt") or hash(raw_dt + item.get("symbol", ""))),
                symbol=item.get("symbol", "").strip().upper(),
                company_name=item.get("sm_name"),
                isin=item.get("sm_isin"),
                published_at_utc=dt_utc,
                title=item.get("desc") or "Corporate Announcement",
                description=item.get("attchmntText"),
                attachment_url=item.get("attchmntFile"),
                attachment_size=item.get("attFileSize"),
                has_xbrl=bool(item.get("hasXbrl")),
                raw_payload=item
            ))

        return {
            "records": records,
            "pages_completed": 1,
            "total_pages_expected": 1,
            "status": "completed",
            "error": None
        }

class NSEExchangeAdapter(ExchangeAdapter):
    """Live NSE India announcements adapter with session header management."""
    def __init__(self, timeout_seconds: float = 12.0):
        self.timeout = timeout_seconds

    def fetch_announcements(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_pages: int = 3
    ) -> Dict[str, Any]:
        url = "https://www.nseindia.com/api/corporate-announcements"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
        }
        try:
            with httpx.Client(headers=headers, timeout=self.timeout, follow_redirects=True) as client:
                params = {"index": "equities"}
                # NSE expects DD-MM-YYYY. Supplying these parameters is what makes
                # historical 7-day and custom windows return more than the latest feed.
                if start_date:
                    params["from_date"] = datetime.fromisoformat(start_date[:10]).strftime("%d-%m-%Y")
                if end_date:
                    params["to_date"] = datetime.fromisoformat(end_date[:10]).strftime("%d-%m-%Y")
                r = client.get(url, params=params)
                if r.status_code == 403 or r.status_code == 429:
                    return {
                        "records": [],
                        "pages_completed": 0,
                        "total_pages_expected": 1,
                        "status": "partial",
                        "error": f"NSE returned HTTP {r.status_code} (rate limited or session rejected)"
                    }
                if r.status_code != 200:
                    return {
                        "records": [],
                        "pages_completed": 0,
                        "total_pages_expected": 1,
                        "status": "failed",
                        "error": f"NSE returned HTTP {r.status_code}"
                    }
                data = r.json()
                if not isinstance(data, list):
                    return {
                        "records": [],
                        "pages_completed": 0,
                        "total_pages_expected": 1,
                        "status": "failed",
                        "error": f"Expected list response from NSE, got {type(data)}"
                    }
                fixture_adapter = FixtureExchangeAdapter(fixture_data=data)
                return fixture_adapter.fetch_announcements(start_date, end_date, max_pages)
        except Exception as e:
            return {
                "records": [],
                "pages_completed": 0,
                "total_pages_expected": 1,
                "status": "failed",
                "error": str(e)
            }

class BSEExchangeAdapter(ExchangeAdapter):
    """BSE Adapter - Documented limitation per spec: returns HTTP 403 / unverified status."""
    def fetch_announcements(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_pages: int = 1
    ) -> Dict[str, Any]:
        return {
            "records": [],
            "pages_completed": 0,
            "total_pages_expected": 1,
            "status": "partial",
            "error": "BSE automated API is blocked by Cloudflare (HTTP 403). Documented contingency active."
        }
