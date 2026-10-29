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

class TestMobileShell(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = find_free_port()
        cls.server_url = f"http://127.0.0.1:{cls.port}"
        
        # Start uvicorn server in a daemon thread
        config = uvicorn.Config(app=app, host="127.0.0.1", port=cls.port, log_level="warning")
        cls.server = uvicorn.Server(config)
        cls.thread = threading.Thread(target=cls.server.run, daemon=True)
        cls.thread.start()
        
        # Wait for server to come up
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

    def test_mobile_shell_390px(self):
        """Test mobile viewport at 390px (iPhone standard), navigation and deep-link reload."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 390, "height": 844},
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
            )
            page = context.new_page()

            # 1. Visit root - should serve SPA and redirect to briefing
            page.goto(self.server_url, wait_until="networkidle")
            
            # Check brand logo and title
            brand_title = page.locator(".mobile-brand")
            self.assertIn("FINN", brand_title.inner_text())
            
            # 2. Check no horizontal overflow at 390px
            scroll_width = page.evaluate("() => document.documentElement.scrollWidth")
            client_width = page.evaluate("() => document.documentElement.clientWidth")
            self.assertEqual(scroll_width, client_width, f"Horizontal overflow detected: scrollWidth {scroll_width} > clientWidth {client_width}")

            # 3. Check bottom navigation has 3 destinations
            nav_items = page.locator(".nav-item")
            self.assertEqual(nav_items.count(), 3)
            
            # Verify touch target height >= 44px
            for i in range(nav_items.count()):
                box = nav_items.nth(i).bounding_box()
                self.assertIsNotNone(box)
                self.assertGreaterEqual(box["height"], 44.0, f"Nav item {i} height {box['height']} < 44px touch target requirement")

            # 4. Navigate to Research tab
            research_btn = page.locator("button:has-text('Research')")
            research_btn.click()
            page.wait_for_selector(".research-screen")
            self.assertIn("#/research", page.url)
            self.assertIn("Follow the evidence", page.content())

            # 5. Official source metadata is available for the default company
            page.wait_for_selector("text=Official source library")
            self.assertGreaterEqual(page.locator("a:has-text('Open official source')").count(), 2)

            # 6. Test Direct Deep-Link Reload
            page.goto(f"{self.server_url}/#/research", wait_until="networkidle")
            page.wait_for_selector(".research-screen")
            self.assertTrue(page.locator(".research-screen").is_visible())

            browser.close()

if __name__ == "__main__":
    unittest.main()
