"""Professional trading-terminal sidebar for StockShield AI v2."""

from __future__ import annotations

import os
from datetime import datetime, time
from typing import Any, Mapping

import streamlit as st

import config

DEFAULT_WATCHLIST: tuple[str, ...] = ("AAPL", "MSFT", "NVDA", "TSLA", "GOOGL")

GLOBAL_MARKETS: tuple[str, ...] = (
    "S&P 500",
    "NASDAQ",
    "Dow Jones",
    "NIFTY 50",
    "SENSEX",
)

MARKET_OVERVIEW: tuple[str, ...] = (
    "Gold",
    "Bitcoin",
    "USD Index",
    "Oil",
)

PLACEHOLDER_NOTE = "placeholder — live quote unavailable"


def market_session_status(now: datetime | None = None) -> str:
    """Classify the session from the user's local weekday and clock.

    Weekends are ``Weekend``. Weekdays 09:30–16:00 local are ``Market Open``;
    other weekday hours are ``Market Closed``.
    """
    stamp = now or datetime.now().astimezone()
    if stamp.weekday() >= 5:
        return "Weekend"
    clock = stamp.time()
    if time(9, 30) <= clock < time(16, 0):
        return "Market Open"
    return "Market Closed"


def _section_banner(title: str) -> None:
    st.markdown(f"**{title}**")
    st.caption("━" * 22)


def _quote_line(name: str, quotes: Mapping[str, Any] | None) -> None:
    payload = (quotes or {}).get(name) if quotes else None
    if isinstance(payload, Mapping) and payload.get("display"):
        st.metric(name, str(payload["display"]))
        return
    st.markdown(f"{name}: —")
    st.caption(PLACEHOLDER_NOTE)


def _load_live_quotes() -> dict[str, Any]:
    """Lazy Yahoo snapshots. Skipped under pytest so AppTests stay offline."""
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return {}
    try:
        from utils.market_snapshots import fetch_market_snapshots

        return fetch_market_snapshots() or {}
    except Exception:
        return {}


def render_sidebar(
    default_symbol: str = "AAPL",
    default_capital: float = 10000.0,
    default_risk_pct: float | None = None,
    quotes: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Draw the collapsible trading sidebar and return Analyze controls.

    Capital and risk widgets stay in Search so existing analysis still runs.
    """
    risk_default = float(config.RISK_PERCENT if default_risk_pct is None else default_risk_pct)
    live_quotes = dict(quotes) if quotes is not None else _load_live_quotes()
    watch_clicked: str | None = None

    with st.sidebar:
        st.caption("Click « at the top to collapse this terminal pane.")
        pending = st.session_state.pop("ss_watchlist_pick", None)
        if pending:
            st.session_state["ss_symbol"] = str(pending).upper()
        if "ss_symbol" not in st.session_state:
            st.session_state["ss_symbol"] = default_symbol

        with st.expander("🔍  SEARCH", expanded=True):
            _section_banner("🔍 SEARCH")
            symbol = st.text_input(
                "Stock Search Box",
                key="ss_symbol",
                help="Yahoo Finance symbol",
            ).strip().upper()
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

        with st.expander("⭐  WATCHLIST", expanded=True):
            _section_banner("⭐ WATCHLIST")
            for ticker in DEFAULT_WATCHLIST:
                if st.button(ticker, key=f"ss_watch_{ticker}", use_container_width=True):
                    watch_clicked = ticker
                    st.session_state["ss_watchlist_pick"] = ticker

        with st.expander("🌍  GLOBAL MARKETS", expanded=True):
            _section_banner("🌍 GLOBAL MARKETS")
            for name in GLOBAL_MARKETS:
                _quote_line(name, live_quotes)

        with st.expander("💰  MARKET OVERVIEW", expanded=False):
            _section_banner("💰 MARKET OVERVIEW")
            for name in MARKET_OVERVIEW:
                _quote_line(name, live_quotes)

        status = market_session_status()
        with st.expander("🔥  MARKET STATUS", expanded=True):
            _section_banner("🔥 MARKET STATUS")
            st.metric("Session", status)
            st.caption("Derived from local weekday and time (09:30–16:00).")

        with st.expander("⚙  SETTINGS", expanded=False):
            _section_banner("⚙ SETTINGS")
            st.selectbox("Theme", ["Dark (terminal)"], index=0)
            st.caption("Theme — placeholder")
            st.selectbox("Notifications", ["Off"], index=0)
            st.caption("Notifications — placeholder")
            st.markdown("**About**")
            st.caption("StockShield AI v2 Development. Educational analysis only.")

        st.caption("Yahoo Finance · Alpha Vantage news")

        if watch_clicked:
            st.rerun()

    return {
        "symbol": symbol,
        "capital": float(capital),
        "risk_pct": float(risk_pct),
        "analyze": bool(analyze),
        "watchlist": list(DEFAULT_WATCHLIST),
        "market_status": status,
    }
