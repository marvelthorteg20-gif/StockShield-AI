"""Ticker-symbol validation with no market-data dependencies.

This module is intentionally independent of yfinance so Streamlit can validate
sidebar input on first paint without downloading Yahoo payloads.
"""

from __future__ import annotations

import re

from utils.errors import InvalidTickerError

_TICKER_RE = re.compile(r"^[A-Z0-9.\-]{1,15}$")


def validate_symbol(symbol: str) -> str:
    """Normalize and validate a ticker symbol.

    Returns:
        Uppercased ticker suitable for Yahoo Finance.

    Raises:
        InvalidTickerError: empty or implausible symbol.
    """
    cleaned = str(symbol or "").strip().upper()
    if not cleaned or not _TICKER_RE.match(cleaned):
        raise InvalidTickerError(f"Invalid ticker: {symbol!r}")
    return cleaned
