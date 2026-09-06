"""Overview page shell for StockShield AI v2."""

from __future__ import annotations

from typing import Any

import streamlit as st

from components.charts import render_charts
from components.header import render_header
from components.metrics import render_metrics


def render_overview_page(result: Any | None = None) -> None:
    """Company snapshot layout. Does not run analysis."""
    render_header()
    st.subheader("Overview")
    if result is None:
        render_metrics()
        render_charts()
        return
    render_metrics(
        [
            {"label": "Company", "value": getattr(result, "company_name", "—")},
            {"label": "Sector", "value": getattr(result, "sector", "—")},
            {"label": "Rating", "value": getattr(result, "rating", "—")},
            {"label": "Confidence", "value": getattr(result, "confidence", "—")},
        ]
    )
    render_charts(result)
