"""Candlestick chart rendering via mplfinance.

Heavy plotting libraries are imported inside ``plot_stock_chart`` so the CLI
can start without loading matplotlib when a chart is not shown.
"""

from __future__ import annotations

import os

import pandas as pd

import config


def _select_matplotlib_backend() -> None:
    """Prefer a headless backend on Unix without DISPLAY (CI / SSH).

    Windows desktop sessions keep the default GUI backend. Operators can
    override with the ``MPLBACKEND`` environment variable on any OS.
    """
    import matplotlib

    forced = os.environ.get("MPLBACKEND")
    if forced:
        matplotlib.use(forced, force=True)
        return
    if os.name != "nt" and not os.environ.get("DISPLAY"):
        matplotlib.use("Agg", force=True)


def plot_stock_chart(history: pd.DataFrame, company_name: str) -> None:
    """Plot OHLCV with SMA20 and EMA20 overlay (unchanged visual)."""
    _select_matplotlib_backend()
    import mplfinance as mpf

    data = history[["Open", "High", "Low", "Close", "Volume"]].copy()
    mav = (config.CHART_MAV,)
    ema20 = mpf.make_addplot(
        history["EMA20"],
        color="green",
        width=1,
    )
    mpf.plot(
        data,
        type="candle",
        style="yahoo",
        title=f"{company_name} Stock Price",
        ylabel="Price ($)",
        volume=True,
        mav=mav,
        addplot=ema20,
        figsize=(12, 8),
        tight_layout=True,
    )
