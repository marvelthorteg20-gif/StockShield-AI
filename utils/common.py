"""Shared numeric helpers used across StockShield modules."""

from __future__ import annotations

from typing import Any


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert *value* to float, returning *default* for None/NaN/invalid."""
    try:
        number = float(value)
        if number != number:
            return default
        return number
    except (TypeError, ValueError):
        return default


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    """Clamp *value* into [low, high]."""
    return max(low, min(high, value))


def as_text(value: Any) -> str:
    """Uppercase string form of *value* (empty string for None)."""
    return str(value or "").upper()
