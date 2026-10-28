import sys
import unittest
from decimal import Decimal
from pathlib import Path

# Add apps/api to PYTHONPATH
api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from finn.adapters.price_adapter import YahooPriceAdapter
from finn.finance.calculations import calculate_price_move, calculate_volume_spike

class TestLivePriceSmoke(unittest.TestCase):
    """Separately marked live integration smoke check.
    Exercises real external Yahoo Finance Chart API.
    """
    def test_live_yahoo_eod_smoke(self):
        adapter = YahooPriceAdapter(timeout_seconds=15.0)
        try:
            bars = adapter.fetch_daily_bars("INFY.NS", range_days=90)
        except Exception as e:
            self.skipTest(f"Live network access unavailable or throttled: {e}")
            return

        self.assertGreaterEqual(len(bars), 21, "Expected at least 21 completed daily sessions")
        latest = bars[-1]
        self.assertIsInstance(latest.close, Decimal)
        self.assertGreater(latest.close, Decimal("0"))
        self.assertGreater(latest.volume, 0)

        # Check calculation runs on live data without error
        move = calculate_price_move(bars)
        self.assertIn(move["status"], ["ok", "invalid_baseline"])

        spike = calculate_volume_spike(bars)
        self.assertIn(spike["status"], ["ok", "insufficient_history"])

if __name__ == "__main__":
    unittest.main()
