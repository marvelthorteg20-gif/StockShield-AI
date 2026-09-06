"""Portfolio page shell for StockShield AI v2."""

from __future__ import annotations

from typing import Any

import streamlit as st

from components.metrics import render_metrics


def render_portfolio_page(result: Any | None = None) -> None:
    """Position-sizing layout. Displays values supplied by the caller."""
    st.subheader("Portfolio")
    if result is None:
        st.info("Position sizing appears after analysis.")
        render_metrics()
        return
    position = getattr(result, "position", None) or {}
    render_metrics(
        [
            {"label": "Capital", "value": position.get("capital", "—")},
            {"label": "Risk %", "value": position.get("risk_pct", "—")},
            {"label": "Quantity", "value": position.get("quantity", "—")},
            {"label": "Allocation", "value": position.get("allocation_pct", "—")},
        ]
    )
