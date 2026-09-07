"""Fundamentals page shell for StockShield AI v2."""

from __future__ import annotations

from typing import Any

import streamlit as st

from components.metrics import render_metrics


def render_fundamentals_page(result: Any | None = None) -> None:
    """Fundamentals section layout. Displays values supplied by the caller."""
    st.subheader("Fundamentals")
    if result is None:
        st.info("Fundamentals appear after analysis.")
        render_metrics()
        return
    render_metrics(
        [
            {"label": "Market cap", "value": getattr(result, "market_cap", "—")},
            {"label": "P/E", "value": getattr(result, "pe_ratio", "—")},
            {"label": "EPS", "value": getattr(result, "eps", "—")},
            {
                "label": "Fundamental score",
                "value": getattr(result, "fundamental_score", "—"),
            },
        ]
    )
