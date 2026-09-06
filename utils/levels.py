"""Pivot, Fibonacci, and dynamic support/resistance engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

import config


def _safe(value: Any, default: Optional[float] = None) -> Optional[float]:
    """Parse a float, returning *default* for None/NaN/invalid."""
    try:
        number = float(value)
        if number != number:
            return default
        return number
    except (TypeError, ValueError):
        return default


def _classic_pivots(high: float, low: float, close: float) -> List[Dict[str, Any]]:
    """Classic floor-trader pivot set for one reference bar."""
    pivot = (high + low + close) / 3.0
    return [
        {"name": "Pivot R2", "price": pivot + (high - low), "kind": "Resistance", "family": "Pivot"},
        {"name": "Pivot R1", "price": (2 * pivot) - low, "kind": "Resistance", "family": "Pivot"},
        {"name": "Pivot P", "price": pivot, "kind": "Pivot", "family": "Pivot"},
        {"name": "Pivot S1", "price": (2 * pivot) - high, "kind": "Support", "family": "Pivot"},
        {"name": "Pivot S2", "price": pivot - (high - low), "kind": "Support", "family": "Pivot"},
    ]


def _fibonacci_levels(swing_high: float, swing_low: float) -> List[Dict[str, Any]]:
    """Retracement levels from swing high to swing low."""
    span = swing_high - swing_low
    ratios = (
        ("Fib 0.0%", 0.0),
        ("Fib 23.6%", 0.236),
        ("Fib 38.2%", 0.382),
        ("Fib 50.0%", 0.5),
        ("Fib 61.8%", 0.618),
        ("Fib 78.6%", 0.786),
        ("Fib 100%", 1.0),
    )
    levels = []
    for name, ratio in ratios:
        price = swing_high - span * ratio
        kind = "Resistance" if ratio < 0.5 else "Support" if ratio > 0.5 else "Pivot"
        levels.append({"name": name, "price": price, "kind": kind, "family": "Fibonacci"})
    return levels


def calculate_sr_engine(
    history: Optional[pd.DataFrame],
    lookback: int = config.SR_LOOKBACK,
) -> List[Dict[str, Any]]:
    """Return strongest support/resistance levels first."""
    if history is None or len(history) < 5:
        return []

    close = _safe(history["Close"].iloc[-1], 0.0)
    window = history.tail(max(lookback, 5))
    ref = history.iloc[-2] if len(history) >= 2 else history.iloc[-1]
    high = _safe(ref["High"], close)
    low = _safe(ref["Low"], close)
    ref_close = _safe(ref["Close"], close)

    sma20 = _safe(history["Close"].tail(config.SMA_WINDOW).mean(), close)
    ema20 = _safe(history["Close"].ewm(span=config.EMA_WINDOW, adjust=False).mean().iloc[-1], close)
    swing_high = _safe(window["High"].max(), close)
    swing_low = _safe(window["Low"].min(), close)
    recent_high = _safe(history["High"].tail(10).max(), close)
    recent_low = _safe(history["Low"].tail(10).min(), close)

    levels = []
    levels.extend(_classic_pivots(high, low, ref_close))
    levels.extend(_fibonacci_levels(swing_high, swing_low))
    levels.append({"name": "Dynamic Support (EMA20)", "price": ema20, "kind": "Support", "family": "Dynamic"})
    levels.append({"name": "Dynamic Support (SMA20)", "price": sma20, "kind": "Support", "family": "Dynamic"})
    levels.append(
        {
            "name": "Dynamic Resistance (Swing High)",
            "price": recent_high,
            "kind": "Resistance",
            "family": "Dynamic",
        }
    )
    levels.append({"name": "Dynamic Support (Swing Low)", "price": recent_low, "kind": "Support", "family": "Dynamic"})

    clustered = _cluster_and_rank(levels, close)
    return clustered


def _cluster_and_rank(
    levels: List[Dict[str, Any]],
    close: float,
    tolerance: float = 0.004,
) -> List[Dict[str, Any]]:
    """Merge nearby levels and rank by confluence."""
    usable = [item for item in levels if item["price"] is not None]
    ranked = []
    used = set()

    for i, level in enumerate(usable):
        if i in used:
            continue
        cluster = [level]
        used.add(i)
        for j, other in enumerate(usable):
            if j in used:
                continue
            if close and abs(other["price"] - level["price"]) / close <= tolerance:
                cluster.append(other)
                used.add(j)
        avg_price = sum(item["price"] for item in cluster) / len(cluster)
        names = sorted({item["name"] for item in cluster})
        families = sorted({item["family"] for item in cluster})
        kind = cluster[0]["kind"]
        if avg_price > close:
            kind = "Resistance"
        elif avg_price < close:
            kind = "Support"
        strength = min(5, 1 + len(cluster) + (1 if len(families) > 1 else 0))
        distance = abs(avg_price - close) / close if close else 1
        ranked.append(
            {
                "name": " + ".join(names[:3]),
                "price": avg_price,
                "kind": kind,
                "family": "/".join(families),
                "strength": strength,
                "distance": distance,
                "confluence": len(cluster),
            }
        )

    ranked.sort(key=lambda item: (-item["strength"], -item["confluence"], item["distance"]))
    return ranked[:12]
