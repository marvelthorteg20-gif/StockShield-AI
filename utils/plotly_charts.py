"""Plotly figures for the StockShield dashboard (no Streamlit import)."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DARK_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#0b1220",
    plot_bgcolor="#0b1220",
    font=dict(color="#e8eef7", family="Inter, Segoe UI, sans-serif"),
    margin=dict(l=40, r=20, t=50, b=40),
)


def candlestick_figure(history: pd.DataFrame, title: str) -> go.Figure:
    """Dark candlestick with volume, SMA20, and EMA20 when present."""
    data = history.copy()
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=[0.72, 0.28],
    )
    fig.add_trace(
        go.Candlestick(
            x=data.index,
            open=data["Open"],
            high=data["High"],
            low=data["Low"],
            close=data["Close"],
            name="OHLC",
            increasing_line_color="#22c55e",
            decreasing_line_color="#f43f5e",
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
                line=dict(color="#38bdf8", width=1.4),
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
                line=dict(color="#f59e0b", width=1.4),
            ),
            row=1,
            col=1,
        )
    if "Volume" in data.columns:
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data["Volume"],
                name="Volume",
                marker_color="#334155",
            ),
            row=2,
            col=1,
        )
    fig.update_layout(
        title=title,
        xaxis_rangeslider_visible=False,
        height=560,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        **DARK_LAYOUT,
    )
    fig.update_yaxes(gridcolor="#1e293b")
    return fig


def score_gauge(score: float) -> go.Figure:
    """0–100 AI Score gauge."""
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=float(score),
            number={"suffix": "/100", "font": {"size": 28, "color": "#e8eef7"}},
            title={"text": "AI Score", "font": {"size": 16, "color": "#94a3b8"}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "#64748b"},
                "bar": {"color": "#22c55e"},
                "bgcolor": "#151c2c",
                "bordercolor": "#1e293b",
                "steps": [
                    {"range": [0, 40], "color": "#3f1d2b"},
                    {"range": [40, 70], "color": "#3f3a1d"},
                    {"range": [70, 100], "color": "#163528"},
                ],
                "threshold": {
                    "line": {"color": "#38bdf8", "width": 3},
                    "thickness": 0.75,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(height=280, **DARK_LAYOUT)
    return fig


def sanitize_download_name(symbol: str, ext: str) -> str:
    """Safe filename for Streamlit download buttons."""
    cleaned = "".join(ch for ch in symbol.upper() if ch.isalnum() or ch in ".-")
    return f"{cleaned or 'STOCK'}_stockshield.{ext}"
