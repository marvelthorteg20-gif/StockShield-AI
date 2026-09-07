"""Consume existing run_analysis() output to rank sector candidates.

This module does not change indicator math, the pipeline, or the decision engine.
"""

from __future__ import annotations

import os
from typing import Any, Callable, Sequence

ANALYZE_KEY = "ss_ip_analyze_fn"
RECS_KEY = "ss_ip_stock_recs"
NARRATED_KEY = "ss_ip_stock_recs_narrated"
SUGGESTIONS_KEY = "ss_ip_stock_suggestions_requested"
PROFILE_KEY = "ss_ip_profile"
TOP_N = 5

SECTOR_CANDIDATES: dict[str, tuple[str, ...]] = {
    "Technology": ("AAPL", "MSFT", "NVDA"),
    "Banking": ("JPM", "BAC", "WFC"),
    "Healthcare": ("JNJ", "PFE", "LLY"),
    "Index Funds": ("SPY", "QQQ", "VTI"),
    "Gold": ("GLD",),
    "AI & Semiconductor": ("NVDA", "AVGO", "AMD"),
    "Cash": (),
}


def candidates_for_allocation(slices: Sequence[tuple[str, int]]) -> list[tuple[str, str]]:
    """Return unique (sleeve, ticker) pairs for sleeves with a positive weight."""
    seen: set[str] = set()
    pairs: list[tuple[str, str]] = []
    for sleeve, weight in slices:
        if int(weight or 0) <= 0:
            continue
        for ticker in SECTOR_CANDIDATES.get(sleeve, ()):
            symbol = str(ticker).upper()
            if symbol in seen:
                continue
            seen.add(symbol)
            pairs.append((sleeve, symbol))
    return pairs


def capital_from_profile(profile: dict[str, Any] | None) -> float:
    """Parse the wizard Budget string (₹10,000) into a float capital."""
    if not isinstance(profile, dict):
        return 10_000.0
    digits = "".join(ch for ch in str(profile.get("Budget") or "") if ch.isdigit())
    if not digits:
        return 10_000.0
    return float(digits)


def why_from_result(result: Any, sleeve: str) -> str:
    """Explain a pick using fields the existing engine already computed."""
    ticker = str(getattr(result, "symbol", "") or "")
    company = str(getattr(result, "company_name", "") or ticker)
    score = getattr(result, "score", "—")
    rec = getattr(result, "recommendation", "—")
    confidence = getattr(result, "confidence", "—")
    trend = getattr(result, "trend", "—")
    sentiment = getattr(result, "sentiment", "—")
    explanation = str(getattr(result, "explanation", "") or "").replace("\n", " ").strip()
    summary = str(getattr(result, "summary", "") or "").strip()
    rsi = getattr(result, "rsi", None)
    rsi_bit = ""
    if rsi is not None:
        try:
            rsi_bit = f" RSI {float(rsi):.0f}."
        except (TypeError, ValueError):
            rsi_bit = ""
    engine_note = explanation or summary or "No extra narrative was attached to this snapshot."
    return (
        f"{ticker} sits in your {sleeve} sleeve. "
        f"The existing engine scored {company} at {score}/100 "
        f"with {rec} and {confidence} confidence. "
        f"Trend {trend}; news {sentiment}.{rsi_bit} "
        f"{engine_note}"
    )


def row_from_result(result: Any, sleeve: str) -> dict[str, Any]:
    """Flatten existing AnalysisResult fields for the recommendation board."""
    latest = getattr(result, "latest", None)
    price: Any = None
    if latest is not None and hasattr(latest, "__contains__") and "Close" in latest:
        price = float(latest["Close"])
    return {
        "ticker": str(getattr(result, "symbol", "") or ""),
        "company": str(getattr(result, "company_name", "") or ""),
        "price": price,
        "score": int(getattr(result, "score", 0) or 0),
        "recommendation": str(getattr(result, "recommendation", "") or ""),
        "confidence": str(getattr(result, "confidence", "") or ""),
        "sleeve": sleeve,
        "why": why_from_result(result, sleeve),
        "trend": str(getattr(result, "trend", "") or ""),
        "rsi": getattr(result, "rsi", None),
        "sentiment": str(getattr(result, "sentiment", "") or ""),
        "explanation": str(getattr(result, "explanation", "") or ""),
        "summary": str(getattr(result, "summary", "") or ""),
    }


def sort_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    """Highest existing AI Score first."""
    return sorted(rows, key=lambda row: (-int(row.get("score") or 0), str(row.get("ticker") or "")))


def generate_recommendations(
    slices: Sequence[tuple[str, int]],
    *,
    analyze: Callable[..., Any] | None = None,
    capital: float = 10_000.0,
    risk_pct: float = 2.0,
) -> list[dict[str, Any]]:
    """Run the existing analyzer on each candidate and rank by AI Score."""
    analyzer = analyze
    if analyzer is None:
        from utils.pipeline import run_analysis

        analyzer = run_analysis
    rows: list[dict[str, Any]] = []
    for sleeve, ticker in candidates_for_allocation(slices):
        try:
            result = analyzer(ticker, capital=float(capital), risk_pct=float(risk_pct))
        except Exception:
            continue
        if result is None:
            continue
        rows.append(row_from_result(result, sleeve))
    return sort_rows(rows)


def recommendations_narrative(rows: Sequence[dict[str, Any]], *, limit: int = TOP_N) -> str:
    """Investor Partner copy explaining the ranked existing-engine output."""
    top = list(rows)[: max(1, int(limit))]
    if not top:
        return (
            "I tried the existing StockShield engine on your sector candidates, "
            "but no snapshots were available to rank."
        )
    lines = [
        "I mapped your allocation to sector candidates, ran the existing StockShield "
        "engine on each name, and ranked the results by AI Score.",
        "These are not trade tickets — they reuse the same scores you would see after Analyze.",
        "",
    ]
    for row in top:
        lines.append(
            f"• {row.get('ticker')} — {row.get('why')}"
        )
    return "\n".join(lines)


def maybe_build_suggestions(
    *,
    analyze: Callable[..., Any] | None = None,
    capital: float | None = None,
    risk_pct: float | None = None,
) -> list[dict[str, Any]]:
    """If the Generate button was clicked, fill session_state with ranked rows."""
    import streamlit as st

    import config
    from components.portfolio_builder import allocation_from_profile

    if not st.session_state.get(SUGGESTIONS_KEY):
        existing = st.session_state.get(RECS_KEY)
        return list(existing) if isinstance(existing, list) else []
    cached = st.session_state.get(RECS_KEY)
    if isinstance(cached, list):
        return cached
    analyzer = analyze or st.session_state.get(ANALYZE_KEY)
    if analyzer is None:
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return []
        from utils.pipeline import run_analysis

        analyzer = run_analysis
    profile = st.session_state.get(PROFILE_KEY) or {}
    slices = allocation_from_profile(profile if isinstance(profile, dict) else {})
    capital_value = float(capital) if capital is not None else capital_from_profile(profile)
    risk_value = float(config.RISK_PERCENT if risk_pct is None else risk_pct)
    rows = generate_recommendations(
        slices,
        analyze=analyzer,
        capital=capital_value,
        risk_pct=risk_value,
    )
    st.session_state[RECS_KEY] = rows
    return rows
