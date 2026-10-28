import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path

# Add apps/api to PYTHONPATH
api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from finn.adapters.price_adapter import PriceBar, FixturePriceAdapter
from finn.finance.calculations import (
    calculate_price_move,
    calculate_volume_spike,
    adjust_for_stock_split
)

class TestPriceCalculations(unittest.TestCase):
    def make_bar(self, date: str, close: str, volume: int = 1000) -> PriceBar:
        c = Decimal(close)
        return PriceBar(
            session_date=date,
            open=c,
            high=c,
            low=c,
            close=c,
            volume=volume,
            provider="test_fixture"
        )

    def test_normal_price_move(self):
        bars = [
            self.make_bar("2026-10-26", "100.00"),
            self.make_bar("2026-10-27", "106.50")
        ]
        res = calculate_price_move(bars, threshold_pct=5.0)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["delta_pct"], "6.50")
        self.assertTrue(res["is_alert"])

    def test_strictly_greater_than_5_pct_threshold(self):
        # Move of exactly 5.00%: 100.00 -> 105.00
        bars_exact_5 = [
            self.make_bar("2026-10-26", "100.00"),
            self.make_bar("2026-10-27", "105.00")
        ]
        res_exact = calculate_price_move(bars_exact_5, threshold_pct=5.0)
        self.assertEqual(res_exact["delta_pct"], "5.00")
        # Rule: strictly greater than 5.0%, so exactly 5.00% is NOT an alert
        self.assertFalse(res_exact["is_alert"])

        # Move of 5.01%: 100.00 -> 105.01
        bars_above_5 = [
            self.make_bar("2026-10-26", "100.00"),
            self.make_bar("2026-10-27", "105.01")
        ]
        res_above = calculate_price_move(bars_above_5, threshold_pct=5.0)
        self.assertEqual(res_above["delta_pct"], "5.01")
        self.assertTrue(res_above["is_alert"])

    def test_strictly_greater_than_2x_volume_threshold(self):
        # 20 prior bars of volume 1000 -> mean is 1000.00
        bars = [self.make_bar(f"2026-09-{i+1:02d}", "100.00", volume=1000) for i in range(20)]
        
        # Today's volume = 2000 (exactly 2.00x)
        bars_exact_2x = bars + [self.make_bar("2026-10-01", "100.00", volume=2000)]
        res_exact = calculate_volume_spike(bars_exact_2x, threshold_multiple=2.0)
        self.assertEqual(res_exact["volume_multiple"], "2.00")
        # Rule: strictly greater than 2.0x, so exactly 2.00x is NOT an alert
        self.assertFalse(res_exact["is_alert"])

        # Today's volume = 2010 (2.01x)
        bars_above_2x = bars + [self.make_bar("2026-10-01", "100.00", volume=2010)]
        res_above = calculate_volume_spike(bars_above_2x, threshold_multiple=2.0)
        self.assertEqual(res_above["volume_multiple"], "2.01")
        self.assertTrue(res_above["is_alert"])

    def test_prior_20_sessions_exclusion_of_today(self):
        """Today's massive volume must NOT inflate the 20-day baseline."""
        bars = [self.make_bar(f"2026-09-{i+1:02d}", "100.00", volume=1000) for i in range(20)]
        bars.append(self.make_bar("2026-10-01", "100.00", volume=100000)) # Huge spike today
        
        res = calculate_volume_spike(bars, threshold_multiple=2.0)
        self.assertEqual(res["baseline_mean"], "1000.00")
        self.assertEqual(res["volume_multiple"], "100.00")
        self.assertTrue(res["is_alert"])

    def test_insufficient_history(self):
        # Only 1 bar for price move
        res_price = calculate_price_move([self.make_bar("2026-10-27", "100.00")])
        self.assertEqual(res_price["status"], "insufficient_history")
        self.assertFalse(res_price["is_alert"])

        # Only 19 prior bars for volume spike
        bars_19 = [self.make_bar(f"2026-09-{i+1:02d}", "100.00", volume=1000) for i in range(19)]
        bars_19.append(self.make_bar("2026-10-01", "100.00", volume=5000))
        res_vol = calculate_volume_spike(bars_19)
        self.assertEqual(res_vol["status"], "insufficient_history")
        self.assertFalse(res_vol["is_alert"])

    def test_zero_and_negative_data_cases(self):
        # Previous close is zero
        bars_zero_prev = [
            self.make_bar("2026-10-26", "0.00"),
            self.make_bar("2026-10-27", "105.00")
        ]
        res_zero = calculate_price_move(bars_zero_prev)
        self.assertEqual(res_zero["status"], "invalid_baseline")
        self.assertIsNone(res_zero["delta_pct"])
        self.assertFalse(res_zero["is_alert"])

        # Baseline volume is 0
        bars_zero_vol = [self.make_bar(f"2026-09-{i+1:02d}", "100.00", volume=0) for i in range(20)]
        bars_zero_vol.append(self.make_bar("2026-10-01", "100.00", volume=100))
        res_vol_zero = calculate_volume_spike(bars_zero_vol)
        self.assertEqual(res_vol_zero["status"], "zero_baseline")
        self.assertIsNone(res_vol_zero["volume_multiple"])

    def test_weekend_handling(self):
        """Calendar weekend gap correctly matches Friday session to Monday session."""
        bars_weekend = [
            self.make_bar("2026-10-23", "100.00"), # Friday
            self.make_bar("2026-10-26", "102.50")  # Monday
        ]
        res = calculate_price_move(bars_weekend)
        self.assertEqual(res["previous_date"], "2026-10-23")
        self.assertEqual(res["current_date"], "2026-10-26")
        self.assertEqual(res["delta_pct"], "2.50")

    def test_stock_split_adjustment(self):
        """2:1 stock split on 2026-10-15 halves pre-split price and doubles volume."""
        pre_split = self.make_bar("2026-10-14", "200.00", volume=1000)
        post_split = self.make_bar("2026-10-15", "105.00", volume=2100)
        
        adjusted = adjust_for_stock_split([pre_split, post_split], split_date="2026-10-15", split_ratio=Decimal("2.0"))
        self.assertEqual(adjusted[0].close, Decimal("100.00"))
        self.assertEqual(adjusted[0].volume, 2000)
        self.assertEqual(adjusted[1].close, Decimal("105.00"))

        # Now compute move: 100.00 -> 105.00 is +5.00% (not a false -47.5% crash)
        move = calculate_price_move(adjusted)
        self.assertEqual(move["delta_pct"], "5.00")

    def test_fixture_adapter_parsing(self):
        fixture_path = str(Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures" / "source" / "infy_eod_sample.json")
        adapter = FixturePriceAdapter(fixture_path=fixture_path)
        bars = adapter.fetch_daily_bars("INFY.NS", range_days=90)
        self.assertGreaterEqual(len(bars), 60)
        self.assertIsInstance(bars[-1].close, Decimal)
        self.assertGreater(bars[-1].volume, 0)

if __name__ == "__main__":
    unittest.main()
