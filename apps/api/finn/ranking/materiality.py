import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

# High-risk keywords that must NEVER be buried regardless of category
CRITICAL_SAFETY_KEYWORDS = [
    ("auditor_resignation", r"resignation of (statutory )?auditor"),
    ("auditor_qualification", r"auditor['’]?s (qualification|adverse remark|disclaimer of opinion)"),
    ("insolvency", r"(insolvency|bankruptcy|cirp|nclt|liquidation|default in payment)"),
    ("regulatory_action", r"(sebi (order|notice)|cbi|ed investigation|search and seizure|restatement)"),
    ("promoter_pledge_invocation", r"(invocation of pledge|revocation of non-disposal)"),
    ("leadership_distress", r"(termination of (ceo|cfo|md)|dismissal of director)")
]

class RankingResult(BaseModel):
    category: str
    subtype: str
    stage: str
    tier: str  # needs_attention, worth_a_look, routine
    score: float
    reasons: List[str]
    override_applied: bool = False

class MaterialityClassifier:
    """Deterministic, inspectable materiality and ranking engine.

    Guarantees:
    - Safety overrides put insolvency, auditor distress, and regulatory actions in 'needs_attention'
      regardless of routine labels or classifier failure.
    - Results intimations/notices rank strictly below actual results filings.
    - Inspectable scoring breakdown.
    """

    def rank_announcement(
        self,
        title: str,
        desc: Optional[str] = None,
        user_categories: Optional[List[str]] = None
    ) -> RankingResult:
        full_text = f"{title} {desc or ''}".lower()
        reasons: List[str] = []

        # 1. Critical Safety Override Check
        for override_key, pattern in CRITICAL_SAFETY_KEYWORDS:
            if re.search(pattern, full_text):
                reasons.append(f"SAFETY OVERRIDE: {override_key.replace('_', ' ').title()}")
                return RankingResult(
                    category="litigation" if "regulatory" in override_key or "insolvency" in override_key else "management_change",
                    subtype=override_key,
                    stage="critical",
                    tier="needs_attention",
                    score=95.0,
                    reasons=reasons,
                    override_applied=True
                )

        # 2. Check for Results Notice vs Actual Results
        is_notice = bool(re.search(r"\b(notice of board meeting|intimation of board meeting|board meeting to consider)\b", full_text))
        is_actual_results = bool(re.search(r"\b(outcome of board meeting|financial results for|un-audited financial results|audited financial results)\b", full_text))

        category = "unclassified"
        subtype = "general"
        stage = "informational"
        base_score = 10.0

        if is_notice:
            category = "results"
            subtype = "board_meeting_intimation"
            stage = "notice"
            base_score = 8.0  # Routine: notice only, no numbers disclosed
            reasons.append("Notice of meeting only; no reported numbers")
        elif is_actual_results:
            category = "results"
            subtype = "financial_results"
            stage = "completed"
            base_score = 65.0  # Needs attention: actual financial results
            reasons.append("Actual quarterly/annual financial results published")
        elif re.search(r"\b(acquisition|amalgamation|merger|takeover|demerger)\b", full_text):
            category = "m_and_a"
            subtype = "acquisition"
            stage = "completed" if "outcome" in full_text or "completed" in full_text else "proposed"
            base_score = 60.0
            reasons.append("Material corporate transaction / M&A")
        elif re.search(r"\b(credit rating|rating downgrade|icra|crisil|care)\b", full_text):
            category = "credit_rating"
            if "downgrade" in full_text:
                subtype = "rating_downgrade"
                base_score = 55.0  # Downgrades are high priority
                reasons.append("Credit rating downgrade")
            else:
                subtype = "rating_reaffirmation"
                base_score = 25.0
                reasons.append("Credit rating update / reaffirmation")
        elif re.search(r"\b(dividend|record date for interim dividend)\b", full_text):
            category = "dividend"
            subtype = "interim_dividend" if "interim" in full_text else "dividend"
            stage = "completed"
            base_score = 25.0
            reasons.append("Shareholder distribution / dividend declaration")
        elif re.search(r"\b(capacity expansion|new plant|commercial production|capex)\b", full_text):
            category = "capex"
            subtype = "expansion"
            base_score = 40.0
            reasons.append("Capital expenditure / expansion update")
        elif re.search(r"\b(resignation|appointment|cessation)\b", full_text):
            category = "management_change"
            subtype = "leadership_change"
            base_score = 45.0
            reasons.append("Executive leadership / KMP change")
        elif re.search(r"\b(investor presentation|analyst meet|transcript|concall)\b", full_text):
            category = "investor_meetings"
            subtype = "presentation_or_concall"
            base_score = 15.0
            reasons.append("Investor presentation or call transcript")
        elif re.search(r"\b(trading window|postal ballot|agm|egm|compliance)\b", full_text):
            category = "routine_compliance"
            subtype = "compliance_filing"
            base_score = 5.0
            reasons.append("Routine statutory compliance filing")

        # 3. User Category Preference Boost
        user_boost = 0.0
        if user_categories and category in user_categories:
            user_boost = 15.0
            reasons.append(f"User explicitly tracking category: {category}")

        final_score = base_score + user_boost

        # 4. Determine Priority Tier
        if final_score >= 55.0:
            tier = "needs_attention"
        elif final_score >= 25.0:
            tier = "worth_a_look"
        else:
            tier = "routine"

        return RankingResult(
            category=category,
            subtype=subtype,
            stage=stage,
            tier=tier,
            score=final_score,
            reasons=reasons,
            override_applied=False
        )
