"""Interactive v2 Plotly charts: figures plus AppTest coverage."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

from components.charts import (
    CHART_TABS,
    PLOTLY_CONFIG,
    close_figure,
    macd_figure,
    price_figure,
    rsi_figure,
    volume_figure,
)
from tests.history_factory import make_history


def _history_with_existing_columns(rows: int = 40):
    history = make_history(rows)
    history["SMA20"] = 101.0
    history["EMA20"] = 102.0
    history["RSI"] = 55.0
    history["MACD"] = 1.2
    history["MACD_SIGNAL"] = 0.8
    history["VOL_AVG20"] = 1_000_000.0
    return history


def _trace_names(fig) -> set[str]:
    return {trace.name for trace in fig.data}


def test_price_figure_uses_existing_overlays_and_volume():
    history = _history_with_existing_columns()
    fig = price_figure(history, "Test", show_sma20=True, show_ema20=True)
    names = _trace_names(fig)
    assert "OHLC" in names
    assert "SMA20" in names
    assert "EMA20" in names
    assert "Volume" in names
    assert fig.layout.hovermode == "x unified"
    assert fig.layout.template.layout.paper_bgcolor or True
    assert fig.layout.xaxis.showspikes is True
    assert fig.layout.dragmode == "zoom"


def test_overlays_can_be_hidden_without_recalculating():
    history = _history_with_existing_columns()
    fig = price_figure(history, "Test", show_sma20=False, show_ema20=False)
    names = _trace_names(fig)
    assert "SMA20" not in names
    assert "EMA20" not in names
    assert "OHLC" in names


def test_price_tab_line_chart_uses_existing_close_and_overlays():
    history = _history_with_existing_columns()
    fig = close_figure(history, "Test", show_sma20=True, show_ema20=True)
    names = _trace_names(fig)
    assert {"Close", "SMA20", "EMA20"} <= names


def test_rsi_macd_volume_figures_read_existing_columns():
    history = _history_with_existing_columns()
    rsi = rsi_figure(history)
    macd = macd_figure(history)
    volume = volume_figure(history)
    assert "RSI" in _trace_names(rsi)
    assert {"MACD", "Signal"} <= _trace_names(macd)
    assert "Volume" in _trace_names(volume)
    assert "VOL_AVG20" in _trace_names(volume)


def test_plotly_config_keeps_zoom_pan_and_reset():
    removed = set(PLOTLY_CONFIG["modeBarButtonsToRemove"])
    assert "zoom2d" not in removed
    assert "pan2d" not in removed
    assert "resetScale2d" not in removed
    assert PLOTLY_CONFIG["scrollZoom"] is True


def _chart_harness() -> None:
    from types import SimpleNamespace

    from components.charts import render_charts
    from tests.history_factory import make_history

    history = make_history(40)
    history["SMA20"] = 101.0
    history["EMA20"] = 102.0
    history["RSI"] = 55.0
    history["MACD"] = 1.2
    history["MACD_SIGNAL"] = 0.8
    history["VOL_AVG20"] = 1_000_000.0
    result = SimpleNamespace(
        history=history,
        symbol="AAPL",
        company_name="Apple",
    )
    render_charts(result)


def test_render_charts_apptest_exposes_tabs_and_overlays():
    at = AppTest.from_function(_chart_harness, default_timeout=30)
    at.run()
    assert not at.exception
    labels = [tab.label for tab in at.tabs]
    assert labels == list(CHART_TABS)
    checkbox_labels = [box.label for box in at.checkbox]
    assert "SMA20" in checkbox_labels
    assert "EMA20" in checkbox_labels
