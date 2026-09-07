"""Optional Yahoo snapshots for the v2 sidebar (not used by analysis)."""

from __future__ import annotations

from typing import Any

INDEX_SYMBOLS: tuple[tuple[str, str], ...] = (
    ("S&P 500", "^GSPC"),
    ("NASDAQ", "^IXIC"),
    ("Dow Jones", "^DJI"),
    ("NIFTY 50", "^NSEI"),
    ("SENSEX", "^BSESN"),
)

OVERVIEW_SYMBOLS: tuple[tuple[str, str], ...] = (
    ("Gold", "GC=F"),
    ("Bitcoin", "BTC-USD"),
    ("USD Index", "DX-Y.NYB"),
    ("Oil", "CL=F"),
)


def _last_close(history: Any) -> float | None:
    if history is None or getattr(history, "empty", True):
        return None
    if "Close" not in history.columns:
        return None
    value = history["Close"].dropna()
    if value.empty:
        return None
    return float(value.iloc[-1])


def fetch_market_snapshots() -> dict[str, dict[str, Any]]:
    """Return last closes for sidebar instruments. Never raises to callers."""
    rows: dict[str, dict[str, Any]] = {}
    try:
        import yfinance as yf
    except Exception:
        return rows
    for label, yahoo in INDEX_SYMBOLS + OVERVIEW_SYMBOLS:
        try:
            history = yf.Ticker(yahoo).history(period="5d", interval="1d")
            last = _last_close(history)
        except Exception:
            last = None
        if last is None:
            continue
        rows[label] = {"value": last, "display": f"{last:,.2f}", "symbol": yahoo}
    return rows
