"""Primary navigation tabs for the v2 dashboard."""

from __future__ import annotations

from typing import Any, Sequence

import streamlit as st

DEFAULT_TAB_LABELS: tuple[str, ...] = (
    "Overview",
    "Technical",
    "Fundamentals",
    "News",
    "Reports",
    "Portfolio",
    "Watchlist",
)


def render_tabs(labels: Sequence[str] | None = None) -> list[Any]:
    """Create Streamlit tabs and return the tab context objects."""
    names = list(labels) if labels else list(DEFAULT_TAB_LABELS)
    return list(st.tabs(names))
