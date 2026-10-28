import re
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import httpx
from pydantic import BaseModel, Field

from finn.extraction.url_validator import validate_url_ssrf_safe

class DiscoveredDocument(BaseModel):
    document_type: str  # annual_report | earnings_transcript | quarterly_results
    title: str
    url: str
    fiscal_period: Optional[str] = None
    is_validated_url: bool = False

class DiscoveryResult(BaseModel):
    company_id: str
    symbol: str
    domain: str
    discovered: List[DiscoveredDocument] = Field(default_factory=list)
    missing_classes: List[str] = Field(default_factory=list)
    status: str = "completed"

class GenericIRDiscoveryService:
    """Generic company IR discovery service.

    Discovers primary annual report and transcript links from official company domains.
    Validates discovered links with SSRF checks.
    """

    def __init__(self, timeout_seconds: float = 12.0):
        self.timeout = timeout_seconds

    def discover_from_html(
        self,
        base_url: str,
        html_content: str,
        company_id: str,
        symbol: str
    ) -> DiscoveryResult:
        """Parses HTML and extracts categorized PDF links."""
        soup = BeautifulSoup(html_content, "html.parser")
        discovered: List[DiscoveredDocument] = []
        found_types = set()

        for a in soup.find_all("a", href=True):
            href = a.get("href", "").strip()
            text = a.get_text(" ", strip=True)
            if not href.lower().endswith(".pdf") and ".pdf" not in href.lower():
                continue

            full_url = urljoin(base_url, href)
            is_safe, _ = validate_url_ssrf_safe(full_url)
            if not is_safe:
                continue

            combined = f"{text} {href}".lower()

            doc_type = None
            if "transcript" in combined or "concall" in combined:
                doc_type = "earnings_transcript"
            elif "annual" in combined or "ar-" in combined or "annualreport" in combined:
                doc_type = "annual_report"
            elif "result" in combined or "quarterly" in combined or "press-release" in combined:
                doc_type = "quarterly_results"

            if doc_type:
                found_types.add(doc_type)
                # Try to extract fiscal period e.g. FY24 or Q4
                m = re.search(r"(q[1-4][-_\s]?fy\d{2,4}|fy[-_\s]?\d{2,4})", combined)
                period = m.group(0).upper().replace(" ", "_").replace("-", "_") if m else None

                discovered.append(DiscoveredDocument(
                    document_type=doc_type,
                    title=text or f"{symbol} {doc_type.replace('_', ' ').title()}",
                    url=full_url,
                    fiscal_period=period,
                    is_validated_url=is_safe
                ))

        all_required = ["annual_report", "earnings_transcript"]
        missing = [t for t in all_required if t not in found_types]

        return DiscoveryResult(
            company_id=company_id,
            symbol=symbol,
            domain=base_url,
            discovered=discovered,
            missing_classes=missing,
            status="completed" if not missing else "partial_coverage"
        )
