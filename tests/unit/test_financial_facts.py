import os
import sys
import unittest
from decimal import Decimal
from pathlib import Path
from typing import Optional
from pydantic import BaseModel

# Add apps/api to PYTHONPATH
api_root = str(Path(__file__).resolve().parent.parent.parent / "apps" / "api")
if api_root not in sys.path:
    sys.path.insert(0, api_root)

from finn.finance.normalizer import FinancialFactModel, normalize_to_crore, parse_decimal_value
from finn.finance.fact_engine import (
    calculate_growth_delta,
    derive_q4_from_fy_and_9m,
    check_sector_metric
)
from finn.llm.client import LLMClient

class MockFactOutput(BaseModel):
    metric: str
    value: str
    unit: str

class TestFinancialFacts(unittest.TestCase):
    def make_fact(
        self,
        fact_id: str,
        metric: str,
        val: Optional[str],
        unit: str = "crore",
        period_type: str = "quarter",
        fiscal_label: str = "Q2_FY27",
        scope: str = "consolidated"
    ) -> FinancialFactModel:
        dec = Decimal(val) if val is not None else None
        return FinancialFactModel(
            id=fact_id,
            company_id="comp-infy-001",
            metric_key=metric,
            source_label=metric.replace("_", " ").title(),
            value_decimal=dec,
            original_unit=unit,
            original_value=str(val) if val is not None else "",
            period_start="2026-07-01",
            period_end="2026-09-30",
            period_type=period_type,
            fiscal_label=fiscal_label,
            scope=scope,
            status="reported" if val is not None else "unavailable",
            evidence_ids=[f"ev-{fact_id}"]
        )

    def test_unit_normalization_to_crore(self):
        """1 crore = 100 lakh = 10 million = 0.01 billion."""
        self.assertEqual(normalize_to_crore("100.0", "crore"), Decimal("100.00"))
        # 10,000 lakh = 100 crore
        self.assertEqual(normalize_to_crore("10000", "lakh"), Decimal("100.00"))
        # 1,000 million = 100 crore
        self.assertEqual(normalize_to_crore("1000", "million"), Decimal("100.00"))
        # 1 billion = 100 crore
        self.assertEqual(normalize_to_crore("1", "billion"), Decimal("100.00"))
        # Negative in parentheses '(50.0)'
        self.assertEqual(normalize_to_crore("(50.0)", "crore"), Decimal("-50.00"))

    def test_bank_ebitda_stays_unavailable(self):
        """EBITDA is marked inappropriate for banks/financial sector."""
        is_compat_bank, reason_bank = check_sector_metric("Banking & Financials", "ebitda")
        self.assertFalse(is_compat_bank)
        self.assertIn("not a standard or meaningful operating measure for banking", reason_bank)

        # IT company allows EBITDA
        is_compat_it, reason_it = check_sector_metric("Information Technology", "ebitda")
        self.assertTrue(is_compat_it)
        self.assertIsNone(reason_it)

    def test_margin_delta_in_percentage_points(self):
        """Margin difference from 18.00% to 21.00% is +3.00 percentage points, NOT percent growth."""
        prior_margin = self.make_fact("f-m-1", "operating_margin", "18.00", unit="percentage", fiscal_label="Q1_FY27")
        current_margin = self.make_fact("f-m-2", "operating_margin", "21.00", unit="percentage", fiscal_label="Q2_FY27")

        res = calculate_growth_delta(current_margin, prior_margin)
        self.assertEqual(res["status"], "ok")
        self.assertEqual(res["metric_type"], "percentage_points")
        self.assertEqual(res["pp_delta"], "3.00")
        self.assertIsNone(res["percentage_growth"])
        self.assertIn("percentage points", res["explanation"])

    def test_negative_prior_handling_no_broken_percentage(self):
        """Negative prior (loss) produces absolute change with descriptive wording, percentage null."""
        prior_loss = self.make_fact("f-p-1", "pat", "-200.00", fiscal_label="Q1_FY27")
        current_profit = self.make_fact("f-p-2", "pat", "150.00", fiscal_label="Q2_FY27")

        res = calculate_growth_delta(current_profit, prior_loss)
        self.assertEqual(res["status"], "non_positive_prior")
        self.assertEqual(res["delta_value"], "350.00")
        self.assertIsNone(res["percentage_growth"])
        self.assertIn("Loss narrowed", res["reason"])

    def test_q4_derivation_citing_both_operands(self):
        """Derived Q4 = FY minus 9M cites both operand facts and sets status to derived."""
        fy_revenue = self.make_fact("f-rev-fy", "revenue_from_operations", "100000.00", period_type="annual", fiscal_label="FY26")
        m9_revenue = self.make_fact("f-rev-9m", "revenue_from_operations", "74000.00", period_type="nine_months", fiscal_label="9M_FY26")

        q4_fact, deriv_record = derive_q4_from_fy_and_9m(fy_revenue, m9_revenue, derived_id="f-rev-q4-derived")
        self.assertEqual(q4_fact.status, "derived")
        self.assertEqual(q4_fact.value_decimal, Decimal("26000.00"))
        self.assertEqual(q4_fact.period_type, "quarter")
        self.assertIn("f-rev-fy", deriv_record["operand_fact_ids"])
        self.assertIn("f-rev-9m", deriv_record["operand_fact_ids"])
        # Both citations preserved
        self.assertIn("ev-f-rev-fy", q4_fact.evidence_ids)
        self.assertIn("ev-f-rev-9m", q4_fact.evidence_ids)

    def test_missing_data_does_not_become_zero(self):
        """Missing values remain None, not silently converted to zero."""
        missing_fact = self.make_fact("f-missing", "ebitda", None)
        self.assertIsNone(missing_fact.value_decimal)
        self.assertEqual(missing_fact.status, "unavailable")

        valid_fact = self.make_fact("f-valid", "ebitda", "500.00")
        res = calculate_growth_delta(valid_fact, missing_fact)
        self.assertEqual(res["status"], "missing_data")

    def test_llm_client_instrumentation_and_caching(self):
        """LLMClient tracks tokens, cost, latency, and caches repeat calls."""
        client = LLMClient(model_name="gemini-1.5-flash")

        def mock_extractor(prompt, evidence):
            return {"metric": "revenue", "value": "28862.00", "unit": "crore"}

        # First call: executes and calculates cost
        res1 = client.generate_structured(
            task_prompt="Extract revenue",
            response_model=MockFactOutput,
            evidence_blocks=[{"text": "Revenue from operations Rs 28,862 crore"}],
            mock_handler=mock_extractor
        )
        self.assertEqual(res1.status, "success")
        self.assertFalse(res1.usage.cached)
        self.assertGreater(res1.usage.input_tokens, 0)
        self.assertGreater(res1.usage.output_tokens, 0)
        self.assertGreater(res1.usage.estimated_cost_usd, 0.0)

        # Second identical call: hits cache with 0 cost
        res2 = client.generate_structured(
            task_prompt="Extract revenue",
            response_model=MockFactOutput,
            evidence_blocks=[{"text": "Revenue from operations Rs 28,862 crore"}],
            mock_handler=mock_extractor
        )
        self.assertEqual(res2.status, "success")
        self.assertTrue(res2.usage.cached)
        self.assertEqual(res2.usage.estimated_cost_usd, 0.0)

if __name__ == "__main__":
    unittest.main()
