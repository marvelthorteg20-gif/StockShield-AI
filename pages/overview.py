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
    render_metrics(result=result)
    if result is None:
        render_charts()
        return
    render_charts(result)
