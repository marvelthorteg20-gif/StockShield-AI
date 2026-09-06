"""Candlestick pattern detectors used by the indicator snapshot."""

from __future__ import annotations

from typing import List, Tuple

import pandas as pd

OHLC = Tuple[float, float, float, float]

DOJI_BODY_RATIO: float = 0.1
HAMMER_LOWER_MULT: float = 2.0
HAMMER_UPPER_BODY_FRAC: float = 0.5
HAMMER_UPPER_RANGE_FRAC: float = 0.1
HAMMER_BODY_RANGE_FRAC: float = 0.4
HAMMER_CLOSE_RANGE_FRAC: float = 0.6
STAR_SMALL_BODY_FRAC: float = 0.5
STAR_DOJI_RANGE_FRAC: float = 0.4


def _ohlc(row: pd.Series) -> OHLC:
    """Extract Open/High/Low/Close as floats."""
    return float(row["Open"]), float(row["High"]), float(row["Low"]), float(row["Close"])


def _body(open_price: float, close: float) -> float:
    """Absolute real-body size."""
    return abs(close - open_price)


def _range(high: float, low: float) -> float:
    """High-low range."""
    return high - low


def is_doji(
    open_price: float,
    high: float,
    low: float,
    close: float,
    body_ratio: float = DOJI_BODY_RATIO,
) -> bool:
    """True when the real body is tiny relative to the range."""
    candle_range = _range(high, low)
    if candle_range <= 0:
        return abs(close - open_price) < 1e-9
    return _body(open_price, close) / candle_range <= body_ratio


def is_hammer(open_price: float, high: float, low: float, close: float) -> bool:
    """True for a hammer-shaped candle on the latest bar."""
    body = _body(open_price, close)
    candle_range = _range(high, low)
    if candle_range <= 0 or body <= 0:
        return False

    upper = high - max(open_price, close)
    lower = min(open_price, close) - low

    return (
        lower >= HAMMER_LOWER_MULT * body
        and upper <= max(body * HAMMER_UPPER_BODY_FRAC, candle_range * HAMMER_UPPER_RANGE_FRAC)
        and body / candle_range <= HAMMER_BODY_RANGE_FRAC
        and max(open_price, close) >= low + HAMMER_CLOSE_RANGE_FRAC * candle_range
    )


def is_bullish_engulfing(prev: OHLC, curr: OHLC) -> bool:
    """True when the current bullish body engulfs the previous bearish body."""
    po, _, _, pc = prev
    o, _, _, c = curr
    return pc < po and c > o and o <= pc and c >= po and _body(o, c) > _body(po, pc)


def is_bearish_engulfing(prev: OHLC, curr: OHLC) -> bool:
    """True when the current bearish body engulfs the previous bullish body."""
    po, _, _, pc = prev
    o, _, _, c = curr
    return pc > po and c < o and o >= pc and c <= po and _body(o, c) > _body(po, pc)


def is_morning_star(first: OHLC, second: OHLC, third: OHLC) -> bool:
    """True for a three-bar morning-star reversal."""
    o1, _, _, c1 = first
    o2, h2, l2, c2 = second
    o3, _, _, c3 = third

    body1 = _body(o1, c1)
    body2 = _body(o2, c2)
    body3 = _body(o3, c3)
    range2 = _range(h2, l2)

    if c1 >= o1 or c3 <= o3:
        return False
    if body1 <= 0 or body3 <= 0:
        return False
    if body2 > STAR_SMALL_BODY_FRAC * body1 and (
        range2 <= 0 or body2 / range2 > STAR_DOJI_RANGE_FRAC
    ):
        return False

    midpoint = (o1 + c1) / 2
    return c3 > midpoint and max(o2, c2) < min(o1, c1)


def is_evening_star(first: OHLC, second: OHLC, third: OHLC) -> bool:
    """True for a three-bar evening-star reversal."""
    o1, _, _, c1 = first
    o2, h2, l2, c2 = second
    o3, _, _, c3 = third

    body1 = _body(o1, c1)
    body2 = _body(o2, c2)
    body3 = _body(o3, c3)
    range2 = _range(h2, l2)

    if c1 <= o1 or c3 >= o3:
        return False
    if body1 <= 0 or body3 <= 0:
        return False
    if body2 > STAR_SMALL_BODY_FRAC * body1 and (
        range2 <= 0 or body2 / range2 > STAR_DOJI_RANGE_FRAC
    ):
        return False

    midpoint = (o1 + c1) / 2
    return c3 < midpoint and min(o2, c2) > max(o1, c1)


def detect_candlestick_patterns(history: pd.DataFrame) -> List[str]:
    """Return pattern names completed on the latest candle."""
    if history is None or len(history) < 1:
        return []

    latest = _ohlc(history.iloc[-1])
    patterns: List[str] = []

    if is_doji(*latest):
        patterns.append("Doji")
    if is_hammer(*latest):
        patterns.append("Hammer")

    if len(history) >= 2:
        prev = _ohlc(history.iloc[-2])
        if is_bullish_engulfing(prev, latest):
            patterns.append("Bullish Engulfing")
        if is_bearish_engulfing(prev, latest):
            patterns.append("Bearish Engulfing")

    if len(history) >= 3:
        first = _ohlc(history.iloc[-3])
        second = _ohlc(history.iloc[-2])
        if is_morning_star(first, second, latest):
            patterns.append("Morning Star")
        if is_evening_star(first, second, latest):
            patterns.append("Evening Star")

    return patterns
