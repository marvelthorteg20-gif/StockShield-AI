"""Position sizing from account capital and per-trade risk."""

from __future__ import annotations

from typing import Any, Dict, Optional, Union

import config

NumberLike = Union[str, int, float, None]


def parse_capital(raw: NumberLike, default: float = config.DEFAULT_CAPITAL) -> float:
    """Parse a currency string such as '$10,000' into a float."""
    if raw is None:
        return default
    text = str(raw).strip().replace("$", "").replace(",", "")
    if not text:
        return default
    try:
        value = float(text)
    except (TypeError, ValueError):
        return default
    if value <= 0:
        return default
    return value


def calculate_position(
    capital: Any,
    entry: Any,
    stop_loss: Any,
    risk_pct: Optional[float] = None,
) -> Dict[str, Any]:
    """Size a long position so a stop-out loses about risk_pct of capital."""
    if risk_pct is None:
        risk_pct = config.RISK_PERCENT
    capital_value = float(capital)
    entry_value = float(entry)
    stop = float(stop_loss)
    risk_value = float(risk_pct)

    max_loss = capital_value * (risk_value / 100.0)
    per_share = entry_value - stop
    if per_share <= 0:
        per_share = entry_value * config.POSITION_MIN_RISK_FRACTION

    quantity = int(max_loss // per_share)
    notional = quantity * entry_value
    allocation = (notional / capital_value) * 100.0 if capital_value else 0.0

    return {
        "capital": capital_value,
        "risk_pct": risk_value,
        "max_loss": max_loss,
        "quantity": quantity,
        "allocation_pct": allocation,
        "notional": notional,
        "per_share_risk": per_share,
    }
