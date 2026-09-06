"""In-process cache for Yahoo Finance ticker info and history.

``calculate_indicators`` and ``get_fundamentals`` previously each constructed
a ``yf.Ticker`` and hit ``.info``. This module fetches once per symbol/period
and reuses the bundle for ``CACHE_TTL_SECONDS``.
"""

from __future__ import annotations

import re
import time
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import yfinance as yf

import config
from utils.errors import EmptyDataError, InvalidTickerError, NetworkError

TickerBundle = Dict[str, Any]

_CACHE: Dict[Tuple[str, str], Dict[str, Any]] = {}
_TIMINGS: Dict[str, float] = {
    "yahoo_info_s": 0.0,
    "yahoo_history_s": 0.0,
    "news_s": 0.0,
    "cache_hits": 0,
    "cache_misses": 0,
}

_TICKER_RE = re.compile(r"^[A-Z0-9.\-]{1,15}$")


def reset_cache() -> None:
    """Clear cached Yahoo payloads (used by tests)."""
    _CACHE.clear()
    _TIMINGS.update(
        {
            "yahoo_info_s": 0.0,
            "yahoo_history_s": 0.0,
            "news_s": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
    )


def get_timings() -> Dict[str, float]:
    """Return a copy of last-session Yahoo/news timing counters."""
    return dict(_TIMINGS)


def add_news_timing(seconds: float) -> None:
    """Accumulate Alpha Vantage news latency into the API timer."""
    _TIMINGS["news_s"] = _TIMINGS.get("news_s", 0.0) + float(seconds)


def api_response_seconds() -> float:
    """Total network time spent on Yahoo + news this process."""
    return (
        _TIMINGS.get("yahoo_info_s", 0.0)
        + _TIMINGS.get("yahoo_history_s", 0.0)
        + _TIMINGS.get("news_s", 0.0)
    )


def validate_symbol(symbol: str) -> str:
    """Normalize and validate a ticker symbol."""
    cleaned = str(symbol or "").strip().upper()
    if not cleaned or not _TICKER_RE.match(cleaned):
        raise InvalidTickerError(f"Invalid ticker: {symbol!r}")
    return cleaned


def get_ticker_bundle(
    symbol: str,
    period: Optional[str] = None,
    force: bool = False,
) -> TickerBundle:
    """Return ``{info, history, symbol}``, using cache when fresh.

    Raises:
        InvalidTickerError: malformed symbol
        EmptyDataError: no OHLCV (same message as before)
        NetworkError: connectivity / Yahoo transport failure
    """
    ticker = validate_symbol(symbol)
    period = period or config.HISTORY_PERIOD
    key = (ticker, period)
    now = time.time()
    cached = _CACHE.get(key)
    if (
        not force
        and cached
        and now - cached["ts"] < config.CACHE_TTL_SECONDS
    ):
        _TIMINGS["cache_hits"] += 1
        return cached["bundle"]

    _TIMINGS["cache_misses"] += 1
    try:
        stock = yf.Ticker(ticker)
        started = time.perf_counter()
        info = stock.info or {}
        _TIMINGS["yahoo_info_s"] += time.perf_counter() - started
        started = time.perf_counter()
        history = stock.history(period=period)
        _TIMINGS["yahoo_history_s"] += time.perf_counter() - started
    except Exception as exc:
        message = str(exc).lower()
        if any(
            token in message
            for token in ("network", "timeout", "temporarily", "connection", "resolve")
        ):
            raise NetworkError("No internet or Yahoo Finance is unreachable.") from exc
        raise NetworkError("Unable to fetch market data.") from exc

    if history is None or getattr(history, "empty", True):
        raise EmptyDataError("No stock data found.")

    if not isinstance(history, pd.DataFrame):
        raise EmptyDataError("No stock data found.")

    bundle: TickerBundle = {"symbol": ticker, "info": info, "history": history}
    _CACHE[key] = {"ts": now, "bundle": bundle}
    return bundle
