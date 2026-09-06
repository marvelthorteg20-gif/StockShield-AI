"""Weighted AI score from trend, oscillators, volatility, news, and fundamentals.

Numeric weights and component scores are unchanged from the original engine.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from utils.common import clamp

SCORE_FLOOR: int = 0
SCORE_CEILING: int = 100
NEUTRAL_COMPONENT: int = 50

WEIGHT_TREND: float = 0.18
WEIGHT_RSI: float = 0.12
WEIGHT_MACD: float = 0.12
WEIGHT_BOLLINGER: float = 0.08
WEIGHT_VOLUME: float = 0.08
WEIGHT_ATR: float = 0.08
WEIGHT_ADX: float = 0.10
WEIGHT_NEWS: float = 0.12
WEIGHT_FUNDAMENTALS: float = 0.12

RSI_HEALTHY_LOW: float = 45.0
RSI_HEALTHY_HIGH: float = 60.0
RSI_WARM_HIGH: float = 70.0
RSI_COLD: float = 30.0
RSI_RECOVERY_HIGH: float = 45.0


def _clamp(value: float, low: float = SCORE_FLOOR, high: float = SCORE_CEILING) -> float:
    """Clamp *value* into [low, high]."""
    return clamp(float(value), float(low), float(high))


def _trend_score(trend: str) -> int:
    """Score the existing trend label."""
    if trend == "🟢 STRONG BULLISH":
        return 90
    if trend == "🟢 BULLISH":
        return 75
    if trend == "🔴 STRONG BEARISH":
        return 15
    return NEUTRAL_COMPONENT


def _rsi_score(rsi: float) -> int:
    """Score RSI using the original band table."""
    if rsi != rsi:
        return NEUTRAL_COMPONENT
    if RSI_HEALTHY_LOW <= rsi <= RSI_HEALTHY_HIGH:
        return 85
    if RSI_HEALTHY_HIGH < rsi <= RSI_WARM_HIGH:
        return 70
    if rsi > RSI_WARM_HIGH:
        return 30
    if rsi < RSI_COLD:
        return 60
    if RSI_COLD <= rsi < RSI_RECOVERY_HIGH:
        return 55
    return NEUTRAL_COMPONENT


def _macd_score(macd_status: str) -> int:
    """Score MACD status text."""
    if macd_status == "🟢 Bullish Crossover":
        return 80
    if macd_status == "🔴 Bearish Crossover":
        return 25
    return NEUTRAL_COMPONENT


def _bb_score(bb_signal: str) -> int:
    """Score Bollinger-band location text."""
    if bb_signal == "🟢 Price Below Lower Band (Oversold)":
        return 70
    if bb_signal == "🔴 Price Above Upper Band (Overbought)":
        return 30
    return 55


def _volume_score(volume_status: str) -> int:
    """Score volume regime text."""
    if volume_status == "🟢 High Volume":
        return 75
    return 45


def _atr_score(volatility_level: str) -> int:
    """Score ATR volatility label."""
    if volatility_level == "🟢 Low":
        return 80
    if volatility_level == "🔴 High":
        return 30
    return 60


def _adx_score(adx_strength: str) -> int:
    """Score ADX strength label."""
    if adx_strength == "Strong":
        return 85
    if adx_strength == "Moderate":
        return 65
    return 40


def _news_score(sentiment: Optional[str]) -> int:
    """Score news sentiment label."""
    if sentiment == "🟢 BULLISH":
        return 80
    if sentiment == "🔴 BEARISH":
        return 20
    return NEUTRAL_COMPONENT


def compute_ai_score(
    trend: str,
    rsi: float,
    macd_status: str,
    bb_signal: str,
    volume_status: str,
    volatility_level: str,
    adx_strength: str,
    sentiment: Optional[str] = None,
    fundamental_score: Any = 50,
) -> Tuple[int, Dict[str, float]]:
    """Weighted AI score from trend, oscillators, volatility, news, and fundamentals."""
    try:
        fund = float(fundamental_score)
        if fund != fund:
            fund = 50.0
    except (TypeError, ValueError):
        fund = 50.0

    components: Dict[str, float] = {
        "trend": _trend_score(trend),
        "rsi": _rsi_score(rsi),
        "macd": _macd_score(macd_status),
        "bollinger": _bb_score(bb_signal),
        "volume": _volume_score(volume_status),
        "atr": _atr_score(volatility_level),
        "adx": _adx_score(adx_strength),
        "news": _news_score(sentiment),
        "fundamentals": _clamp(fund),
    }

    weights: Dict[str, float] = {
        "trend": WEIGHT_TREND,
        "rsi": WEIGHT_RSI,
        "macd": WEIGHT_MACD,
        "bollinger": WEIGHT_BOLLINGER,
        "volume": WEIGHT_VOLUME,
        "atr": WEIGHT_ATR,
        "adx": WEIGHT_ADX,
        "news": WEIGHT_NEWS,
        "fundamentals": WEIGHT_FUNDAMENTALS,
    }

    score = sum(components[name] * weights[name] for name in weights)
    return int(round(_clamp(score))), components
