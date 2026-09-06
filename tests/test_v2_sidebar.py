"""Professional trading sidebar: session status plus AppTest coverage."""

from __future__ import annotations

from datetime import datetime

from streamlit.testing.v1 import AppTest

from components.sidebar import (
    DEFAULT_WATCHLIST,
    GLOBAL_MARKETS,
    MARKET_OVERVIEW,
    PLACEHOLDER_NOTE,
    market_session_status,
)


def test_market_session_status_weekend_open_closed():
    weekend = datetime(2026, 9, 6, 11, 0)  # Sunday
    weekday_open = datetime(2026, 9, 7, 10, 15)  # Monday
    weekday_closed = datetime(2026, 9, 7, 18, 0)
    assert market_session_status(weekend) == "Weekend"
    assert market_session_status(weekday_open) == "Market Open"
    assert market_session_status(weekday_closed) == "Market Closed"


def _sidebar_harness() -> None:
    from components.sidebar import render_sidebar

    render_sidebar()


def test_sidebar_apptest_sections_watchlist_and_placeholders():
    at = AppTest.from_function(_sidebar_harness, default_timeout=30)
    at.run()
    assert not at.exception
    button_labels = [btn.label for btn in at.button]
    assert "Analyze" in button_labels
    for ticker in DEFAULT_WATCHLIST:
        assert ticker in button_labels
    markdown = " ".join(str(item.value) for item in at.markdown)
    captions = " ".join(str(item.value) for item in at.caption)
    blob = markdown + " " + captions
    for heading in (
        "SEARCH",
        "WATCHLIST",
        "GLOBAL MARKETS",
        "MARKET OVERVIEW",
        "MARKET STATUS",
        "SETTINGS",
    ):
        assert heading in blob
    for name in GLOBAL_MARKETS + MARKET_OVERVIEW:
        assert name in blob
    assert PLACEHOLDER_NOTE in captions
    inputs = [box.label for box in at.text_input]
    assert "Stock Search Box" in inputs
    assert "Theme" in [box.label for box in at.selectbox]
    assert "Notifications" in [box.label for box in at.selectbox]


def test_sidebar_watchlist_click_fills_search_box():
    at = AppTest.from_function(_sidebar_harness, default_timeout=30)
    at.run()
    at.button(key="ss_watch_NVDA").click().run()
    assert not at.exception
    assert at.session_state["ss_symbol"] == "NVDA"
    values = [box.value for box in at.text_input]
    assert "NVDA" in values
