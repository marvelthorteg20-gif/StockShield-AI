"""Position sizing from account capital and per-trade risk."""

from __future__ import annotations


def parse_capital(raw, default=10000.0):
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


def calculate_position(capital, entry, stop_loss, risk_pct=2.0):
    """Size a long position so a stop-out loses about risk_pct of capital."""
    capital = float(capital)
    entry = float(entry)
    stop = float(stop_loss)
    risk_pct = float(risk_pct)

    max_loss = capital * (risk_pct / 100.0)
    per_share = entry - stop
    if per_share <= 0:
        per_share = entry * 0.01

    quantity = int(max_loss // per_share)
    notional = quantity * entry
    allocation = (notional / capital) * 100.0 if capital else 0.0

    return {
        "capital": capital,
        "risk_pct": risk_pct,
        "max_loss": max_loss,
        "quantity": quantity,
        "allocation_pct": allocation,
        "notional": notional,
        "per_share_risk": per_share,
    }
