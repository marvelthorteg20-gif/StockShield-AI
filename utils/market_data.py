"""In-process cache for Yahoo Finance ticker info and history.

``calculate_indicators`` and ``get_fundamentals`` previously each constructed
a ``yf.Ticker`` and hit ``.info``. This module fetches once per symbol/period
and reuses the bundle for ``CACHE_TTL_SECONDS``.
"""

from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple

import pandas as pd
import yfinance as yf

import config
from utils.app_log import get_logger
from utils.errors import EmptyDataError, NetworkError
from utils.symbols import validate_symbol

logger = get_logger("market_data")

TickerBundle = Dict[str, Any]

_CACHE: Dict[Tuple[str, str], Dict[str, Any]] = {}
_TIMINGS: Dict[str, float] = {
    "yahoo_info_s": 0.0,
    "yahoo_history_s": 0.0,
    "news_s": 0.0,
    "cache_hits": 0,
    "cache_misses": 0,
}

_NETWORK_TOKENS = ("network", "timeout", "temporarily", "connection", "resolve")


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


def _as_network_error(exc: Exception) -> NetworkError:
    """Map a transport failure to the public NetworkError message."""
    message = str(exc).lower()
    if any(token in message for token in _NETWORK_TOKENS):
        return NetworkError("No internet or Yahoo Finance is unreachable.")
    return NetworkError("Unable to fetch market data.")


def _read_info(stock: Any, ticker: str) -> Dict[str, Any]:
    """Load Yahoo ``info``; empty dict on failure so history can still proceed."""
    started = time.perf_counter()
    try:
        info = stock.info or {}
        if not isinstance(info, dict):
            logger.warning("Yahoo info for %s was not a dict; using empty metadata.", ticker)
            info = {}
        return info
    except Exception as exc:
        logger.warning("Yahoo ticker.info failed for %s: %s", ticker, exc)
        return {}
    finally:
        _TIMINGS["yahoo_info_s"] += time.perf_counter() - started


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
        logger.debug("Yahoo cache hit for %s (%s)", ticker, period)
        return cached["bundle"]

    _TIMINGS["cache_misses"] += 1
    try:
        stock = yf.Ticker(ticker)
    except Exception as exc:
        raise _as_network_error(exc) from exc

    info = _read_info(stock, ticker)

    started = time.perf_counter()
    try:
        history = stock.history(period=period)
    except Exception as exc:
        raise _as_network_error(exc) from exc
    finally:
        _TIMINGS["yahoo_history_s"] += time.perf_counter() - started

    if history is None or getattr(history, "empty", True):
        raise EmptyDataError("No stock data found.")

    if not isinstance(history, pd.DataFrame):
        raise EmptyDataError("No stock data found.")

    bundle: TickerBundle = {"symbol": ticker, "info": info, "history": history}
    _CACHE[key] = {"ts": now, "bundle": bundle}
    return bundle
