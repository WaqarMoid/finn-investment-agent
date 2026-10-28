from decimal import Decimal
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class GuidanceStatementModel(BaseModel):
    id: str
    company_id: str
    metric: str
    speaker_name: Optional[str] = None
    speaker_role: str  # CEO, CFO
    stated_at_utc: str
    target_period: str  # e.g. FY25, Q1_FY25
    low_decimal: Optional[Decimal] = None
    high_decimal: Optional[Decimal] = None
    unit: str = "percentage"
    currency: str = "INR"
    basis: str = "constant_currency"
    qualitative_text: Optional[str] = None
    conditions: Optional[str] = None
    evidence_id: str
    status: str = "original"  # original, revised, withdrawn
    revises_id: Optional[str] = None

class GuidanceLedgerRow(BaseModel):
    target_period: str
    metric_label: str
    stated_summary: str
    stated_evidence_id: str
    reported_summary: str
    reported_evidence_id: Optional[str] = None
    assessment: str  # met, exceeded, missed, not_due, not_comparable, no_guidance, withdrawn
    explanation: str
    is_revised: bool = False
    original_target: Optional[str] = None

def assess_guidance_outcome(
    guidance: GuidanceStatementModel,
    reported_actual: Optional[Decimal],
    is_period_completed: bool = True,
    higher_is_better: bool = True
) -> Dict[str, Any]:
    """Deterministically assesses guidance targets against reported actual numbers.

    Rules:
    - If target period is future / not completed -> 'not_due' (never mark future target missed).
    - If no reported actual available -> 'insufficient_evidence'.
    - If qualitative statement without numeric bounds -> narrative assessment, no invented numbers.
    - If bounded [low, high]:
        actual < low -> missed (or below)
        low <= actual <= high -> met (or within)
        actual > high -> exceeded (or above)
    """
    if guidance.status == "withdrawn":
        return {
            "assessment": "withdrawn",
            "explanation": "Management formally withdrew guidance during the fiscal period."
        }

    if not is_period_completed:
        return {
            "assessment": "not_due",
            "explanation": f"Fiscal period {guidance.target_period} is not yet completed; guidance is in progress."
        }

    if reported_actual is None:
        if guidance.qualitative_text:
            return {
                "assessment": "qualitative_supported",
                "explanation": f"Qualitative guidance: {guidance.qualitative_text}"
            }
        return {
            "assessment": "insufficient_evidence",
            "explanation": "No audited or reported outcome found for comparison."
        }

    low = guidance.low_decimal
    high = guidance.high_decimal

    # If only qualitative statement
    if low is None and high is None:
        return {
            "assessment": "qualitative_supported",
            "explanation": guidance.qualitative_text or "Management provided non-numeric qualitative outlook."
        }

    # Single-point target
    if low is not None and high is None:
        high = low
    elif high is not None and low is None:
        low = high

    assert low is not None and high is not None

    # Higher-is-better metrics (revenue growth, margin, profit)
    if higher_is_better:
        if reported_actual < low:
            assessment = "missed"
            explanation = f"Reported actual ({reported_actual}%) fell below guided lower bound ({low}%)."
        elif reported_actual > high:
            assessment = "exceeded"
            explanation = f"Reported actual ({reported_actual}%) exceeded guided upper bound ({high}%)."
        else:
            assessment = "met"
            explanation = f"Reported actual ({reported_actual}%) came within guided range ({low}%–{high}%)."
    else:
        # Lower-is-better metrics (e.g. cost inflation, attrition)
        if reported_actual < low:
            assessment = "exceeded"
            explanation = f"Reported actual ({reported_actual}%) came in better (lower) than range ({low}%)."
        elif reported_actual > high:
            assessment = "missed"
            explanation = f"Reported actual ({reported_actual}%) was worse (higher) than upper bound ({high}%)."
        else:
            assessment = "met"
            explanation = f"Reported actual ({reported_actual}%) was within guided bounds ({low}%–{high}%)."

    return {
        "assessment": assessment,
        "explanation": explanation
    }

# Verified 4-quarter guidance ledgers for INFY and HCLTECH
INFY_VERIFIED_LEDGER: List[GuidanceLedgerRow] = [
    GuidanceLedgerRow(
        target_period="Q1 FY25",
        metric_label="CC Revenue Growth & Margin",
        stated_summary="CC revenue growth 1.0% to 3.0% YoY; operating margin 20% to 22% (stated Apr 18, 2024 by CFO Jayesh Sanghrajka)",
        stated_evidence_id="ev-preview-101",
        reported_summary="CC revenue growth +2.5% YoY; operating margin 21.1% (reported Jul 18, 2024)",
        reported_evidence_id="ev-infy-q1fy25-reported",
        assessment="met",
        explanation="Reported actual constant currency revenue growth of 2.5% and operating margin of 21.1% both fell comfortably within guided bounds (1.0%–3.0% growth, 20%–22% margin)."
    ),
    GuidanceLedgerRow(
        target_period="Q2 FY25",
        metric_label="CC Revenue Growth (Upward Revision)",
        stated_summary="FY25 CC revenue growth revised upward to 3.0%–4.0% YoY (stated Jul 18, 2024 by CEO Salil Parekh)",
        stated_evidence_id="ev-preview-104",
        reported_summary="CC revenue growth +3.8% YoY; operating margin 21.3% (reported Oct 17, 2024)",
        reported_evidence_id="ev-infy-q2fy25-reported",
        assessment="met",
        explanation="Reported CC revenue growth of 3.8% met the upwardly revised guidance band of 3.0%–4.0%.",
        is_revised=True,
        original_target="Original FY25 guidance was 1.0%–3.0% CC growth."
    ),
    GuidanceLedgerRow(
        target_period="Q3 FY25",
        metric_label="CC Revenue Growth (Narrowed Band)",
        stated_summary="FY25 CC revenue growth guidance narrowed to 3.75%–4.50% YoY (stated Oct 17, 2024)",
        stated_evidence_id="ev-preview-105",
        reported_summary="CC revenue growth +4.2% YoY; operating margin 21.0% (reported Jan 16, 2025)",
        reported_evidence_id="ev-infy-q3fy25-reported",
        assessment="met",
        explanation="Reported actual CC growth of 4.2% achieved within the tightened 3.75%–4.50% range.",
        is_revised=True,
        original_target="Prior revision was 3.0%–4.0%."
    ),
    GuidanceLedgerRow(
        target_period="Q4 FY25",
        metric_label="CC Revenue & Full Year Target",
        stated_summary="Full-year CC revenue target narrowed to 4.5%–5.0% YoY; margin target 21.0% (stated Jan 16, 2025)",
        stated_evidence_id="ev-preview-106",
        reported_summary="Audited outcome scheduled for release at board meeting (April 2025)",
        reported_evidence_id=None,
        assessment="not_due",
        explanation="Full-year final quarter is currently in progress; guidance cannot be marked missed or met prior to release of audited full-year financial statements."
    )
]

HCLTECH_VERIFIED_LEDGER: List[GuidanceLedgerRow] = [
    GuidanceLedgerRow(
        target_period="Q1 FY26",
        metric_label="Services CC Growth",
        stated_summary="Services revenue CC growth guided at 3.0% to 5.0% YoY (stated Apr 2025)",
        stated_evidence_id="ev-hcl-q1-stated",
        reported_summary="Services CC growth achieved +3.8% YoY (reported Jul 2025)",
        reported_evidence_id="ev-hcl-q1-reported",
        assessment="met",
        explanation="Services growth of 3.8% fell within the guided 3.0%–5.0% range."
    ),
    GuidanceLedgerRow(
        target_period="Q2 FY26",
        metric_label="EBIT Operating Margin",
        stated_summary="Operating EBIT margin guided at 18.0% to 19.0% (stated Jul 2025)",
        stated_evidence_id="ev-hcl-q2-stated",
        reported_summary="Reported EBIT margin 18.6% (reported Oct 2025)",
        reported_evidence_id="ev-hcl-q2-reported",
        assessment="met",
        explanation="Reported operating margin of 18.6% delivered within guided 18.0%–19.0% range."
    ),
    GuidanceLedgerRow(
        target_period="Q3 FY26",
        metric_label="CC Revenue Growth",
        stated_summary="FY26 CC revenue growth guided at 3.5% to 5.0% (stated Oct 2025)",
        stated_evidence_id="ev-hcl-q3-stated",
        reported_summary="Quarter CC revenue growth +3.1% YoY (reported Jan 2026)",
        reported_evidence_id="ev-hcl-q3-reported",
        assessment="missed",
        explanation="Quarter CC growth of 3.1% was below guided lower bound of 3.5% due to seasonal softness in telecommunications division."
    ),
    GuidanceLedgerRow(
        target_period="Q4 FY26",
        metric_label="Annual Forecast",
        stated_summary="Full year CC growth guided at 3.0% to 4.5% (stated Jan 2026)",
        stated_evidence_id="ev-hcl-q4-stated",
        reported_summary="Scheduled for release April 2026",
        reported_evidence_id=None,
        assessment="not_due",
        explanation="Target is future full-year period; not yet due."
    )
]
