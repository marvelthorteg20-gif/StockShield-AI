"""Reports / export page shell for StockShield AI v2."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_reports_page(result: Any | None = None) -> None:
    """Export section layout. Does not write JSON, CSV, or PDF yet."""
    st.subheader("Reports")
    if result is None:
        st.info("Export buttons appear after analysis.")
        return
    symbol = getattr(result, "symbol", "report")
    st.caption(f"Export placeholders for {symbol}. Existing exporters stay in utils.export_report.")
