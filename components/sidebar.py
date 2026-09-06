"""Sidebar controls for the v2 dashboard."""

from __future__ import annotations

from typing import Any

import streamlit as st

import config

NAV_ITEMS: tuple[str, ...] = (
    "Search Stock",
    "Watchlist",
    "Portfolio",
    "Markets",
    "News",
    "Settings",
)


def render_sidebar(
    default_symbol: str = "AAPL",
    default_capital: float = 10000.0,
    default_risk_pct: float | None = None,
) -> dict[str, Any]:
    """Draw sidebar search plus placeholder nav sections.

    Returns UI state only. Callers decide when to run analysis. Capital and
    risk widgets stay so existing Analyze behavior is unchanged.
    """
    risk_default = float(config.RISK_PERCENT if default_risk_pct is None else default_risk_pct)
    with st.sidebar:
        st.header("Workspace")
        section = st.radio("Navigate", NAV_ITEMS, index=0)

        st.markdown("#### Search Stock")
        symbol = st.text_input("Ticker", value=default_symbol, help="Yahoo Finance symbol").strip().upper()
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
        st.markdown("#### Watchlist")
        st.caption("Placeholder — saved tickers will land in a later v2 slice.")
        st.markdown("#### Portfolio")
        st.caption("Placeholder — holdings view will land in a later v2 slice.")
        st.markdown("#### Markets")
        st.caption("Placeholder — market overview will land in a later v2 slice.")
        st.markdown("#### News")
        st.caption("Placeholder — headline feed will land in a later v2 slice.")
        st.markdown("#### Settings")
        st.caption("Placeholder — preferences will land in a later v2 slice.")

        if section != "Search Stock":
            st.info(f"{section} is a placeholder. Use Search Stock to run analysis.")

        st.markdown("---")
        st.caption("Yahoo Finance · Alpha Vantage news")
    return {
        "symbol": symbol,
        "capital": float(capital),
        "risk_pct": float(risk_pct),
        "analyze": bool(analyze),
        "section": section,
    }
