"""Metric cards and simple key/value tables for the v2 dashboard."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import streamlit as st


def render_metrics(
    items: Sequence[Mapping[str, Any]] | None = None,
    *,
    columns: int = 4,
) -> None:
    """Render a row of Streamlit metrics from precomputed values.

    Each item may include ``label``, ``value``, and optional ``delta``.
    Missing ``items`` shows a placeholder so pages can mount before analysis.
    """
    if not items:
        st.caption("Metrics will appear after an analysis run.")
        return
    cols = st.columns(max(1, int(columns)))
    for index, item in enumerate(items):
        col = cols[index % len(cols)]
        label = str(item.get("label", ""))
        value = item.get("value", "—")
        delta = item.get("delta")
        if delta is None:
            col.metric(label, value)
        else:
            col.metric(label, value, delta)
