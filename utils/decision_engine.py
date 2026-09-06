"""AI Decision Engine for StockShield AI.

Combines trend, momentum, volatility, volume, news, fundamentals,
risk, and candlestick evidence into a single professional decision.
This module is additive and does not replace existing recommendations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from utils.common import as_text as _text
from utils.common import safe_float as _safe_float

ACTIONS = (
    "Strong Buy",
    "Buy",
    "Accumulate",
    "Hold",
    "Reduce",
    "Sell",
    "Strong Sell",
)

BULLISH_PATTERNS = {"Hammer", "Bullish Engulfing", "Morning Star"}
BEARISH_PATTERNS = {"Bearish Engulfing", "Evening Star"}

Bias = Tuple[int, str]


def _normalize_patterns(candlestick_pattern: Any) -> List[str]:
    """Turn a pattern string or list into a list of names."""
    if candlestick_pattern is None:
        return []
    if isinstance(candlestick_pattern, str):
        text = candlestick_pattern.strip()
        return [text] if text and text.lower() != "no pattern detected" else []
    return [str(item) for item in candlestick_pattern if item]


def _trend_bias(trend: Any) -> Bias:
    """Score the existing trend label."""
    label = _text(trend)
    if "STRONG BULLISH" in label:
        return 28, "Trend is strongly bullish."
    if "BULLISH" in label:
        return 16, "Trend is bullish."
    if "STRONG BEARISH" in label:
        return -28, "Trend is strongly bearish."
    if "BEARISH" in label:
        return -16, "Trend is bearish."
    return 0, "Trend is neutral."


def _macd_bias(macd_status: Any) -> Bias:
    """Score MACD status text."""
    label = _text(macd_status)
    if "BULLISH" in label:
        return 16, "MACD shows a bullish crossover."
    if "BEARISH" in label:
        return -16, "MACD shows a bearish crossover."
    return 0, "MACD is neutral."


def _rsi_bias(rsi: float) -> Bias:
    """Score RSI using the original band table."""
    if rsi != rsi:
        return 0, "RSI is unavailable."
    if 45 <= rsi <= 65:
        return 14, f"RSI ({rsi:.1f}) is in a healthy momentum zone."
    if 30 <= rsi < 45:
        return 6, f"RSI ({rsi:.1f}) is recovering from weakness."
    if rsi < 30:
        return 8, f"RSI ({rsi:.1f}) is oversold and may bounce."
    if 65 < rsi <= 70:
        return -4, f"RSI ({rsi:.1f}) is approaching overbought."
    return -14, f"RSI ({rsi:.1f}) is overbought."


def _bb_bias(bb_signal: Any) -> Bias:
    """Score Bollinger-band location text."""
    label = _text(bb_signal)
    if "OVERSOLD" in label or "LOWER" in label:
        return 8, "Price is at or below the lower Bollinger Band."
    if "OVERBOUGHT" in label or "UPPER" in label:
        return -8, "Price is at or above the upper Bollinger Band."
    return 2, "Price is inside the Bollinger Bands."


def _volume_bias(volume_status: Any, trend_score: int) -> Bias:
    """Score volume confirmation relative to trend bias."""
    label = _text(volume_status)
    high = "HIGH" in label
    if high and trend_score > 0:
        return 8, "Volume confirms the upside move."
    if high and trend_score < 0:
        return -8, "Volume confirms the downside move."
    if high:
        return 3, "Volume is elevated."
    return -2, "Volume is below average, so conviction is weaker."


def _news_bias(news_sentiment: Any) -> Bias:
    """Score news sentiment text."""
    label = _text(news_sentiment)
    if "BULLISH" in label:
        return 12, "News sentiment is bullish."
    if "BEARISH" in label or "NEGATIVE" in label:
        return -12, "News sentiment is negative."
    if "UNKNOWN" in label:
        return 0, "News sentiment is unavailable."
    return 0, "News sentiment is neutral."


def _fundamental_bias(fundamental_score: Any) -> Bias:
    """Score the 0–100 fundamental number."""
    score = _safe_float(fundamental_score, 50.0)
    if score > 80:
        return 15, f"Fundamental score ({score:.0f}/100) is strong."
    if score >= 60:
        return 8, f"Fundamental score ({score:.0f}/100) is supportive."
    if score >= 40:
        return 0, f"Fundamental score ({score:.0f}/100) is mixed."
    return -12, f"Fundamental score ({score:.0f}/100) is weak."


def _risk_bias(risk_level: Any) -> Bias:
    """Score the existing risk badge."""
    label = _text(risk_level)
    if "HIGH" in label:
        return -8, "Risk level is high."
    if "LOW" in label:
        return 6, "Risk level is low."
    return 0, "Risk level is moderate."


def _atr_bias(atr: Any, adx: float) -> Bias:
    """Score ATR in the context of ADX."""
    atr_value = _safe_float(atr, 0.0)
    if atr_value <= 0:
        return 0, "ATR is unavailable."
    if adx < 20 and atr_value > 0:
        return -3, f"ATR({atr_value:.2f}) shows volatility without a strong trend."
    return 2, f"ATR({atr_value:.2f}) is factored into position sizing."


def _adx_adjustment(adx: float, trend_score: int) -> Bias:
    """Adjust conviction from ADX strength and trend direction."""
    if adx > 40:
        boost = 12 if trend_score > 0 else -12 if trend_score < 0 else 0
        return boost, f"ADX ({adx:.1f}) shows a very strong trend."
    if adx > 25:
        boost = 8 if trend_score > 0 else -8 if trend_score < 0 else 2
        return boost, f"ADX ({adx:.1f}) confirms a tradable trend."
    if adx >= 20:
        return 3, f"ADX ({adx:.1f}) shows a developing trend."
    return -6, f"ADX ({adx:.1f}) shows a weak trend."


def _pattern_bias(patterns: List[str]) -> Bias:
    """Score detected candlestick pattern names."""
    bullish = [name for name in patterns if name in BULLISH_PATTERNS]
    bearish = [name for name in patterns if name in BEARISH_PATTERNS]
    doji = [name for name in patterns if name == "Doji"]

    if bullish and not bearish:
        joined = ", ".join(bullish)
        return 8, f"Bullish candlestick evidence: {joined}."
    if bearish and not bullish:
        joined = ", ".join(bearish)
        return -8, f"Bearish candlestick evidence: {joined}."
    if bullish and bearish:
        return 0, "Candlestick signals are mixed."
    if doji:
        return -2, "Doji suggests indecision at the current price."
    return 0, "No decisive candlestick pattern."


def _action_from_score(score: float) -> str:
    """Map conviction to Strong Buy … Strong Sell."""
    if score >= 55:
        return "Strong Buy"
    if score >= 35:
        return "Buy"
    if score >= 18:
        return "Accumulate"
    if score > -18:
        return "Hold"
    if score > -35:
        return "Reduce"
    if score > -55:
        return "Sell"
    return "Strong Sell"


def _matches_strong_buy(
    trend: Any,
    rsi: float,
    macd_status: Any,
    fundamental_score: Any,
    news_sentiment: Any,
    adx: float,
) -> bool:
    """True when the original Strong Buy overlay conditions all fire."""
    return (
        "STRONG BULLISH" in _text(trend)
        and "BULLISH" in _text(macd_status)
        and "BEARISH" not in _text(macd_status)
        and 45 <= rsi <= 65
        and _safe_float(fundamental_score, 0.0) > 80
        and "BULLISH" in _text(news_sentiment)
        and adx > 25
    )


def _matches_reduce_setup(
    trend: Any,
    rsi: float,
    macd_status: Any,
    news_sentiment: Any,
) -> bool:
    """True when the original Reduce overlay conditions all fire."""
    trend_label = _text(trend)
    news_label = _text(news_sentiment)
    return (
        "NEUTRAL" in trend_label
        and "BEARISH" in _text(macd_status)
        and rsi > 70
        and ("BEARISH" in news_label or "NEGATIVE" in news_label)
    )


def _holding_period(
    action: str,
    adx: float,
    atr: float,
    fundamental_score: Any,
    risk_level: Any,
) -> str:
    """Pick Intraday / Swing / Position / Long Term from existing rules."""
    high_risk = "HIGH" in _text(risk_level)
    strong_fundamentals = _safe_float(fundamental_score, 50.0) > 80
    high_volatility = _safe_float(atr, 0.0) > 0 and adx < 20 and high_risk

    if action in ("Strong Buy", "Buy") and strong_fundamentals and adx > 25:
        return "Long Term"
    if action in ("Strong Buy", "Buy", "Accumulate") and adx > 25:
        return "Position"
    if action in ("Reduce", "Sell", "Strong Sell") and (high_risk or adx < 20):
        return "Swing"
    if high_volatility:
        return "Intraday"
    if action in ("Accumulate", "Hold") and strong_fundamentals:
        return "Position"
    return "Swing"


def _risk_reward_rating(
    action: str,
    adx: float,
    risk_level: Any,
    risk_reward: Any,
    rsi: float,
) -> str:
    """Rate R/R as Excellent / Good / Average / Poor."""
    rr = _safe_float(risk_reward, 2.0)
    high_risk = "HIGH" in _text(risk_level)
    overbought = rsi > 70
    oversold = rsi < 30

    if action in ("Strong Buy", "Buy") and adx > 25 and rr >= 2 and not high_risk:
        return "Excellent"
    if action in ("Strong Buy", "Buy", "Accumulate") and rr >= 2 and not overbought:
        return "Good"
    if action in ("Sell", "Strong Sell") and adx > 25 and not oversold:
        return "Good"
    if abs(rr) >= 1.5 and action != "Hold":
        return "Average"
    if action == "Hold":
        return "Average"
    return "Poor"


def _probability(confidence: float, reasons_aligned: int, total_signals: int) -> int:
    """Blend confidence and signal agreement into a 15–95 probability."""
    alignment = 100.0 * reasons_aligned / max(total_signals, 1)
    estimate = 0.55 * confidence + 0.35 * alignment + 8
    return int(max(15, min(95, round(estimate))))


def generate_decision(
    trend: Any,
    rsi: Any,
    macd_status: Any,
    bb_signal: Any,
    atr: Any,
    adx: Any,
    volume_status: Any,
    news_sentiment: Any,
    fundamental_score: Any,
    risk_level: Any,
    candlestick_pattern: Any,
    risk_reward: Any = None,
) -> Dict[str, Any]:
    """Combine every available signal into one professional decision.

    Returns a dict with action, confidence, reasons, holding_period,
    probability, and risk_reward_rating.
    """
    rsi_value = _safe_float(rsi, float("nan"))
    adx_value = _safe_float(adx, 0.0)
    atr_value = _safe_float(atr, 0.0)
    patterns = _normalize_patterns(candlestick_pattern)

    trend_score, trend_reason = _trend_bias(trend)
    macd_score, macd_reason = _macd_bias(macd_status)
    rsi_score, rsi_reason = _rsi_bias(rsi_value)
    bb_score, bb_reason = _bb_bias(bb_signal)
    volume_score, volume_reason = _volume_bias(volume_status, trend_score)
    news_score, news_reason = _news_bias(news_sentiment)
    fund_score, fund_reason = _fundamental_bias(fundamental_score)
    risk_score, risk_reason = _risk_bias(risk_level)
    atr_score, atr_reason = _atr_bias(atr_value, adx_value)
    adx_score, adx_reason = _adx_adjustment(adx_value, trend_score)
    pattern_score, pattern_reason = _pattern_bias(patterns)

    components = [
        trend_score,
        macd_score,
        rsi_score,
        bb_score,
        volume_score,
        news_score,
        fund_score,
        risk_score,
        atr_score,
        adx_score,
        pattern_score,
    ]
    reasons = [
        trend_reason,
        macd_reason,
        rsi_reason,
        bb_reason,
        volume_reason,
        news_reason,
        fund_reason,
        risk_reason,
        atr_reason,
        adx_reason,
        pattern_reason,
    ]

    conviction = sum(components)
    action = _action_from_score(conviction)

    # ADX must confirm extreme actions.
    if action == "Strong Buy" and adx_value <= 25:
        action = "Buy" if adx_value >= 20 else "Accumulate"
    if action == "Strong Sell" and adx_value <= 25:
        action = "Sell" if adx_value >= 20 else "Reduce"

    agreement_confidence = int(max(20, min(96, 50 + abs(conviction) * 0.55)))

    if _matches_strong_buy(
        trend, rsi_value, macd_status, fundamental_score, news_sentiment, adx_value
    ):
        action = "Strong Buy"
        confidence = 92
    elif _matches_reduce_setup(trend, rsi_value, macd_status, news_sentiment):
        action = "Reduce"
        confidence = max(62, min(78, agreement_confidence))
    else:
        confidence = agreement_confidence

    aligned = sum(1 for value in components if value > 0)
    if action in ("Reduce", "Sell", "Strong Sell"):
        aligned = sum(1 for value in components if value < 0)

    probability = _probability(confidence, aligned, len(components))
    if action == "Strong Buy" and _matches_strong_buy(
        trend, rsi_value, macd_status, fundamental_score, news_sentiment, adx_value
    ):
        probability = max(probability, 84)

    holding_period = _holding_period(
        action, adx_value, atr_value, fundamental_score, risk_level
    )
    risk_reward_rating = _risk_reward_rating(
        action, adx_value, risk_level, risk_reward, rsi_value
    )

    return {
        "action": action,
        "confidence": int(confidence),
        "reasons": reasons,
        "holding_period": holding_period,
        "probability": int(probability),
        "risk_reward_rating": risk_reward_rating,
        "conviction": conviction,
    }
