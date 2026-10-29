import os, socket, sys, threading, time, unittest
from pathlib import Path
import uvicorn
from playwright.sync_api import sync_playwright

os.environ.setdefault("FINN_EXCHANGE_SOURCE", "fixture")
api_root = str(Path(__file__).resolve().parents[2] / "apps" / "api")
if api_root not in sys.path: sys.path.insert(0, api_root)
from finn.main import app

def find_free_port():
    with socket.socket() as sock: sock.bind(("",0)); return sock.getsockname()[1]

class TestResearchVerticalSlice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port=find_free_port(); cls.url=f"http://127.0.0.1:{cls.port}"
        cls.server=uvicorn.Server(uvicorn.Config(app=app,host="127.0.0.1",port=cls.port,log_level="warning"))
        cls.thread=threading.Thread(target=cls.server.run,daemon=True); cls.thread.start()
        for _ in range(30):
            try:
                with socket.create_connection(("127.0.0.1",cls.port),timeout=.5): break
            except OSError: time.sleep(.1)
    @classmethod
    def tearDownClass(cls): cls.server.should_exit=True; cls.thread.join(timeout=2)

    def test_sources_race_and_honest_empty_states(self):
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True); page=browser.new_page(viewport={"width":390,"height":844})
            page.goto(f"{self.url}/#/research",wait_until="networkidle")
            page.wait_for_selector("text=Infosys Limited")
            self.assertGreaterEqual(page.locator("a:has-text('Open official source')").count(),2)
            page.get_by_role("button",name="TCS",exact=True).click()
            page.wait_for_selector("text=Tata Consultancy Services Limited")
            self.assertNotIn("Infosys Limited",page.locator(".research-screen").inner_text())
            page.get_by_role("button",name="Facts · 3").click()
            self.assertIn("₹267,021 Cr",page.content())
            page.get_by_role("button",name="Guidance · 0").click()
            self.assertIn("No evidence-paired guidance yet",page.content())
            page.locator("#research-question").fill("What changed in management guidance?")
            page.get_by_role("button",name="Ask",exact=True).click()
            page.wait_for_selector("text=FINN cannot answer this")
            self.assertEqual(page.locator("[role=dialog]").count(),0)
            browser.close()

if __name__=="__main__": unittest.main()
