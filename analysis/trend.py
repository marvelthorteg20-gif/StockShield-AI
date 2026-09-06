"""Simple SMA/EMA trend classifier used by older helper modules."""

from __future__ import annotations

import pandas as pd


def analyze_trend(history: pd.DataFrame) -> str:
    """Score price vs SMA20/SMA50/EMA20 into a four-state trend label."""
    price = history["Close"].iloc[-1]
    sma20 = history["SMA20"].iloc[-1]
    sma50 = history["SMA50"].iloc[-1]
    ema20 = history["EMA20"].iloc[-1]

    score = 0

    if price > sma20:
        score += 1

    if price > ema20:
        score += 1

    if sma20 > sma50:
        score += 1

    if score == 3:
        trend = "🟢 STRONG BULLISH"

    elif score == 2:
        trend = "🟡 BULLISH"

    elif score == 1:
        trend = "🟠 BEARISH"

    else:
        trend = "🔴 STRONG BEARISH"

    return trend
