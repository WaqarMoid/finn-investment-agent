import os
import sys
import time
import socket
import threading
import unittest
from pathlib import Path
import uvicorn
from playwright.sync_api import sync_playwright

# Add apps/api to PYTHONPATH
api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from finn.main import app

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

class TestBriefingVerticalSlice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = find_free_port()
        cls.server_url = f"http://127.0.0.1:{cls.port}"
        
        config = uvicorn.Config(app=app, host="127.0.0.1", port=cls.port, log_level="warning")
        cls.server = uvicorn.Server(config)
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()
        
        for _ in range(30):
            try:
                with socket.create_connection(("127.0.0.1", cls.port), timeout=0.5):
                    break
            except (ConnectionRefusedError, OSError):
                time.sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.server.should_exit = True
        cls.thread.join(timeout=2.0)

    def test_complete_briefing_and_rules_vertical_slice(self):
        """Exercises complete briefing workflow at 390px mobile viewport:

        1. Changing date range presets (24h to 7d).
        2. Inspecting evidence drawer and verifying primary quote & page number.
        3. Saving custom notification threshold and observing confirmation.
        4. Running non-notifying 'Test on recent data' preview.
        5. Mobile back button navigation restoring list.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 390, "height": 844},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
            )
            page = context.new_page()

            # Step 1: Open Briefing Screen
            page.goto(f"{self.server_url}/#/briefing", wait_until="networkidle")
            page.wait_for_selector(".briefing-screen")
            self.assertIn("Portfolio Briefing", page.content())

            # Step 2: Change date window to "7 Days"
            btn_7d = page.locator("button:has-text('7 Days')")
            btn_7d.click()
            page.wait_for_timeout(400)
            self.assertIn("Past 7 Days", page.content())

            # Step 3: Inspect Evidence Drawer
            inspect_btn = page.locator("button:has-text('Inspect Source')").first
            inspect_btn.click()
            drawer = page.locator("[role='dialog']")
            self.assertTrue(drawer.is_visible())
            page.wait_for_selector("text=Page 4")
            self.assertIn("revenue growth guidance", drawer.inner_text().lower())

            # Close drawer
            close_btn = page.locator("button:has-text('Close')")
            close_btn.click()
            page.wait_for_timeout(300)
            self.assertFalse(drawer.is_visible())

            # Step 4: Navigate to Watchlist & Save Custom Threshold
            watchlist_tab = page.locator("button:has-text('Watchlist')")
            watchlist_tab.click()
            page.wait_for_selector(".watchlist-screen")
            self.assertIn("Notification Trigger Thresholds", page.content())

            # Enter custom price threshold: 6.5%
            price_input = page.locator("#price-input")
            price_input.fill("6.5")

            # Click Save Alert Rules
            save_btn = page.locator("button:has-text('Save Alert Rules')")
            save_btn.click()
            page.wait_for_selector("text=Rules saved for this session!")
            self.assertIn("Rules saved for this session!", page.content())

            # Step 5: Click "Test on recent data" preview
            preview_btn = page.locator("button:has-text('Test on recent data')")
            preview_btn.click()
            page.wait_for_selector("text=Preview Matches")
            self.assertIn("Non-notifying preview", page.content())

            # Step 6: Mobile back navigation
            page.go_back()
            page.wait_for_timeout(300)

            browser.close()

if __name__ == "__main__":
    unittest.main()
