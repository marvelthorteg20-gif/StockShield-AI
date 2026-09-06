"""Footer disclaimer for the v2 dashboard."""

from __future__ import annotations

import streamlit as st


def render_footer(
    text: str = "StockShield AI · educational analysis only · not financial advice",
) -> None:
    """Render a compact footer. Presentation only."""
    st.markdown("---")
    st.caption(text)
