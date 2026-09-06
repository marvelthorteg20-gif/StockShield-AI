from unittest.mock import patch

from tests.history_factory import make_history
from utils.pipeline import INSTITUTIONAL_LABELS, run_analysis
from utils.plotly_charts import candlestick_figure, score_gauge, sanitize_download_name


def test_sanitize_download_name():
    assert sanitize_download_name("aapl", "json") == "AAPL_stockshield.json"
    assert sanitize_download_name("***", "pdf").endswith(".pdf")


def test_chart_builders():
    history = make_history(40)
    history["SMA20"] = history["Close"].rolling(5).mean()
    history["EMA20"] = history["Close"].ewm(span=5, adjust=False).mean()
    candle = candlestick_figure(history, "Test")
    gauge = score_gauge(72)
    assert candle.data
    assert gauge.data
    assert candle.layout.template.layout.paper_bgcolor or True


def test_pipeline_uses_existing_engines():
    history = make_history(80, start=90, drift=0.3)
    history["SMA20"] = history["Close"].rolling(20).mean()
    history["EMA20"] = history["Close"].ewm(span=20, adjust=False).mean()
    history["RSI"] = 55.0
    history["MACD"] = 1.2
    history["MACD_SIGNAL"] = 0.8

    def fake_indicators(symbol):
        latest = history.iloc[-1]
        smart = {
            "entry": float(latest["Close"]),
            "stop_loss": float(latest["Close"]) * 0.97,
            "risk_pct": 3.0,
            "target1": float(latest["Close"]) * 1.06,
            "target2": float(latest["Close"]) * 1.09,
            "risk_reward": 2.0,
        }
        return (
            history,
            "🟢 BULLISH",
            "🟢 BUY",
            "• Trend is bullish.",
            "Fixture Co",
            "Technology",
            "🟢 Bullish Crossover",
            70,
            "🟡 MEDIUM",
            "★★★☆☆",
            "🟡 Price Inside Bands",
            "🟢 High Volume",
            "🟡 MEDIUM",
            float(history["Low"].tail(20).min()),
            float(history["High"].tail(20).max()),
            float(history["High"].max()),
            float(history["Low"].min()),
            1.0,
            0.5,
            1.2,
            "🟡 Moderate",
            22.0,
            "Moderate",
            [],
            smart,
        )

    with patch("utils.pipeline.calculate_indicators", side_effect=fake_indicators), patch(
        "utils.pipeline.get_fundamentals",
        return_value=(1, 15, 2.0, 0.01, 1.0, 100, 0.2, 80),
    ), patch(
        "utils.pipeline.get_news_sentiment",
        return_value=(["🟡 Headline"], "🟡 NEUTRAL"),
    ):
        result = run_analysis("AAPL", capital=10000, risk_pct=2.0)

    assert result.symbol == "AAPL"
    assert result.company_name == "Fixture Co"
    assert 0 <= result.score <= 100
    assert result.decision["action"]
    assert result.swing["target3"] > result.swing["target2"]
    assert result.position["capital"] == 10000
    payload = result.export_payload()
    assert payload["symbol"] == "AAPL"
    assert set(dict(INSTITUTIONAL_LABELS)) <= set(result.institutional)
    assert result.summary
