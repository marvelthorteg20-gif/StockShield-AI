"""Technical indicator pipeline for StockShield AI.

Public functions keep their historical return shapes so ``app.py`` and
existing tests remain compatible. Yahoo fetches go through
``utils.market_data`` so fundamentals reuse the same payload.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import ADXIndicator, MACD
from ta.volatility import AverageTrueRange, BollingerBands

import config
from analysis.ai_score import compute_ai_score
from analysis.patterns import detect_candlestick_patterns
from analysis.risk import (
    calculate_smart_levels,
    classify_adx_strength,
    classify_volatility,
)
from utils.errors import EmptyDataError
from utils.market_data import get_ticker_bundle

IndicatorResult = Tuple[Any, ...]


def _rating_from_score(score: int) -> str:
    """Map an AI score to the historical star-rating string."""
    if score >= 90:
        return "★★★★★"
    if score >= 80:
        return "★★★★☆"
    if score >= 70:
        return "★★★☆☆"
    if score >= 60:
        return "★★☆☆☆"
    return "★☆☆☆☆"


def _confidence_from_score(score: int) -> str:
    """Map an AI score to HIGH / MEDIUM / LOW confidence labels."""
    if score >= 80:
        return "🟢 HIGH"
    if score >= 60:
        return "🟡 MEDIUM"
    return "🔴 LOW"


def _risk_from_score(score: int, rsi: float, volatility_level: str) -> str:
    """Derive the risk badge from RSI extremes, volatility, and confidence."""
    if rsi > config.RSI_OVERBOUGHT or rsi < config.RSI_OVERSOLD or volatility_level == "🔴 High":
        return "🔴 HIGH"
    if score >= 80 and volatility_level == "🟢 Low":
        return "🟢 LOW"
    if _confidence_from_score(score) == "🟢 HIGH":
        return "🟢 LOW"
    return "🟡 MEDIUM"


def refine_ai_score(
    trend: str,
    rsi: float,
    macd_status: str,
    bb_signal: str,
    volume_status: str,
    volatility_level: str,
    adx_strength: str,
    sentiment: str,
    fundamental_score: int,
) -> Tuple[int, str, str, str]:
    """Blend technicals with news and fundamentals; same return tuple as before."""
    score, _ = compute_ai_score(
        trend=trend,
        rsi=rsi,
        macd_status=macd_status,
        bb_signal=bb_signal,
        volume_status=volume_status,
        volatility_level=volatility_level,
        adx_strength=adx_strength,
        sentiment=sentiment,
        fundamental_score=fundamental_score,
    )
    confidence = _confidence_from_score(score)
    rating = _rating_from_score(score)
    risk = _risk_from_score(score, rsi, volatility_level)
    return score, confidence, rating, risk


def calculate_indicators(symbol: str) -> IndicatorResult:
    """Fetch (cached) Yahoo data and compute the full indicator snapshot.

    Raises:
        InvalidTickerError, EmptyDataError, NetworkError
    """
    bundle = get_ticker_bundle(symbol)
    info: Dict[str, Any] = bundle["info"] or {}
    history: pd.DataFrame = bundle["history"]

    company_name = info.get("longName", symbol)
    sector = info.get("sector", "Unknown")

    if history.empty:
        raise EmptyDataError("No stock data found.")

    history["SMA20"] = history["Close"].rolling(config.SMA_WINDOW).mean()
    history["EMA20"] = history["Close"].ewm(span=config.EMA_WINDOW, adjust=False).mean()

    history["RSI"] = RSIIndicator(
        close=history["Close"],
        window=config.RSI_PERIOD,
    ).rsi()

    macd = MACD(
        history["Close"],
        window_slow=config.MACD_SLOW,
        window_fast=config.MACD_FAST,
        window_sign=config.MACD_SIGNAL,
    )
    history["MACD"] = macd.macd()
    history["MACD_SIGNAL"] = macd.macd_signal()

    bb = BollingerBands(
        close=history["Close"],
        window=config.BB_WINDOW,
        window_dev=config.BB_STD,
    )

    history["BB_UPPER"] = bb.bollinger_hband()
    history["BB_LOWER"] = bb.bollinger_lband()
    history["BB_MIDDLE"] = bb.bollinger_mavg()

    history["VOL_AVG20"] = history["Volume"].rolling(config.VOLUME_AVG_WINDOW).mean()

    atr_indicator = AverageTrueRange(
        high=history["High"],
        low=history["Low"],
        close=history["Close"],
        window=config.ATR_LENGTH,
    )
    history["ATR"] = atr_indicator.average_true_range()

    adx_indicator = ADXIndicator(
        high=history["High"],
        low=history["Low"],
        close=history["Close"],
        window=config.ADX_WINDOW,
    )
    history["ADX"] = adx_indicator.adx()

    latest = history.iloc[-1]

    rsi = latest["RSI"]
    atr = latest["ATR"]
    adx = latest["ADX"]

    if latest["Close"] > latest["EMA20"] > latest["SMA20"]:
        trend = "🟢 STRONG BULLISH"

    elif latest["Close"] > latest["SMA20"]:
        trend = "🟢 BULLISH"

    elif latest["Close"] < latest["EMA20"] < latest["SMA20"]:
        trend = "🔴 STRONG BEARISH"

    else:
        trend = "🟡 NEUTRAL"

    if latest["MACD"] > latest["MACD_SIGNAL"]:
        macd_status = "🟢 Bullish Crossover"

    elif latest["MACD"] < latest["MACD_SIGNAL"]:
        macd_status = "🔴 Bearish Crossover"

    else:
        macd_status = "🟡 Neutral"

    if latest["Close"] > latest["BB_UPPER"]:
        bb_signal = "🔴 Price Above Upper Band (Overbought)"

    elif latest["Close"] < latest["BB_LOWER"]:
        bb_signal = "🟢 Price Below Lower Band (Oversold)"

    else:
        bb_signal = "🟡 Price Inside Bands"

    if latest["Volume"] > latest["VOL_AVG20"]:
        volume_status = "🟢 High Volume"
    else:
        volume_status = "🟡 Low Volume"

    today_change = latest["Close"] - latest["Open"]
    today_percent = (today_change / latest["Open"]) * 100

    support = history["Low"].tail(config.SWING_LOOKBACK).min()
    resistance = history["High"].tail(config.SWING_LOOKBACK).max()

    high_52 = history["High"].max()
    low_52 = history["Low"].min()

    volatility_level = classify_volatility(atr, latest["Close"])
    adx_strength = classify_adx_strength(adx)
    patterns = detect_candlestick_patterns(history)
    smart_levels = calculate_smart_levels(
        entry=float(latest["Close"]),
        atr=float(atr) if atr == atr else 0.0,
        support=float(support),
        resistance=float(resistance),
    )

    score, _ = compute_ai_score(
        trend=trend,
        rsi=rsi,
        macd_status=macd_status,
        bb_signal=bb_signal,
        volume_status=volume_status,
        volatility_level=volatility_level,
        adx_strength=adx_strength,
    )

    confidence = _confidence_from_score(score)
    rating = _rating_from_score(score)
    risk = _risk_from_score(score, rsi, volatility_level)

    if trend == "🟢 STRONG BULLISH":
        if rsi > config.RSI_OVERBOUGHT:
            recommendation = "🟡 HOLD"
            explanation = (
                "• Trend is bullish.\n"
                "• RSI is above 70.\n"
                "• Stock may be overbought.\n"
                "• Wait before buying."
            )
        else:
            recommendation = "🟢 BUY"
            explanation = (
                "• Trend is strongly bullish.\n"
                "• Price is above EMA20 and SMA20.\n"
                f"• RSI: {rsi:.2f}\n"
                f"• {macd_status}\n"
                f"• {bb_signal}\n"
                f"• {volume_status}\n"
                "• Technical indicators support buying."
            )

    elif trend == "🟢 BULLISH":
        recommendation = "🟢 BUY"
        explanation = (
            "• Trend is bullish.\n"
            f"• RSI: {rsi:.2f}\n"
            f"• {macd_status}\n"
            "• Momentum remains positive."
        )

    elif trend == "🔴 STRONG BEARISH":
        if rsi < config.RSI_OVERSOLD:
            recommendation = "🟡 HOLD"
            explanation = (
                "• Trend is bearish.\n"
                "• RSI is below 30.\n"
                "• Stock may be oversold."
            )
        else:
            recommendation = "🔴 SELL"
            explanation = (
                "• Trend is bearish.\n"
                "• Price is below EMA20 and SMA20.\n"
                "• Technical indicators remain weak."
            )

    else:
        recommendation = "🟡 HOLD"
        explanation = (
            "• Trend is neutral.\n"
            "• Wait for a stronger signal."
        )

    return (
        history,
        trend,
        recommendation,
        explanation,
        company_name,
        sector,
        macd_status,
        score,
        confidence,
        rating,
        bb_signal,
        volume_status,
        risk,
        support,
        resistance,
        high_52,
        low_52,
        today_change,
        today_percent,
        atr,
        volatility_level,
        adx,
        adx_strength,
        patterns,
        smart_levels,
    )
