"""KPI metric cards for the v2 dashboard."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import streamlit as st

KPI_LABELS: tuple[str, ...] = (
    "Current Price",
    "AI Score",
    "Recommendation",
    "Confidence",
    "Risk Level",
)


def kpi_items_from_result(result: Any) -> list[dict[str, Any]]:
    """Map existing analysis fields onto the five KPI cards.

    Does not recompute scores. Uses ``latest['Close']``, ``score``,
    ``recommendation``, ``confidence``, and ``volatility_level`` as risk level.
    """
    latest = getattr(result, "latest", None)
    price: Any = "—"
    delta: Any = None
    if latest is not None and hasattr(latest, "__contains__") and "Close" in latest:
        price = f"${float(latest['Close']):.2f}"
        today = getattr(result, "today_percent", None)
        if today is not None:
            delta = f"{float(today):+.2f}%"
    return [
        {"label": "Current Price", "value": price, "delta": delta},
        {"label": "AI Score", "value": getattr(result, "score", "—")},
        {"label": "Recommendation", "value": getattr(result, "recommendation", "—")},
        {"label": "Confidence", "value": getattr(result, "confidence", "—")},
        {"label": "Risk Level", "value": getattr(result, "volatility_level", "—")},
    ]


def _placeholder_kpis() -> list[dict[str, Any]]:
    return [{"label": label, "value": "—"} for label in KPI_LABELS]


def render_metrics(
    items: Sequence[Mapping[str, Any]] | None = None,
    *,
    result: Any | None = None,
    columns: int | None = None,
) -> None:
    """Render KPI cards in a responsive ``st.columns`` row.

    Pass ``result`` to fill cards from existing analysis output. Pass ``items``
    to render a custom row. With neither, empty KPI slots are shown.
    """
    if items is None:
        items = kpi_items_from_result(result) if result is not None else _placeholder_kpis()
    count = max(1, int(columns) if columns is not None else max(1, len(items)))
    cols = st.columns(count)
    for index, item in enumerate(items):
        col = cols[index % len(cols)]
        label = str(item.get("label", ""))
        value = item.get("value", "—")
        delta = item.get("delta")
        if delta is None:
            col.metric(label, value)
        else:
            col.metric(label, value, delta)
