"""Institutional-style market structure and flow signals."""

from __future__ import annotations


def _clamp(value, low=0, high=99):
    return int(max(low, min(high, round(value))))


def _safe(value, default=0.0):
    try:
        number = float(value)
        if number != number:
            return default
        return number
    except (TypeError, ValueError):
        return default


def detect_institutional_signals(history, high_52=None, low_52=None, support=None, resistance=None):
    """Detect unusual volume, breakouts, 52-week proximity, and gaps."""
    empty = {
        "unusual_volume": {"detected": False, "confidence": 10},
        "breakout": {"detected": False, "confidence": 10},
        "breakdown": {"detected": False, "confidence": 10},
        "near_52w_high": {"detected": False, "confidence": 10},
        "near_52w_low": {"detected": False, "confidence": 10},
        "gap_up": {"detected": False, "confidence": 10},
        "gap_down": {"detected": False, "confidence": 10},
    }
    if history is None or len(history) < 3:
        return empty

    latest = history.iloc[-1]
    previous = history.iloc[-2]
    close = _safe(latest["Close"])
    high = _safe(latest["High"])
    low = _safe(latest["Low"])
    open_px = _safe(latest["Open"])
    volume = _safe(latest["Volume"])
    prev_close = _safe(previous["Close"])

    vol_avg = _safe(history["Volume"].tail(20).mean(), volume)
    prior_high = _safe(history["High"].iloc[:-1].tail(20).max(), high)
    prior_low = _safe(history["Low"].iloc[:-1].tail(20).min(), low)
    high_52 = _safe(high_52, history["High"].max())
    low_52 = _safe(low_52, history["Low"].min())
    resistance = _safe(resistance, prior_high)
    support = _safe(support, prior_low)

    unusual = volume > (1.8 * vol_avg) if vol_avg > 0 else False
    unusual_conf = 15
    if vol_avg > 0:
        unusual_conf = _clamp(20 + (volume / vol_avg - 1.0) * 45)

    breakout = close > max(prior_high, resistance) * 0.999
    breakdown = close < min(prior_low, support) * 1.001
    breakout_conf = _clamp(20 + max(0.0, (close - prior_high) / close * 800)) if close else 10
    breakdown_conf = _clamp(20 + max(0.0, (prior_low - close) / close * 800)) if close else 10

    near_high = high_52 > 0 and (high_52 - close) / high_52 <= 0.03
    near_low = low_52 > 0 and (close - low_52) / low_52 <= 0.03 if close else False
    near_high_conf = (
        _clamp(100 - ((high_52 - close) / high_52) * 1500) if high_52 else 10
    )
    near_low_conf = (
        _clamp(100 - ((close - low_52) / low_52) * 1500) if low_52 and close else 10
    )

    gap_up = prev_close > 0 and open_px >= prev_close * 1.01
    gap_down = prev_close > 0 and open_px <= prev_close * 0.99
    gap_pct = abs(open_px - prev_close) / prev_close * 100 if prev_close else 0
    gap_conf = _clamp(25 + gap_pct * 18)

    return {
        "unusual_volume": {
            "detected": bool(unusual),
            "confidence": max(10, unusual_conf if unusual else min(unusual_conf, 35)),
        },
        "breakout": {
            "detected": bool(breakout),
            "confidence": max(10, breakout_conf if breakout else min(breakout_conf, 30)),
        },
        "breakdown": {
            "detected": bool(breakdown),
            "confidence": max(10, breakdown_conf if breakdown else min(breakdown_conf, 30)),
        },
        "near_52w_high": {
            "detected": bool(near_high),
            "confidence": max(10, near_high_conf if near_high else min(near_high_conf, 40)),
        },
        "near_52w_low": {
            "detected": bool(near_low),
            "confidence": max(10, near_low_conf if near_low else min(near_low_conf, 40)),
        },
        "gap_up": {"detected": bool(gap_up), "confidence": max(10, gap_conf if gap_up else min(gap_conf, 25))},
        "gap_down": {"detected": bool(gap_down), "confidence": max(10, gap_conf if gap_down else min(gap_conf, 25))},
    }
