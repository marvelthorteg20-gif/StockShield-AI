"""Shared analysis pipeline for the CLI and Streamlit dashboard.

This module composes existing engines. It does not change indicator math or
decision-engine rules; it only gathers their outputs in one place.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

import config
from utils.ai_summary import generate_ai_summary
from utils.decision_engine import generate_decision
from utils.fundamentals import get_fundamentals
from utils.indicators import calculate_indicators, refine_ai_score
from utils.institutional import detect_institutional_signals
from utils.levels import calculate_sr_engine
from utils.multi_timeframe import analyze_timeframes
from utils.news import get_news_sentiment
from utils.position_sizing import calculate_position, parse_capital
from utils.star_decision import rate_star_decision
from utils.swing_trade import build_swing_plan

INSTITUTIONAL_LABELS: Tuple[Tuple[str, str], ...] = (
    ("unusual_volume", "Unusual Volume"),
    ("breakout", "Breakout"),
    ("breakdown", "Breakdown"),
    ("near_52w_high", "Near 52 Week High"),
    ("near_52w_low", "Near 52 Week Low"),
    ("gap_up", "Gap Up"),
    ("gap_down", "Gap Down"),
)


@dataclass
class AnalysisResult:
    """Complete StockShield snapshot used by every front-end."""

    symbol: str
    history: pd.DataFrame
    latest: pd.Series
    company_name: str
    sector: str
    trend: str
    recommendation: str
    explanation: str
    macd_status: str
    score: int
    confidence: str
    rating: str
    bb_signal: str
    volume_status: str
    risk: str
    support: float
    resistance: float
    high_52: float
    low_52: float
    today_change: float
    today_percent: float
    atr: float
    volatility_level: str
    adx: float
    adx_strength: str
    patterns: List[str]
    smart_levels: Dict[str, float]
    market_cap: Any
    pe_ratio: Any
    eps: Any
    dividend: Any
    beta: Any
    revenue: Any
    profit_margin: float
    fundamental_score: int
    news: List[str]
    sentiment: str
    rsi: float
    decision: Dict[str, Any]
    timeframes: Dict[str, Any]
    institutional: Dict[str, Dict[str, Any]]
    sr_levels: List[Dict[str, Any]]
    star: Dict[str, Any]
    swing: Dict[str, Any]
    position: Dict[str, Any]
    summary: str
    target_price: float
    upside: float
    extras: Dict[str, Any] = field(default_factory=dict)

    def export_payload(self) -> Dict[str, Any]:
        """JSON-friendly report body (same keys the CLI already exports)."""
        return {
            "symbol": self.symbol,
            "company": self.company_name,
            "price": float(self.latest["Close"]),
            "trend": self.trend,
            "rsi": float(self.rsi),
            "macd_status": self.macd_status,
            "ai_score": self.score,
            "recommendation": self.recommendation,
            "decision": self.decision,
            "star_rating": self.star["display"],
            "timeframes": self.timeframes,
            "institutional": self.institutional,
            "support_resistance": self.sr_levels,
            "swing": self.swing,
            "position": self.position,
            "summary": self.summary,
            "news_sentiment": self.sentiment,
            "fundamental_score": self.fundamental_score,
        }


def run_analysis(
    symbol: str,
    capital: float = 10000.0,
    risk_pct: Optional[float] = None,
) -> AnalysisResult:
    """Run the full StockShield stack for *symbol*.

    *risk_pct* defaults to ``config.RISK_PERCENT`` (2.0) so the CLI output
    stays identical when the caller omits it.
    """
    ticker = str(symbol).strip().upper()
    risk = float(config.RISK_PERCENT if risk_pct is None else risk_pct)
    capital_value = parse_capital(capital, default=10000.0)

    (
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
        risk_level,
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
    ) = calculate_indicators(ticker)

    (
        market_cap,
        pe_ratio,
        eps,
        dividend,
        beta,
        revenue,
        profit_margin,
        fundamental_score,
    ) = get_fundamentals(ticker)

    news, sentiment = get_news_sentiment(ticker)

    latest = history.iloc[-1]
    rsi = latest["RSI"]

    score, confidence, rating, risk_level = refine_ai_score(
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

    decision = generate_decision(
        trend=trend,
        rsi=rsi,
        macd_status=macd_status,
        bb_signal=bb_signal,
        atr=atr,
        adx=adx,
        volume_status=volume_status,
        news_sentiment=sentiment,
        fundamental_score=fundamental_score,
        risk_level=risk_level,
        candlestick_pattern=patterns,
        risk_reward=smart_levels["risk_reward"],
    )

    timeframes = analyze_timeframes(history)
    institutional = detect_institutional_signals(
        history,
        high_52=high_52,
        low_52=low_52,
        support=support,
        resistance=resistance,
    )
    sr_levels = calculate_sr_engine(history)
    star = rate_star_decision(decision)
    swing = build_swing_plan(
        entry=smart_levels["entry"],
        stop_loss=smart_levels["stop_loss"],
        target1=smart_levels["target1"],
        target2=smart_levels["target2"],
        atr=atr,
        probability=decision["probability"],
    )
    position = calculate_position(
        capital=capital_value,
        entry=swing["entry"],
        stop_loss=swing["stop_loss"],
        risk_pct=risk,
    )
    summary = generate_ai_summary(
        company_name=company_name,
        trend=trend,
        rsi=rsi,
        macd_status=macd_status,
        fundamental_score=fundamental_score,
        atr=atr,
        adx=adx,
        risk_level=risk_level,
        sentiment=sentiment,
        star_label=star["label"],
        alignment=timeframes["alignment"],
        institutional_signals=institutional,
        volatility_level=volatility_level,
    )

    close = float(latest["Close"])
    target_price = float(resistance)
    upside = ((target_price - close) / close) * 100 if close else 0.0

    return AnalysisResult(
        symbol=ticker,
        history=history,
        latest=latest,
        company_name=company_name,
        sector=sector,
        trend=trend,
        recommendation=recommendation,
        explanation=explanation,
        macd_status=macd_status,
        score=int(score),
        confidence=confidence,
        rating=rating,
        bb_signal=bb_signal,
        volume_status=volume_status,
        risk=risk_level,
        support=float(support),
        resistance=float(resistance),
        high_52=float(high_52),
        low_52=float(low_52),
        today_change=float(today_change),
        today_percent=float(today_percent),
        atr=float(atr) if atr == atr else 0.0,
        volatility_level=volatility_level,
        adx=float(adx) if adx == adx else 0.0,
        adx_strength=adx_strength,
        patterns=list(patterns or []),
        smart_levels=smart_levels,
        market_cap=market_cap,
        pe_ratio=pe_ratio,
        eps=eps,
        dividend=dividend,
        beta=beta,
        revenue=revenue,
        profit_margin=float(profit_margin or 0),
        fundamental_score=int(fundamental_score),
        news=list(news or []),
        sentiment=sentiment,
        rsi=float(rsi) if rsi == rsi else 0.0,
        decision=decision,
        timeframes=timeframes,
        institutional=institutional,
        sr_levels=sr_levels,
        star=star,
        swing=swing,
        position=position,
        summary=summary,
        target_price=target_price,
        upside=upside,
    )
