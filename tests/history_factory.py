"""Helpers for building deterministic OHLCV frames in tests."""

from __future__ import annotations

from typing import Any, List

import pandas as pd


def make_history(
    rows: int,
    start: float = 100.0,
    drift: float = 0.4,
    volume: float = 1_000_000,
    gap: float = 0.0,
    volume_spike: float = 1.0,
) -> pd.DataFrame:
    """Build a simple trending OHLCV frame with *rows* sessions."""
    records: List[dict[str, Any]] = []
    price = start
    for index in range(rows):
        if index == rows - 1 and gap:
            open_px = price * (1 + gap)
        else:
            open_px = price
        close = open_px + drift
        high = max(open_px, close) + 0.4
        low = min(open_px, close) - 0.3
        vol = volume * volume_spike if index == rows - 1 else volume
        records.append(
            {
                "Open": open_px,
                "High": high,
                "Low": low,
                "Close": close,
                "Volume": vol,
            }
        )
        price = close
    return pd.DataFrame(records)
