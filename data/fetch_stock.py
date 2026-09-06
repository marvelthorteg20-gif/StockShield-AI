"""Low-level Yahoo history helper (cached)."""

from __future__ import annotations

from typing import Any, Dict, Tuple

import pandas as pd

from utils.market_data import get_ticker_bundle


def get_stock_data(symbol: str) -> Tuple[Dict[str, Any], pd.DataFrame]:
    """Return Yahoo ``info`` and one year of history."""
    bundle = get_ticker_bundle(symbol)
    return bundle["info"], bundle["history"]
