import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

UNIT_TO_CRORE_FACTORS = {
    "crore": Decimal("1.0"),
    "cr": Decimal("1.0"),
    "crores": Decimal("1.0"),
    "inr crore": Decimal("1.0"),
    "rs. in crore": Decimal("1.0"),
    "rs in crore": Decimal("1.0"),
    "lakh": Decimal("0.01"),
    "lakhs": Decimal("0.01"),
    "inr lakh": Decimal("0.01"),
    "million": Decimal("0.1"),
    "millions": Decimal("0.1"),
    "inr million": Decimal("0.1"),
    "billion": Decimal("100.0"),
    "billions": Decimal("100.0"),
    "inr billion": Decimal("100.0"),
    "thousand": Decimal("0.0001"),
    "percentage": Decimal("1.0"),
    "%": Decimal("1.0")
}

class FinancialFactModel(BaseModel):
    id: str
    company_id: str
    metric_key: str  # revenue_from_operations, pat, pbt, ebitda, operating_margin
    source_label: str
    value_decimal: Optional[Decimal] = None  # None if unavailable
    original_unit: str
    original_value: str
    currency: str = "INR"
    normalized_unit: str = "crore"
    period_start: str
    period_end: str
    period_type: str  # quarter, half_year, nine_months, annual
    fiscal_label: str  # e.g. Q2_FY27, FY26
    scope: str = "consolidated"  # consolidated, standalone
    status: str = "reported"  # reported, derived, restated, unavailable
    missing_reason: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    derivation_id: Optional[str] = None

def parse_decimal_value(raw_val: str) -> Optional[Decimal]:
    """Parses numeric string including negative parentheses e.g. '(1,234.50)' -> Decimal('-1234.50')."""
    if raw_val is None:
        return None
    cleaned = str(raw_val).strip().replace(",", "").replace(" ", "")
    if not cleaned or cleaned.lower() in ["null", "nil", "na", "n/a", "-", "--"]:
        return None

    is_negative = False
    if cleaned.startswith("(") and cleaned.endswith(")"):
        is_negative = True
        cleaned = cleaned[1:-1]
    elif cleaned.startswith("-"):
        is_negative = True
        cleaned = cleaned[1:]

    try:
        val = Decimal(cleaned)
        return -val if is_negative else val
    except Exception:
        return None

def normalize_to_crore(
    raw_value: str,
    raw_unit: str
) -> Optional[Decimal]:
    dec = parse_decimal_value(raw_value)
    if dec is None:
        return None

    unit_key = raw_unit.strip().lower()
    factor = UNIT_TO_CRORE_FACTORS.get(unit_key)
    if factor is None:
        # Check partial match
        for k, f in UNIT_TO_CRORE_FACTORS.items():
            if k in unit_key:
                factor = f
                break

    if factor is None:
        return dec  # Default no conversion if unit is unknown

    normalized = dec * factor
    return normalized.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
