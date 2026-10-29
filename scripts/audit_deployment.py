"""Read-only browser audit for the deployed FINN prototype.

Usage:
    python scripts/audit_deployment.py https://example.test [output-directory]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from playwright.sync_api import Page, sync_playwright


def visible_text(page: Page) -> str:
    return page.locator("body").inner_text(timeout=10_000)


def safe_click(page: Page, label: str) -> dict[str, Any]:
    locator = page.get_by_role("button", name=label, exact=True)
    result: dict[str, Any] = {"label": label, "count": locator.count()}
    if locator.count():
        locator.first.click()
        page.wait_for_timeout(500)
        result["url"] = page.url
        result["text_excerpt"] = visible_text(page)[:600]
    return result


def audit_viewport(base_url: str, output: Path, width: int, height: int) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": width, "height": height},
            extra_http_headers={"bypass-tunnel-reminder": "true"},
        )
        page = context.new_page()
        console_errors: list[str] = []
        failed_requests: list[str] = []
        api_requests: list[str] = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("requestfailed", lambda req: failed_requests.append(f"{req.method} {req.url}: {req.failure}"))
        page.on("request", lambda req: api_requests.append(f"{req.method} {req.url}") if "/api/" in req.url else None)

        page.goto(base_url, wait_until="domcontentloaded", timeout=30_000)
        page.wait_for_selector(".app-shell", timeout=15_000)
        page.wait_for_timeout(1_000)
        page.screenshot(path=str(output / f"briefing-{width}.png"), full_page=True)

        initial = visible_text(page)
        dimensions = page.evaluate(
            "() => ({scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth})"
        )
        control_results = [safe_click(page, "Last 24h"), safe_click(page, "7 days"), safe_click(page, "Custom")]
        page.screenshot(path=str(output / f"briefing-custom-{width}.png"), full_page=True)

        custom_inputs = page.locator("input[type=date], input[type=datetime-local]").count()

        safe_click(page, "Research")
        page.wait_for_selector(".research-screen", timeout=10_000)
        page.wait_for_timeout(800)
        page.screenshot(path=str(output / f"research-infy-{width}.png"), full_page=True)

        research_results: dict[str, Any] = {}
        for symbol in ("INFY", "HCLTECH", "TCS", "RELIANCE"):
            chip = page.get_by_role("button", name=symbol, exact=True)
            if chip.count():
                chip.first.click()
                page.wait_for_timeout(700)
                body = visible_text(page)
                research_results[symbol] = {
                    "has_company": symbol in body,
                    "sources_text": next((line for line in body.splitlines() if line.startswith("Sources")), None),
                    "no_guidance": "Guidance · 0" in body,
                    "error": next((line for line in body.splitlines() if "unavailable" in line.lower()), None),
                    "body_excerpt": body[:900],
                }

        safe_click(page, "Watchlist")
        page.wait_for_selector(".watchlist-screen", timeout=10_000)
        page.wait_for_timeout(500)
        page.screenshot(path=str(output / f"watchlist-{width}.png"), full_page=True)
        watchlist_text = visible_text(page)

        theme_controls = page.get_by_role("button", name="Use dark theme").count() + page.get_by_role("button", name="Use light theme").count()
        result = {
            "viewport": {"width": width, "height": height},
            "initial_text_excerpt": initial[:1400],
            "dimensions": dimensions,
            "window_controls": control_results,
            "custom_date_inputs": custom_inputs,
            "api_requests": api_requests,
            "research": research_results,
            "watchlist_excerpt": watchlist_text[:1200],
            "theme_toggle_count": theme_controls,
            "console_errors": console_errors,
            "failed_requests": failed_requests,
        }
        context.close()
        browser.close()
        return result


def main() -> None:
    base_url = sys.argv[1] if len(sys.argv) > 1 else "https://finn-briefing-agent.loca.lt"
    output = Path(sys.argv[2] if len(sys.argv) > 2 else "docs/audit-before")
    results = [
        audit_viewport(base_url, output, 390, 844),
        audit_viewport(base_url, output, 1440, 900),
    ]
    report = {"base_url": base_url, "results": results}
    (output / "audit.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
