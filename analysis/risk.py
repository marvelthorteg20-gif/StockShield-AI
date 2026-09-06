"""Volatility, ADX strength, and ATR-based smart risk levels."""

from __future__ import annotations

from typing import Any, Dict

VOL_LOW_PCT: float = 1.5
VOL_HIGH_PCT: float = 3.0
ADX_WEAK: float = 20.0
ADX_STRONG: float = 40.0
ATR_STOP_MULT: float = 1.5
SUPPORT_BUFFER_ATR: float = 0.25
FALLBACK_STOP_FRACTION: float = 0.02
TARGET_1_R: float = 2.0
TARGET_2_R: float = 3.0


def classify_volatility(atr: Any, price: Any) -> str:
    """Label ATR as Low / Moderate / High from percent of price."""
    if atr is None or price in (None, 0) or atr != atr:
        return "🟡 Moderate"

    atr_pct = (atr / price) * 100

    if atr_pct < VOL_LOW_PCT:
        return "🟢 Low"
    if atr_pct < VOL_HIGH_PCT:
        return "🟡 Moderate"
    return "🔴 High"


def classify_adx_strength(adx: Any) -> str:
    """Map ADX to Weak / Moderate / Strong."""
    if adx is None or adx != adx:
        return "Weak"
    if adx < ADX_WEAK:
        return "Weak"
    if adx < ADX_STRONG:
        return "Moderate"
    return "Strong"


def calculate_smart_levels(
    entry: Any,
    atr: Any,
    support: Any,
    resistance: Any,
) -> Dict[str, float]:
    """ATR + support stop, with 2R / 3R targets."""
    if entry is None or entry != entry:
        raise ValueError("Invalid entry price")

    atr_value = 0.0 if atr is None or atr != atr else max(float(atr), 0.0)
    support_value = float(support) if support is not None and support == support else entry
    _ = float(resistance) if resistance is not None and resistance == resistance else entry

    atr_stop = entry - (ATR_STOP_MULT * atr_value if atr_value > 0 else entry * FALLBACK_STOP_FRACTION)
    support_stop = support_value - (SUPPORT_BUFFER_ATR * atr_value)

    candidates = [level for level in (atr_stop, support_stop, support_value) if level < entry]
    stop_loss = max(candidates) if candidates else atr_stop

    if stop_loss >= entry:
        stop_loss = entry * (1.0 - FALLBACK_STOP_FRACTION)

    risk_amount = entry - stop_loss
    if risk_amount <= 0:
        risk_amount = entry * FALLBACK_STOP_FRACTION
        stop_loss = entry - risk_amount

    target1 = entry + (TARGET_1_R * risk_amount)
    target2 = entry + (TARGET_2_R * risk_amount)

    risk_pct = (risk_amount / entry) * 100
    reward = target1 - entry
    risk_reward = reward / risk_amount if risk_amount else 0.0

    return {
        "entry": entry,
        "stop_loss": stop_loss,
        "risk_pct": risk_pct,
        "target1": target1,
        "target2": target2,
        "risk_reward": risk_reward,
    }
