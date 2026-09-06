"""Chart placeholders for the v2 dashboard."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_charts(result: Any | None = None) -> None:
    """Reserve chart space. Does not build figures or call analysis helpers.

    Plotly wiring stays in existing ``utils.plotly_charts`` until the v2 shell
    is connected to ``streamlit_app.py``.
    """
    left, right = st.columns((2, 1))
    with left:
        st.subheader("Live Candlestick Chart")
        if result is None:
            st.info("Chart loads after analysis.")
        else:
            st.caption(f"Ready for {getattr(result, 'symbol', 'symbol')} candlestick.")
    with right:
        st.subheader("AI Score Gauge")
        if result is None:
            st.info("Gauge loads after analysis.")
        else:
            st.caption("Ready for AI score gauge.")
