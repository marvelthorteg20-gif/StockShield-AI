"""Fundamental snapshot scored from Yahoo ``info`` (cached)."""

from __future__ import annotations

from typing import Any, Dict, Tuple

from utils.common import safe_float
from utils.errors import NetworkError, StockShieldError
from utils.market_data import get_ticker_bundle


def _coerce(info: Dict[str, Any], key: str, default: float = 0.0) -> Any:
    value = info.get(key, default)
    if value is None:
        return default
    return value


def get_fundamentals(symbol: str) -> Tuple[Any, ...]:
    """Return market-cap through fundamental score.

    Missing Yahoo fields become 0 so the CLI never crashes on sparse info.
    Scoring rules are unchanged.
    """
    try:
        bundle = get_ticker_bundle(symbol)
        info = bundle.get("info") or {}
    except StockShieldError:
        info = {}
    except Exception as exc:
        raise NetworkError("Unable to fetch fundamentals.") from exc

    market_cap = _coerce(info, "marketCap", 0) or 0
    pe_ratio = _coerce(info, "trailingPE", 0) or 0
    eps = _coerce(info, "trailingEps", 0) or 0
    beta = _coerce(info, "beta", 0) or 0
    dividend = _coerce(info, "dividendYield", 0) or 0
    revenue = _coerce(info, "totalRevenue", 0) or 0
    profit_margin = _coerce(info, "profitMargins", 0) or 0

    pe_ratio = safe_float(pe_ratio, 0.0)
    eps = safe_float(eps, 0.0)
    beta = safe_float(beta, 0.0)
    dividend = safe_float(dividend, 0.0)
    profit_margin = safe_float(profit_margin, 0.0)
    try:
        market_cap = int(safe_float(market_cap, 0.0))
    except (TypeError, ValueError):
        market_cap = 0
    try:
        revenue = int(safe_float(revenue, 0.0))
    except (TypeError, ValueError):
        revenue = 0

    score = 50

    if pe_ratio:
        if pe_ratio < 25:
            score += 10
        else:
            score -= 5

    if eps and eps > 0:
        score += 10

    if revenue and revenue > 0:
        score += 10

    if profit_margin:
        if profit_margin > 0.15:
            score += 10

    if beta:
        if beta < 1.2:
            score += 10
        else:
            score -= 5

    score = max(0, min(score, 100))

    return (
        market_cap,
        pe_ratio,
        eps,
        dividend,
        beta,
        revenue,
        profit_margin,
        score,
    )
