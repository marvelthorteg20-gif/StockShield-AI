"""Yahoo quote snapshot used by the original stock-fetcher helpers."""

from __future__ import annotations

from typing import Any, Dict

from utils.market_data import get_ticker_bundle


def fetch_stock(symbol: str) -> Dict[str, Any]:
    """Fetch stock information using Yahoo Finance (cached bundle)."""
    info = get_ticker_bundle(symbol)["info"] or {}
    return {
        "Company": info.get("longName"),
        "Current Price": info.get("currentPrice"),
        "Previous Close": info.get("previousClose"),
        "Open": info.get("open"),
        "Day High": info.get("dayHigh"),
        "Day Low": info.get("dayLow"),
        "Market Cap": info.get("marketCap"),
        "Volume": info.get("volume"),
    }
