"""StockShield AI runtime configuration.

Adjust these constants to tune analysis windows, risk, exports, and CLI theme
without changing application code. Defaults match the current production CLI.
"""

from __future__ import annotations

from typing import Final

# --- Technical windows (defaults preserve current indicator output) ---
ATR_LENGTH: Final[int] = 14
RSI_PERIOD: Final[int] = 14
MACD_FAST: Final[int] = 12
MACD_SLOW: Final[int] = 26
MACD_SIGNAL: Final[int] = 9
SMA_WINDOW: Final[int] = 20
EMA_WINDOW: Final[int] = 20
SMA_MEDIUM_WINDOW: Final[int] = 50
SMA_LONG_WINDOW: Final[int] = 200
EMA_MEDIUM_WINDOW: Final[int] = 50
BB_WINDOW: Final[int] = 20
BB_STD: Final[int] = 2
ADX_WINDOW: Final[int] = 14
VOLUME_AVG_WINDOW: Final[int] = 20
SWING_LOOKBACK: Final[int] = 20
SR_LOOKBACK: Final[int] = 60
CHART_MAV: Final[int] = 20

RSI_OVERBOUGHT: Final[int] = 70
RSI_OVERSOLD: Final[int] = 30

# --- Risk and files ---
RISK_PERCENT: Final[float] = 2.0
EXPORT_FOLDER: Final[str] = "reports"
LOG_FOLDER: Final[str] = "logs"
LOG_FILE_NAME: Final[str] = "stockshield.log"
JSONL_LOG_NAME: Final[str] = "stockshield.jsonl"

# --- CLI ---
# "color" enables ANSI colors when stdout is a TTY; "classic" is plain text.
THEME: Final[str] = "color"
CLI_RULE_WIDTH: Final[int] = 45

# --- Data ---
HISTORY_PERIOD: Final[str] = "1y"
CACHE_TTL_SECONDS: Final[int] = 300
YAHOO_TIMEOUT_SECONDS: Final[int] = 20
NEWS_TIMEOUT_SECONDS: Final[int] = 10
NEWS_API_KEY: Final[str] = "9S8DLJBP2UN5RIEW"
NEWS_HEADLINE_LIMIT: Final[int] = 5
NEWS_SENTIMENT_BULLISH: Final[float] = 0.35
NEWS_SENTIMENT_BEARISH: Final[float] = -0.35
ALPHA_VANTAGE_BASE_URL: Final[str] = "https://www.alphavantage.co/query"

# --- Scoring bounds (same numeric behavior as existing engines) ---
SCORE_MIN: Final[int] = 0
SCORE_MAX: Final[int] = 100
DEFAULT_CAPITAL: Final[float] = 10_000.0
POSITION_MIN_RISK_FRACTION: Final[float] = 0.01

# --- Dashboard sidebar defaults (presentation only) ---
STREAMLIT_CAPITAL_MIN: Final[float] = 100.0
STREAMLIT_CAPITAL_STEP: Final[float] = 100.0
STREAMLIT_RISK_MIN: Final[float] = 0.1
STREAMLIT_RISK_MAX: Final[float] = 10.0
STREAMLIT_RISK_STEP: Final[float] = 0.1
