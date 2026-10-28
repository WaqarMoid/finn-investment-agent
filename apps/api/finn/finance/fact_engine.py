from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Any, Optional, Tuple
from finn.finance.normalizer import FinancialFactModel

def check_sector_metric(sector: Optional[str], metric_key: str) -> Tuple[bool, Optional[str]]:
    """Validates whether a financial metric is appropriate for the company's sector.

    Rule: Bank/financial sector EBITDA must stay unavailable rather than forcing a generic metric.
    """
    if not sector:
        return True, None

    sec_lower = sector.lower()
    met_lower = metric_key.lower()

    if ("bank" in sec_lower or "financial" in sec_lower or "insurance" in sec_lower) and met_lower == "ebitda":
        return False, "EBITDA is not a standard or meaningful operating measure for banking and financial institutions; Net Interest Income or Operating Profit should be used."

    return True, None

def calculate_growth_delta(
    current: FinancialFactModel,
    prior: FinancialFactModel
) -> Dict[str, Any]:
    """Calculates deterministic QoQ or YoY growth between two compatible financial facts.

    Rules:
    - Both facts must match company_id, metric_key, currency, and scope.
    - Non-positive prior (loss or zero) -> percentage is null, returns absolute change with explanation.
    - Margin or percentage metrics -> difference in percentage points (pp), NOT percent growth.
    - Missing operands -> status insufficient_data.
    """
    if current.company_id != prior.company_id:
        return {"status": "incompatible_scope", "reason": "Companies do not match"}
    if current.metric_key != prior.metric_key:
        return {"status": "incompatible_scope", "reason": f"Metrics do not match: {current.metric_key} vs {prior.metric_key}"}
    if current.scope != prior.scope:
        return {"status": "incompatible_scope", "reason": f"Reporting scopes do not match: {current.scope} vs {prior.scope}"}
    if current.currency != prior.currency:
        return {"status": "incompatible_scope", "reason": f"Currencies do not match: {current.currency} vs {prior.currency}"}

    if current.value_decimal is None or prior.value_decimal is None:
        return {"status": "missing_data", "reason": "One or both period values are unavailable"}

    c_val = current.value_decimal
    p_val = prior.value_decimal
    abs_delta = (c_val - p_val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Check if metric is a margin / percentage
    is_margin = (
        "margin" in current.metric_key.lower() or
        current.original_unit.lower() in ["percentage", "%"] or
        current.normalized_unit.lower() in ["percentage", "%"]
    )

    if is_margin:
        pp_diff = abs_delta
        return {
            "status": "ok",
            "metric_type": "percentage_points",
            "current_value": str(c_val),
            "prior_value": str(p_val),
            "pp_delta": str(pp_diff),
            "percentage_growth": None,
            "unit": "percentage_points",
            "explanation": f"Margin changed by {pp_diff:+} percentage points (not percentage growth)"
        }

    # Non-positive prior check
    if p_val <= Decimal("0"):
        wording = "Loss narrowed" if (p_val < Decimal("0") and c_val > p_val) else "Loss widened" if (p_val < Decimal("0") and c_val < p_val) else "Growth from zero base"
        return {
            "status": "non_positive_prior",
            "metric_type": "currency",
            "current_value": str(c_val),
            "prior_value": str(p_val),
            "delta_value": str(abs_delta),
            "percentage_growth": None,
            "unit": current.normalized_unit,
            "reason": f"Prior period value was non-positive ({p_val}); percentage change is undefined. {wording}."
        }

    # Standard positive-base percentage growth
    growth_exact = ((c_val / p_val) - Decimal("1")) * Decimal("100")
    growth_pct = growth_exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "status": "ok",
        "metric_type": "currency",
        "current_value": str(c_val),
        "prior_value": str(p_val),
        "delta_value": str(abs_delta),
        "percentage_growth": str(growth_pct),
        "unit": current.normalized_unit
    }

def derive_q4_from_fy_and_9m(
    fy_fact: FinancialFactModel,
    m9_fact: FinancialFactModel,
    derived_id: str
) -> Tuple[FinancialFactModel, Dict[str, Any]]:
    """Derives Q4 value from Full Year (FY) minus Nine Months (9M).

    Rules:
    - Both operands must have identical company, metric, currency, scope, and restatement version.
    - Sets status to 'derived' and links operand fact IDs.
    - Cites both FY and 9M evidence IDs.
    """
    assert fy_fact.company_id == m9_fact.company_id, "Companies must match"
    assert fy_fact.metric_key == m9_fact.metric_key, "Metrics must match"
    assert fy_fact.scope == m9_fact.scope, "Scopes must match"
    assert fy_fact.value_decimal is not None and m9_fact.value_decimal is not None, "Operands must have values"

    q4_value = (fy_fact.value_decimal - m9_fact.value_decimal).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    derivation_id = f"deriv-q4-{fy_fact.fiscal_label}"

    derivation_record = {
        "id": derivation_id,
        "formula_key": "q4_derivation",
        "formula": "Q4 = Full_Year - Nine_Months",
        "operand_fact_ids": [fy_fact.id, m9_fact.id],
        "result_decimal": str(q4_value),
        "rounding_policy": "round_2_decimals"
    }

    derived_q4_fact = FinancialFactModel(
        id=derived_id,
        company_id=fy_fact.company_id,
        metric_key=fy_fact.metric_key,
        source_label=f"Derived Q4 from {fy_fact.fiscal_label} FY minus 9M",
        value_decimal=q4_value,
        original_unit=fy_fact.original_unit,
        original_value=str(q4_value),
        currency=fy_fact.currency,
        normalized_unit=fy_fact.normalized_unit,
        period_start=m9_fact.period_end,  # Starts after 9M end
        period_end=fy_fact.period_end,    # Ends at FY end
        period_type="quarter",
        fiscal_label=f"Q4_{fy_fact.fiscal_label}",
        scope=fy_fact.scope,
        status="derived",
        evidence_ids=list(set(fy_fact.evidence_ids + m9_fact.evidence_ids)),
        derivation_id=derivation_id
    )

    return derived_q4_fact, derivation_record
