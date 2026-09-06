from utils.multi_timeframe import ALIGNMENT_WEIGHTS, analyze_timeframes, classify_timeframe
from tests.history_factory import make_history


def test_alignment_example_weights():
    labels = ["Bullish", "Bullish", "Neutral", "Bullish", "Strong Bullish"]
    alignment = round(100 * sum(ALIGNMENT_WEIGHTS[item] for item in labels) / 5)
    assert alignment == 82


def test_analyze_uptrend_history():
    history = make_history(260, start=80, drift=0.5)
    result = analyze_timeframes(history)
    assert set(result) >= {"1D", "1W", "1M", "3M", "1Y", "alignment"}
    assert result["1Y"] in ("Bullish", "Strong Bullish")
    assert 0 <= result["alignment"] <= 100


def test_classify_timeframe_neutral():
    assert classify_timeframe(0.0, 100, 100, 1.0, 3.0) == "Neutral"
