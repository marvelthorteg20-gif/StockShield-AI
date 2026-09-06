"""Top-of-page branding for the v2 dashboard."""

from __future__ import annotations

import streamlit as st


def render_header(
    title: str = "StockShield AI",
    subtitle: str = "Professional equity terminal · dark workspace",
) -> None:
    """Render the application header. Does not fetch or compute market data."""
    st.title(title)
    if subtitle:
        st.caption(subtitle)
