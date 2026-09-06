"""News sentiment page shell for StockShield AI v2."""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_news_page(result: Any | None = None) -> None:
    """News section layout. Does not fetch headlines."""
    st.subheader("News")
    if result is None:
        st.info("News sentiment appears after analysis.")
        return
    st.write("Overall:", getattr(result, "sentiment", "—"))
    items = getattr(result, "news", None) or []
    for item in items:
        st.markdown(f"- {item}")
