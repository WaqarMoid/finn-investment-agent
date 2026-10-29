import os, socket, sys, threading, time, unittest
from pathlib import Path
import uvicorn
from playwright.sync_api import sync_playwright

os.environ.setdefault("FINN_EXCHANGE_SOURCE", "fixture")
api_root = str(Path(__file__).resolve().parents[2] / "apps" / "api")
if api_root not in sys.path: sys.path.insert(0, api_root)
from finn.main import app

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("", 0)); return sock.getsockname()[1]

class TestBriefingVerticalSlice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = find_free_port(); cls.server_url = f"http://127.0.0.1:{cls.port}"
        cls.server = uvicorn.Server(uvicorn.Config(app=app, host="127.0.0.1", port=cls.port, log_level="warning"))
        cls.thread = threading.Thread(target=cls.server.run, daemon=True); cls.thread.start()
        for _ in range(30):
            try:
                with socket.create_connection(("127.0.0.1", cls.port), timeout=.5): break
            except OSError: time.sleep(.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.should_exit = True; cls.thread.join(timeout=2)

    def test_custom_window_theme_and_rules(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.goto(f"{self.server_url}/#/briefing", wait_until="networkidle")
            page.wait_for_selector(".briefing-screen")
            self.assertIn("What changed?", page.content())
            page.get_by_role("button", name="Custom").click()
            self.assertEqual(page.locator("input[type=date]").count(), 2)
            page.locator("#briefing-start").fill("2026-10-22")
            page.locator("#briefing-end").fill("2026-10-29")
            page.get_by_role("button", name="Apply window").click()
            page.wait_for_function("document.body.innerText.includes('source filings')")
            self.assertNotIn("ev-preview-101", page.content())
            page.locator(".icon-button").click()
            self.assertEqual(page.evaluate("document.documentElement.dataset.theme"), "dark")
            self.assertEqual(page.evaluate("document.documentElement.scrollWidth"), 390)
            page.get_by_role("button", name="Watchlist").click()
            page.wait_for_selector(".watchlist-screen")
            page.locator("#price-input").fill("6.5")
            page.get_by_role("button", name="Save Alert Rules").click()
            page.wait_for_selector("text=Rules saved for this session!")
            browser.close()

if __name__ == "__main__": unittest.main()
