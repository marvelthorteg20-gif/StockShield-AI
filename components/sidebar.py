"""Sidebar controls for the v2 dashboard."""

from __future__ import annotations

from typing import Any

import streamlit as st

import config


def render_sidebar(
    default_symbol: str = "AAPL",
    default_capital: float = 10000.0,
    default_risk_pct: float | None = None,
) -> dict[str, Any]:
    """Draw sidebar inputs and return their values.

    Returns a dict of UI state only. Callers decide when to run analysis.
    """
    risk_default = float(config.RISK_PERCENT if default_risk_pct is None else default_risk_pct)
    with st.sidebar:
        st.header("Controls")
        symbol = st.text_input("Stock Symbol", value=default_symbol).strip().upper()
        capital = st.number_input(
            "Capital",
            min_value=100.0,
            value=float(default_capital),
            step=100.0,
        )
        risk_pct = st.number_input(
            "Risk %",
            min_value=0.1,
            max_value=10.0,
            value=risk_default,
            step=0.1,
        )
        analyze = st.button("Analyze", type="primary", use_container_width=True)
        st.markdown("---")
        st.caption("Yahoo Finance · Alpha Vantage news")
    return {
        "symbol": symbol,
        "capital": float(capital),
        "risk_pct": float(risk_pct),
        "analyze": bool(analyze),
    }
