"""Technical indicators page shell for StockShield AI v2."""

from __future__ import annotations

from typing import Any

import streamlit as st

from components.metrics import render_metrics


def render_technical_page(result: Any | None = None) -> None:
    """Technical section layout. Displays values supplied by the caller."""
    st.subheader("Technical")
    if result is None:
        st.info("Technical indicators appear after analysis.")
        render_metrics()
        return
    latest = getattr(result, "latest", None)
    sma20 = "—"
    if latest is not None and hasattr(latest, "__contains__") and "SMA20" in latest:
        sma20 = latest["SMA20"]
    render_metrics(
        [
            {"label": "Trend", "value": getattr(result, "trend", "—")},
            {"label": "RSI", "value": getattr(result, "rsi", "—")},
            {"label": "MACD status", "value": getattr(result, "macd_status", "—")},
            {"label": "SMA20", "value": sma20},
        ]
    )
    patterns = getattr(result, "patterns", None)
    st.caption("Patterns: " + (", ".join(patterns) if patterns else "—"))
