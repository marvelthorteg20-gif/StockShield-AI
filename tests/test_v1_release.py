"""v1.0 release checks: helpers, exports, and path portability."""

from __future__ import annotations

from pathlib import Path

import config
from analysis.trend import analyze_trend
from data.fetch_stock import get_stock_data
from indicators.ema import calculate_ema
from indicators.sma import calculate_sma
from tests.history_factory import make_history
from utils.export_report import export_reports
from utils.stock_fetcher import fetch_stock


SAMPLE_PAYLOAD = {
    "symbol": "AAPL",
    "company": "Apple Inc.",
    "price": 319.97,
    "trend": "STRONG BULLISH",
    "rsi": 53.95,
    "macd_status": "Bullish Crossover",
    "ai_score": 69,
    "recommendation": "BUY",
    "decision": {
        "action": "Accumulate",
        "confidence": 80,
        "probability": 72,
        "holding_period": "Swing",
        "risk_reward_rating": "Good",
    },
    "star_rating": "★★★★ BUY",
    "timeframes": {"1D": "Bullish", "alignment": 70},
    "news_sentiment": "NEUTRAL",
    "fundamental_score": 80,
    "disclaimer": "Sample report for StockShield AI v1.0. Not live market data.",
}


def test_version_is_1_0_0():
    assert config.VERSION == "1.0.0"


def test_sma_ema_trend_helpers_still_work():
    history = make_history(60)
    history = calculate_sma(history)
    history = calculate_ema(history)
    assert "SMA20" in history.columns
    assert "EMA20" in history.columns
    label = analyze_trend(history)
    assert isinstance(label, str) and label


def test_export_works_with_pathlib_directories(tmp_path: Path):
    paths = export_reports(SAMPLE_PAYLOAD, directory=str(tmp_path), symbol="AAPL")
    for kind in ("json", "csv", "pdf"):
        dest = Path(paths[kind])
        assert dest.is_file()
        assert dest.suffix == f".{kind}"


def test_fetch_wrappers_use_cached_bundle(monkeypatch):
    history = make_history(10)
    bundle = {
        "info": {"longName": "Apple Inc.", "currentPrice": 100.0, "volume": 1},
        "history": history,
        "symbol": "AAPL",
    }
    monkeypatch.setattr("utils.stock_fetcher.get_ticker_bundle", lambda symbol: bundle)
    monkeypatch.setattr("data.fetch_stock.get_ticker_bundle", lambda symbol: bundle)
    snapshot = fetch_stock("AAPL")
    assert snapshot["Company"] == "Apple Inc."
    info, frame = get_stock_data("AAPL")
    assert info["longName"] == "Apple Inc."
    assert not frame.empty
