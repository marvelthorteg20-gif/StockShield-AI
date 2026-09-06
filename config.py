"""StockShield AI runtime configuration.

Adjust these constants to tune analysis windows, risk, exports, and CLI theme
without changing application code. Defaults match the current production CLI.
"""

from __future__ import annotations

# --- Technical windows (defaults preserve current indicator output) ---
ATR_LENGTH: int = 14
RSI_PERIOD: int = 14
MACD_FAST: int = 12
MACD_SLOW: int = 26
MACD_SIGNAL: int = 9

# --- Risk and files ---
RISK_PERCENT: float = 2.0
EXPORT_FOLDER: str = "reports"
LOG_FOLDER: str = "logs"

# --- CLI ---
# "color" enables ANSI colors when stdout is a TTY; "classic" is plain text.
THEME: str = "color"

# --- Data ---
HISTORY_PERIOD: str = "1y"
CACHE_TTL_SECONDS: int = 300
YAHOO_TIMEOUT_SECONDS: int = 20
NEWS_TIMEOUT_SECONDS: int = 10
NEWS_API_KEY: str = "9S8DLJBP2UN5RIEW"
