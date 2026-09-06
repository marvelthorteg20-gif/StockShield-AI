"""Plotly figures for the StockShield dashboard (no Streamlit import)."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DARK_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#0e1420",
    plot_bgcolor="#0e1420",
    font=dict(color="#d1d4dc", family="IBM Plex Sans, Segoe UI, sans-serif"),
    margin=dict(l=48, r=16, t=44, b=28),
    hovermode="x unified",
    hoverlabel=dict(bgcolor="#1c2333", font_size=12),
)


def candlestick_figure(history: pd.DataFrame, title: str) -> go.Figure:
    """TradingView-style dark candlestick with volume and existing overlays."""
    data = history.copy()
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
    if {"BB_UPPER", "BB_LOWER"}.issubset(data.columns):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["BB_UPPER"],
                name="BB Upper",
                line=dict(color="rgba(139,155,180,0.45)", width=1, dash="dot"),
                hoverinfo="skip",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["BB_LOWER"],
                name="BB Lower",
                line=dict(color="rgba(139,155,180,0.45)", width=1, dash="dot"),
                fill="tonexty",
                fillcolor="rgba(38,166,154,0.06)",
                hoverinfo="skip",
            ),
            row=1,
            col=1,
        )
    if "SMA20" in data.columns:
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
    if "EMA20" in data.columns:
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
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#d1d4dc")),
        xaxis_rangeslider_visible=False,
        height=520,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, font=dict(size=11)),
        **DARK_LAYOUT,
    )
    fig.update_xaxes(showgrid=True, gridcolor="#1b2433", showspikes=True, spikecolor="#5d6b80")
    fig.update_yaxes(showgrid=True, gridcolor="#1b2433", zeroline=False, side="right")
    fig.update_yaxes(title_text="Price", row=1, col=1)
    fig.update_yaxes(title_text="Vol", row=2, col=1)
    return fig


def score_gauge(score: float) -> go.Figure:
    """0–100 AI Score gauge."""
    value = float(score)
    bar = "#26a69a" if value >= 60 else "#f0b429" if value >= 40 else "#ef5350"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": "/100", "font": {"size": 28, "color": "#e8eef7"}},
            title={"text": "AI Score", "font": {"size": 14, "color": "#8b9bb4"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#5d6b80"},
                "bar": {"color": bar},
                "bgcolor": "#121826",
                "borderwidth": 1,
                "bordercolor": "#243044",
                "steps": [
                    {"range": [0, 40], "color": "#2a1518"},
                    {"range": [40, 70], "color": "#2a2414"},
                    {"range": [70, 100], "color": "#10241c"},
                ],
                "threshold": {
                    "line": {"color": "#42a5f5", "width": 3},
                    "thickness": 0.75,
                    "value": value,
                },
            },
        )
    )
    fig.update_layout(height=260, **DARK_LAYOUT)
    return fig


def sanitize_download_name(symbol: str, ext: str) -> str:
    """Safe filename for Streamlit download buttons."""
    cleaned = "".join(ch for ch in symbol.upper() if ch.isalnum() or ch in ".-")
    return f"{cleaned or 'STOCK'}_stockshield.{ext}"
