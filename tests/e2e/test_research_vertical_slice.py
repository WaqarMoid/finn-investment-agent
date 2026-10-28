import os
import sys
import time
import socket
import threading
import unittest
from pathlib import Path
import uvicorn
from playwright.sync_api import sync_playwright

api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from finn.main import app

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]

class TestResearchVerticalSlice(unittest.TestCase):
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

    def test_research_desk_and_guidance_ledger_flow(self):
        """Exercises complete Research Desk workflow at 390px mobile viewport:
        1. Navigates to Research destination.
        2. Verifies 4-quarter Guidance Ledger rows (Stated / Reported / Assessment).
        3. Opens Evidence Drawer for stated guidance and inspects verified page and excerpt.
        4. Closes Evidence Drawer.
        5. Switches to HCLTECH and verifies guidance ledger.
        6. Asks bounded question and verifies cited grounded response.
        """
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 390, "height": 844})
            page = context.new_page()

            # Navigate to Research tab
            page.goto(f"{self.server_url}/#/research", wait_until="networkidle")
            # If not already on research, click the Research tab in navigation
            research_tab = page.locator("button.nav-item:has-text('Research')")
            if research_tab.count() > 0:
                research_tab.first.click()

            page.wait_for_selector(".research-screen", timeout=6000)

            # Wait for INFY default research report to load
            page.wait_for_selector("text=Infosys Limited", timeout=6000)
            page.wait_for_selector("text=4-Quarter Management Guidance Ledger", timeout=6000)

            # Verify Q1 FY25 through Q4 FY25 periods exist in DOM
            content = page.content()
            self.assertIn("Q1 FY25", content)
            self.assertIn("Q2 FY25", content)
            self.assertIn("Q3 FY25", content)
            self.assertIn("Q4 FY25", content)
            self.assertIn("MET", content)
            self.assertIn("NOT YET DUE", content)

            # Inspect Stated Evidence [1] on Q1 FY25
            inspect_btn = page.locator("button:has-text('Inspect Stated Evidence [1]')").first
            inspect_btn.click()

            # Evidence Drawer should appear with citation and excerpt
            page.wait_for_selector(".evidence-drawer", timeout=5000)
            page.wait_for_selector("text=Exact PDF Page:", timeout=5000)
            drawer_content = page.content()
            self.assertIn("PRIMARY EVIDENCE", drawer_content)
            self.assertIn("Page 4", drawer_content)
            self.assertIn("revenue growth guidance", drawer_content)

            # Close drawer
            close_btn = page.locator(".evidence-drawer button:has-text('Close')").first
            close_btn.click()
            time.sleep(0.3)

            # Switch company to HCLTECH
            hcl_chip = page.locator("button:has-text('HCLTECH')").first
            hcl_chip.click()
            page.wait_for_selector("text=HCL Technologies Limited", timeout=6000)
            hcl_content = page.content()
            self.assertIn("Q1 FY26", hcl_content)
            self.assertIn("MISSED", hcl_content)

            # Ask a bounded question using suggestion chip
            chip_btn = page.locator("button:has-text('What changed in guidance?')").first
            chip_btn.click()

            page.wait_for_selector("text=Q: What changed in guidance?", timeout=5000)
            q_content = page.content()
            self.assertIn("HCL Technologies maintained its services constant currency growth guidance", q_content)

            context.close()
            browser.close()

if __name__ == "__main__":
    unittest.main()
