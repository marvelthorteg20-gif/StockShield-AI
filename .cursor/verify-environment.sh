#!/usr/bin/env bash
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"
export MPLBACKEND=Agg

cd /workspace

python3 <<'PY'
from utils.indicators import calculate_indicators
from utils.fundamentals import get_fundamentals
from utils.news import get_news_sentiment

symbol = "AAPL"
(
    history,
    trend,
    recommendation,
    _explanation,
    company_name,
    _sector,
    _macd_status,
    score,
    _confidence,
    _rating,
    _bb_signal,
    _volume_status,
    _risk,
    _support,
    _resistance,
    _high_52,
    _low_52,
    _today_change,
    _today_percent,
) = calculate_indicators(symbol)
(
    market_cap,
    _pe_ratio,
    _eps,
    _dividend,
    _beta,
    _revenue,
    _profit_margin,
    fundamental_score,
) = get_fundamentals(symbol)
news, sentiment = get_news_sentiment(symbol)
latest = history.iloc[-1]

assert company_name, "company name missing"
assert latest["Close"] > 0, "invalid close price"
assert market_cap > 0, "invalid market cap"
assert len(news) > 0, "no news returned"
assert score >= 0, "invalid score"

print("StockShield AI environment verification passed")
print(f"  Company: {company_name}")
print(f"  Price: ${latest['Close']:.2f}")
print(f"  Trend: {trend}")
print(f"  Recommendation: {recommendation}")
print(f"  AI Score: {score}/100")
print(f"  Fundamental Score: {fundamental_score}/100")
print(f"  News items: {len(news)}")
print(f"  Sentiment: {sentiment}")
PY

python3 <<'PY'
import os

import matplotlib

matplotlib.use("Agg")
import mplfinance as mpf

from utils.indicators import calculate_indicators

history, *_ = calculate_indicators("AAPL")
data = history[["Open", "High", "Low", "Close", "Volume"]].copy()
ema20 = mpf.make_addplot(history["EMA20"], color="green", width=1)
chart_path = "/opt/cursor/artifacts/stockshield-verify-chart.png"
os.makedirs(os.path.dirname(chart_path), exist_ok=True)
mpf.plot(
    data,
    type="candle",
    style="yahoo",
    title="AAPL Stock Price",
    volume=True,
    mav=(20,),
    addplot=ema20,
    savefig=chart_path,
)
assert os.path.getsize(chart_path) > 0, "chart file empty"
print(f"Chart saved: {chart_path}")
PY
