"""Top-of-page branding for the v2 dashboard."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import streamlit as st

VERSION_BADGE = "v2 Development"
_LOGO_PATH = Path(__file__).resolve().parents[1] / "docs" / "assets" / "logo.png"


def _now_label() -> str:
    """Local date/time for the header clock (presentation only)."""
    stamp = datetime.now().astimezone()
    zone = stamp.tzname() or ""
    return f"{stamp.strftime('%Y-%m-%d %H:%M:%S')} {zone}".strip()


def render_header(
    title: str = "StockShield AI",
    subtitle: str = "Professional equity terminal · dark workspace",
) -> None:
    """Render logo/title, live clock, and the v2 development badge."""
    brand, clock, badge = st.columns([3.2, 2.2, 1.6])
    with brand:
        logo_col, title_col = st.columns([1, 5])
        with logo_col:
            if _LOGO_PATH.is_file():
                st.image(str(_LOGO_PATH), width=52)
            else:
                st.markdown("## 📈")
        with title_col:
            st.markdown(f"### {title}")
            if subtitle:
                st.caption(subtitle)
    with clock:
        st.markdown(f"**{_now_label()}**")
        st.caption("Local date / time")
    with badge:
        st.markdown(
            f"""
            <div style="
                display:inline-block;
                margin-top:0.35rem;
                padding:0.35rem 0.7rem;
                border-radius:999px;
                background:#134e4a;
                color:#99f6e4;
                font-size:0.85rem;
                font-weight:600;
                letter-spacing:0.02em;
            ">{VERSION_BADGE}</div>
            """,
            unsafe_allow_html=True,
        )
