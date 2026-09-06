"""Exponential moving-average column helpers."""

from __future__ import annotations

import pandas as pd

import config


def calculate_ema(history: pd.DataFrame) -> pd.DataFrame:
    """Add EMA20 and EMA50 columns in place and return *history*."""
    history["EMA20"] = history["Close"].ewm(span=config.EMA_WINDOW, adjust=False).mean()
    history["EMA50"] = history["Close"].ewm(span=config.EMA_MEDIUM_WINDOW, adjust=False).mean()
    return history
