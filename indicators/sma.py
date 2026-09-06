"""Simple moving-average column helpers."""

from __future__ import annotations

import pandas as pd

import config


def calculate_sma(history: pd.DataFrame) -> pd.DataFrame:
    """Add SMA20, SMA50, and SMA200 columns in place and return *history*."""
    history["SMA20"] = history["Close"].rolling(window=config.SMA_WINDOW).mean()
    history["SMA50"] = history["Close"].rolling(window=config.SMA_MEDIUM_WINDOW).mean()
    history["SMA200"] = history["Close"].rolling(window=config.SMA_LONG_WINDOW).mean()
    return history
