"""Swing-trading plan: entry, stop, three targets, horizon, and probability."""

from __future__ import annotations


def _safe(value, default=0.0):
    try:
        number = float(value)
        if number != number:
            return default
        return number
    except (TypeError, ValueError):
        return default


def build_swing_plan(entry, stop_loss, target1, target2, atr, probability=50):
    """Build a 3-target swing plan from existing smart-risk levels."""
    entry = _safe(entry)
    stop = _safe(stop_loss, entry * 0.98)
    t1 = _safe(target1, entry * 1.04)
    t2 = _safe(target2, entry * 1.06)
    atr_value = max(_safe(atr, 0.0), 0.0)
    risk = entry - stop
    if risk <= 0:
        risk = entry * 0.02
        stop = entry - risk
    target3 = entry + (4.0 * risk)
    if target3 <= t2:
        target3 = t2 + risk

    if atr_value > 0:
        holding_days = int(round((t1 - entry) / atr_value))
    else:
        holding_days = 7
    holding_days = max(3, min(45, holding_days))

    success = int(max(15, min(95, _safe(probability, 50))))

    return {
        "entry": entry,
        "stop_loss": stop,
        "target1": t1,
        "target2": t2,
        "target3": target3,
        "holding_days": holding_days,
        "probability": success,
    }
