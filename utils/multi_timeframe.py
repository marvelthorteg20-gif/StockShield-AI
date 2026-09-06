"""Multi-timeframe trend scoring from a daily OHLCV history."""

from __future__ import annotations

from typing import Dict, Optional

import pandas as pd

ALIGNMENT_WEIGHTS = {
    "Strong Bullish": 1.0,
    "Bullish": 0.85,
    "Neutral": 0.55,
    "Bearish": 0.15,
    "Strong Bearish": 0.0,
}

WINDOWS = {
    "1D": 2,
    "1W": 5,
    "1M": 21,
    "3M": 63,
    "1Y": 252,
}

THRESHOLDS = {
    "1D": (0.4, 1.5),
    "1W": (1.0, 3.0),
    "1M": (2.0, 7.0),
    "3M": (4.0, 12.0),
    "1Y": (8.0, 20.0),
}


def _safe_close(history: Optional[pd.DataFrame]) -> Optional[float]:
    """Latest close, or None when history is empty."""
    if history is None or len(history) == 0:
        return None
    return float(history["Close"].iloc[-1])


def _window_return(series: pd.Series) -> float:
    """Percent return from first to last close in *series*."""
    start = float(series.iloc[0])
    end = float(series.iloc[-1])
    if start == 0:
        return 0.0
    return ((end - start) / start) * 100.0


def classify_timeframe(
    return_pct: float,
    close: float,
    sma: Optional[float],
    bull_th: float,
    strong_th: float,
) -> str:
    """Map return and SMA bias to a professional timeframe label."""
    above = sma is not None and close > sma
    below = sma is not None and close < sma

    if return_pct >= strong_th and above:
        return "Strong Bullish"
    if return_pct <= -strong_th and below:
        return "Strong Bearish"
    if return_pct >= bull_th or (return_pct > 0 and above):
        return "Bullish" if return_pct >= 0 else "Neutral"
    if return_pct <= -bull_th or (return_pct < 0 and below):
        return "Bearish" if return_pct <= 0 else "Neutral"
    if above:
        return "Bullish"
    if below:
        return "Bearish"
    return "Neutral"


def analyze_timeframes(history: Optional[pd.DataFrame]) -> Dict[str, object]:
    """Score 1D, 1W, 1M, 3M, and 1Y trends and overall alignment."""
    labels = {}
    close = _safe_close(history)
    if close is None:
        return {
            "1D": "Neutral",
            "1W": "Neutral",
            "1M": "Neutral",
            "3M": "Neutral",
            "1Y": "Neutral",
            "alignment": 50,
        }

    for name, bars in WINDOWS.items():
        slice_df = history.tail(max(bars, 2))
        closes = slice_df["Close"]
        ret = _window_return(closes)
        sma = float(closes.mean()) if len(closes) else close
        bull_th, strong_th = THRESHOLDS[name]
        labels[name] = classify_timeframe(ret, close, sma, bull_th, strong_th)

    weights = [ALIGNMENT_WEIGHTS[labels[name]] for name in WINDOWS]
    alignment = int(round(100 * sum(weights) / len(weights)))
    return {
        "1D": labels["1D"],
        "1W": labels["1W"],
        "1M": labels["1M"],
        "3M": labels["3M"],
        "1Y": labels["1Y"],
        "alignment": alignment,
    }
