"""Reusable Streamlit UI pieces for StockShield AI v2.

These modules are presentation-only. They must not call the analysis pipeline
or change scores, signals, or risk numbers.
"""

from components.charts import render_charts
from components.footer import render_footer
from components.header import render_header
from components.metrics import kpi_items_from_result, render_metrics
from components.sidebar import render_sidebar
from components.tabs import render_tabs

__all__ = [
    "render_charts",
    "render_footer",
    "render_header",
    "kpi_items_from_result",
    "render_metrics",
    "render_sidebar",
    "render_tabs",
]
