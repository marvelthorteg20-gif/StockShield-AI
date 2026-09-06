"""Swing-trading plan: entry, stop, three targets, horizon, and probability."""

from __future__ import annotations

from typing import Any, Dict

from utils.common import safe_float as _safe

FALLBACK_STOP_FRACTION: float = 0.02
FALLBACK_T1_MULT: float = 1.04
FALLBACK_T2_MULT: float = 1.06
TARGET3_R: float = 4.0
HOLDING_ATR_FALLBACK_DAYS: int = 7
HOLDING_MIN_DAYS: int = 3
HOLDING_MAX_DAYS: int = 45
PROBABILITY_MIN: int = 15
PROBABILITY_MAX: int = 95


def build_swing_plan(
    entry: Any,
    stop_loss: Any,
    target1: Any,
    target2: Any,
    atr: Any,
    probability: Any = 50,
) -> Dict[str, Any]:
    """Build a 3-target swing plan from existing smart-risk levels."""
    entry_value = _safe(entry)
    stop = _safe(stop_loss, entry_value * (1.0 - FALLBACK_STOP_FRACTION))
    t1 = _safe(target1, entry_value * FALLBACK_T1_MULT)
    t2 = _safe(target2, entry_value * FALLBACK_T2_MULT)
    atr_value = max(_safe(atr, 0.0), 0.0)
    risk = entry_value - stop
    if risk <= 0:
        risk = entry_value * FALLBACK_STOP_FRACTION
        stop = entry_value - risk
    target3 = entry_value + (TARGET3_R * risk)
    if target3 <= t2:
        target3 = t2 + risk

    if atr_value > 0:
        holding_days = int(round((t1 - entry_value) / atr_value))
    else:
        holding_days = HOLDING_ATR_FALLBACK_DAYS
    holding_days = max(HOLDING_MIN_DAYS, min(HOLDING_MAX_DAYS, holding_days))

    success = int(max(PROBABILITY_MIN, min(PROBABILITY_MAX, _safe(probability, 50))))

    return {
        "entry": entry_value,
        "stop_loss": stop,
        "target1": t1,
        "target2": t2,
        "target3": target3,
        "holding_days": holding_days,
        "probability": success,
    }
