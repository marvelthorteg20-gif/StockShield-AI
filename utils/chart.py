"""Candlestick chart rendering via mplfinance."""

from __future__ import annotations

import pandas as pd
import mplfinance as mpf


def plot_stock_chart(history: pd.DataFrame, company_name: str) -> None:
    """Plot OHLCV with SMA20 and EMA20 overlay (unchanged visual)."""
    data = history[["Open", "High", "Low", "Close", "Volume"]].copy()
    mav = (20,)
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
