"""Domain errors for StockShield AI.

Callers can catch ``StockShieldError`` for any recoverable analysis failure.
Messages for empty price history stay identical to the previous CLI.
"""

from __future__ import annotations


class StockShieldError(Exception):
    """Base class for recoverable StockShield failures."""


class InvalidTickerError(StockShieldError):
    """The symbol is empty or not a plausible ticker."""


class EmptyDataError(StockShieldError):
    """Yahoo Finance returned no OHLCV rows."""


class NetworkError(StockShieldError):
    """A market-data request failed because of connectivity."""


class RateLimitError(StockShieldError):
    """An upstream API reported a rate-limit / quota condition."""
