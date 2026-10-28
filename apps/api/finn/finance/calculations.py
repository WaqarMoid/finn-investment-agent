from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any, Optional
from finn.adapters.price_adapter import PriceBar

def calculate_price_move(
    bars: List[PriceBar],
    threshold_pct: float = 5.0
) -> Dict[str, Any]:
    """Calculates price movement between the latest completed session and the previous completed session.

    Formula: 100 * (current_close / previous_close - 1)
    Rules:
    - Missing or fewer than 2 completed sessions -> insufficient_history.
    - Zero or negative previous close -> invalid_baseline (percentage null).
    - Threshold evaluation is strictly greater than threshold_pct: abs(delta_pct) > threshold_pct.
    """
    if len(bars) < 2:
        return {
            "status": "insufficient_history",
            "current_date": bars[-1].session_date if bars else None,
            "previous_date": None,
            "current_close": str(bars[-1].close) if bars else None,
            "previous_close": None,
            "delta_value": None,
            "delta_pct": None,
            "is_alert": False,
            "reason": "Need at least 2 completed sessions to compute price movement"
        }

    current = bars[-1]
    previous = bars[-2]

    if previous.close <= Decimal("0"):
        return {
            "status": "invalid_baseline",
            "current_date": current.session_date,
            "previous_date": previous.session_date,
            "current_close": str(current.close),
            "previous_close": str(previous.close),
            "delta_value": str(current.close - previous.close),
            "delta_pct": None,
            "is_alert": False,
            "reason": "Previous session close is zero or negative; percentage change undefined"
        }

    delta_val = current.close - previous.close
    delta_pct_exact = ((current.close / previous.close) - Decimal("1")) * Decimal("100")
    delta_pct = delta_pct_exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    # Rule: Trigger strictly greater than threshold
    thresh_dec = Decimal(str(threshold_pct))
    is_alert = abs(delta_pct) > thresh_dec

    return {
        "status": "ok",
        "current_date": current.session_date,
        "previous_date": previous.session_date,
        "current_close": str(current.close),
        "previous_close": str(previous.close),
        "delta_value": str(delta_val),
        "delta_pct": str(delta_pct),
        "is_alert": bool(is_alert),
        "threshold_pct": str(thresh_dec)
    }

def calculate_volume_spike(
    bars: List[PriceBar],
    threshold_multiple: float = 2.0,
    lookback_sessions: int = 20
) -> Dict[str, Any]:
    """Calculates volume ratio of latest session relative to the mean of previous 20 completed sessions.

    Formula: today_volume / mean(previous 20 completed sessions' volumes)
    Rules:
    - Today is strictly excluded from the baseline.
    - Fewer than 20 prior sessions -> insufficient_history (alert false).
    - Zero baseline volume -> zero_baseline (multiple null).
    - Trigger strictly greater than threshold_multiple (e.g. 2.0x is not triggered, 2.01x is).
    """
    if len(bars) <= lookback_sessions:
        return {
            "status": "insufficient_history",
            "current_date": bars[-1].session_date if bars else None,
            "today_volume": bars[-1].volume if bars else None,
            "prior_sessions_count": len(bars) - 1 if len(bars) > 0 else 0,
            "baseline_mean": None,
            "volume_multiple": None,
            "is_alert": False,
            "reason": f"Requires at least {lookback_sessions} prior completed sessions, got {len(bars) - 1}"
        }

    today = bars[-1]
    prior_bars = bars[-(lookback_sessions + 1) : -1]
    assert len(prior_bars) == lookback_sessions, f"Expected {lookback_sessions} bars, got {len(prior_bars)}"

    total_prior_volume = sum(Decimal(str(b.volume)) for b in prior_bars)
    baseline_mean = total_prior_volume / Decimal(str(lookback_sessions))

    if baseline_mean <= Decimal("0"):
        return {
            "status": "zero_baseline",
            "current_date": today.session_date,
            "today_volume": today.volume,
            "prior_sessions_count": lookback_sessions,
            "baseline_mean": "0.0",
            "volume_multiple": None,
            "is_alert": False,
            "reason": "Baseline 20-day mean volume is zero"
        }

    multiple_exact = Decimal(str(today.volume)) / baseline_mean
    multiple = multiple_exact.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    thresh_dec = Decimal(str(threshold_multiple))
    # Trigger strictly greater than threshold
    is_alert = multiple > thresh_dec

    return {
        "status": "ok",
        "current_date": today.session_date,
        "today_volume": today.volume,
        "prior_sessions_count": lookback_sessions,
        "baseline_mean": str(baseline_mean.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
        "volume_multiple": str(multiple),
        "threshold_multiple": str(thresh_dec),
        "is_alert": bool(is_alert)
    }

def adjust_for_stock_split(
    bars: List[PriceBar],
    split_date: str,
    split_ratio: Decimal
) -> List[PriceBar]:
    """Adjusts historical bars prior to split_date for a stock split.

    split_ratio: e.g. Decimal('2.0') for 2:1 stock split (price halved, volume doubled).
    """
    adjusted: List[PriceBar] = []
    for b in bars:
        if b.session_date < split_date:
            adj_open = (b.open / split_ratio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            adj_high = (b.high / split_ratio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            adj_low = (b.low / split_ratio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            adj_close = (b.close / split_ratio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            adj_vol = int(Decimal(str(b.volume)) * split_ratio)
            adjusted.append(PriceBar(
                session_date=b.session_date,
                open=adj_open,
                high=adj_high,
                low=adj_low,
                close=adj_close,
                adjusted_close=b.adjusted_close,
                volume=adj_vol,
                action_flags=f"split_adjusted_{split_ratio}",
                provider=b.provider
            ))
        else:
            adjusted.append(b)
    return adjusted
