"""Interactive Plotly trading charts for StockShield AI v2.

Figures read columns already present on the analysis dataframe. They do not
call the pipeline or recompute SMA, EMA, RSI, or MACD.
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

CHART_TABS: tuple[str, ...] = ("Price", "RSI", "MACD", "Volume")

DARK_LAYOUT: dict[str, Any] = dict(
    template="plotly_dark",
    paper_bgcolor="#0e1420",
    plot_bgcolor="#0e1420",
    font=dict(color="#d1d4dc", family="IBM Plex Sans, Segoe UI, sans-serif"),
    margin=dict(l=48, r=16, t=44, b=28),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1c2333", font_size=12),
    dragmode="zoom",
)

PLOTLY_CONFIG: dict[str, Any] = {
    "displaylogo": False,
    "scrollZoom": True,
    "displayModeBar": True,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"],
}

_OHLC = ("Open", "High", "Low", "Close")


def _apply_crosshair(fig: go.Figure) -> go.Figure:
    """Enable hover tooltips, spike crosshair, and zoom-friendly axes."""
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#1b2433",
        showspikes=True,
        spikemode="across+marker",
        spikesnap="cursor",
        spikethickness=1,
        spikedash="dot",
        spikecolor="#8b9bb4",
        rangeslider_visible=False,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#1b2433",
        zeroline=False,
        side="right",
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        spikethickness=1,
        spikedash="dot",
        spikecolor="#8b9bb4",
    )
    fig.update_layout(
        **DARK_LAYOUT,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
        xaxis=dict(fixedrange=False),
        yaxis=dict(fixedrange=False),
        modebar=dict(orientation="v"),
    )
    return fig


def _history_frame(history: Any) -> pd.DataFrame | None:
    if history is None or getattr(history, "empty", True):
        return None
    if not set(_OHLC).issubset(history.columns):
        return None
    return history


def price_figure(
    history: pd.DataFrame,
    title: str,
    *,
    show_sma20: bool = True,
    show_ema20: bool = True,
) -> go.Figure:
    """Candlestick + volume with optional existing SMA20/EMA20 overlays."""
    data = history
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.74, 0.26],
    )
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="OHLC",
            increasing_line_color="#26a69a",
            decreasing_line_color="#ef5350",
            increasing_fillcolor="#26a69a",
            decreasing_fillcolor="#ef5350",
            whiskerwidth=0.8,
        ),
        row=1,
        col=1,
    )
    if show_sma20 and "SMA20" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["SMA20"],
                name="SMA20",
                line=dict(color="#42a5f5", width=1.5),
            ),
            row=1,
            col=1,
        )
    if show_ema20 and "EMA20" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["EMA20"],
                name="EMA20",
                line=dict(color="#f0b429", width=1.5),
            ),
            row=1,
            col=1,
        )
    if "Volume" in data.columns:
        colors = [
            "#26a69a" if close >= open_ else "#ef5350"
            for open_, close in zip(data["Open"], data["Close"])
        ]
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data["Volume"],
                name="Volume",
                marker_color=colors,
                marker_line_width=0,
                opacity=0.85,
            ),
            row=2,
            col=1,
        )
    _apply_crosshair(fig)
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#d1d4dc")),
        height=520,
    )
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Vol", row=2, col=1)
    return fig


def rsi_figure(history: pd.DataFrame, title: str = "RSI") -> go.Figure:
    """Plot the existing RSI column."""
    fig = go.Figure()
    if "RSI" not in history.columns:
        fig.update_layout(title="RSI unavailable", height=360, **DARK_LAYOUT)
        return fig
    fig.add_trace(
        go.Scatter(
            x=history.index,
            y=history["RSI"],
            name="RSI",
            line=dict(color="#ce93d8", width=1.6),
        )
    )
    fig.add_hline(y=70, line_dash="dot", line_color="#ef5350", opacity=0.7)
    fig.add_hline(y=30, line_dash="dot", line_color="#26a69a", opacity=0.7)
    _apply_crosshair(fig)
    fig.update_layout(title=dict(text=title, font=dict(size=15)), height=360)
    fig.update_yaxes(title_text="RSI", range=[0, 100])
    return fig


def macd_figure(history: pd.DataFrame, title: str = "MACD") -> go.Figure:
    """Plot existing MACD and signal-line columns."""
    fig = go.Figure()
    if "MACD" not in history.columns:
        fig.update_layout(title="MACD unavailable", height=360, **DARK_LAYOUT)
        return fig
    fig.add_trace(
        go.Scatter(
            x=history.index,
            y=history["MACD"],
            name="MACD",
            line=dict(color="#42a5f5", width=1.6),
        )
    )
    if "MACD_SIGNAL" in history.columns:
        fig.add_trace(
            go.Scatter(
                x=history.index,
                y=history["MACD_SIGNAL"],
                name="Signal",
                line=dict(color="#f0b429", width=1.4),
            )
        )
    _apply_crosshair(fig)
    fig.update_layout(title=dict(text=title, font=dict(size=15)), height=360)
    fig.update_yaxes(title_text="MACD")
    return fig


def volume_figure(history: pd.DataFrame, title: str = "Volume") -> go.Figure:
    """Plot existing volume bars (and VOL_AVG20 when already present)."""
    fig = go.Figure()
    if "Volume" not in history.columns:
        fig.update_layout(title="Volume unavailable", height=360, **DARK_LAYOUT)
        return fig
    colors = [
        "#26a69a" if close >= open_ else "#ef5350"
        for open_, close in zip(history["Open"], history["Close"])
    ]
    fig.add_trace(
        go.Bar(
            x=history.index,
            y=history["Volume"],
            name="Volume",
            marker_color=colors,
            marker_line_width=0,
            opacity=0.9,
        )
    )
    if "VOL_AVG20" in history.columns:
        fig.add_trace(
            go.Scatter(
                x=history.index,
                y=history["VOL_AVG20"],
                name="VOL_AVG20",
                line=dict(color="#90caf9", width=1.4),
            )
        )
    _apply_crosshair(fig)
    fig.update_layout(title=dict(text=title, font=dict(size=15)), height=360)
    fig.update_yaxes(title_text="Volume")
    return fig


def _show_figure(fig: go.Figure) -> None:
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


def render_charts(
    result: Any | None = None,
    *,
    show_classic: bool = True,
) -> None:
    """Render Price / RSI / MACD / Volume tabs from existing history columns."""
    if result is None:
        st.info("Interactive charts load after analysis.")
        return

    history = _history_frame(getattr(result, "history", None))
    if history is None:
        st.error("Candlestick data is incomplete.")
        return

    symbol = getattr(result, "symbol", "")
    company = getattr(result, "company_name", "")
    title = " · ".join(part for part in (symbol, company) if part) or "Price"

    overlay_l, overlay_r, _ = st.columns([1, 1, 3])
    with overlay_l:
        show_sma20 = st.checkbox("SMA20", value=True, key="ss_overlay_sma20")
    with overlay_r:
        show_ema20 = st.checkbox("EMA20", value=True, key="ss_overlay_ema20")

    price_tab, rsi_tab, macd_tab, volume_tab = st.tabs(list(CHART_TABS))
    with price_tab:
        _show_figure(
            price_figure(history, title, show_sma20=show_sma20, show_ema20=show_ema20)
        )
    with rsi_tab:
        if "RSI" in history.columns:
            _show_figure(rsi_figure(history, f"{title} · RSI"))
        else:
            st.info("RSI column is not on this dataframe.")
    with macd_tab:
        if "MACD" in history.columns:
            _show_figure(macd_figure(history, f"{title} · MACD"))
        else:
            st.info("MACD column is not on this dataframe.")
    with volume_tab:
        if "Volume" in history.columns:
            _show_figure(volume_figure(history, f"{title} · Volume"))
        else:
            st.info("Volume column is not on this dataframe.")

    if show_classic:
        from utils.plotly_charts import candlestick_figure

        with st.expander("Classic chart (fallback)", expanded=False):
            _show_figure(candlestick_figure(history, title))
