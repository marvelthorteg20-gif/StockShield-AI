import pandas as pd

from analysis.ai_score import compute_ai_score
from analysis.patterns import (
    detect_candlestick_patterns,
    is_bearish_engulfing,
    is_bullish_engulfing,
    is_doji,
    is_evening_star,
    is_hammer,
    is_morning_star,
)
from analysis.risk import (
    calculate_smart_levels,
    classify_adx_strength,
    classify_volatility,
)


def test_atr_volatility_levels():
    assert classify_volatility(1.0, 100.0) == "🟢 Low"
    assert classify_volatility(2.0, 100.0) == "🟡 Moderate"
    assert classify_volatility(4.0, 100.0) == "🔴 High"


def test_adx_trend_strength():
    assert classify_adx_strength(10) == "Weak"
    assert classify_adx_strength(25) == "Moderate"
    assert classify_adx_strength(45) == "Strong"


def test_smart_stop_uses_atr_and_support():
    levels = calculate_smart_levels(entry=100.0, atr=2.0, support=96.0, resistance=110.0)
    assert levels["entry"] == 100.0
    assert levels["stop_loss"] < 100.0
    assert levels["risk_pct"] > 0
    assert levels["target1"] > levels["entry"]
    assert levels["target2"] > levels["target1"]
    assert levels["risk_reward"] >= 1.0


def test_candlestick_patterns():
    assert is_doji(10, 10.2, 9.8, 10.01)
    assert is_hammer(10.4, 10.5, 9.0, 10.3)

    prev_bull = (10.0, 10.2, 9.5, 9.6)
    curr_bull = (9.5, 11.0, 9.4, 10.8)
    assert is_bullish_engulfing(prev_bull, curr_bull)

    prev_bear = (10.0, 10.5, 9.8, 10.4)
    curr_bear = (10.5, 10.6, 9.4, 9.5)
    assert is_bearish_engulfing(prev_bear, curr_bear)

    morning = (
        (12.0, 12.1, 10.0, 10.2),
        (10.1, 10.3, 9.7, 10.0),
        (10.1, 11.6, 10.0, 11.4),
    )
    assert is_morning_star(*morning)

    evening = (
        (10.0, 12.0, 9.9, 11.8),
        (12.0, 12.3, 11.7, 12.1),
        (11.8, 11.9, 10.2, 10.4),
    )
    assert is_evening_star(*evening)


def test_detect_patterns_on_history():
    rows = [
        {"Open": 12.0, "High": 12.1, "Low": 10.0, "Close": 10.2},
        {"Open": 10.1, "High": 10.3, "Low": 9.7, "Close": 10.0},
        {"Open": 10.1, "High": 11.6, "Low": 10.0, "Close": 11.4},
    ]
    history = pd.DataFrame(rows)
    patterns = detect_candlestick_patterns(history)
    assert "Morning Star" in patterns


def test_ai_score_includes_all_components():
    score, components = compute_ai_score(
        trend="🟢 STRONG BULLISH",
        rsi=52,
        macd_status="🟢 Bullish Crossover",
        bb_signal="🟡 Price Inside Bands",
        volume_status="🟢 High Volume",
        volatility_level="🟢 Low",
        adx_strength="Strong",
        sentiment="🟢 BULLISH",
        fundamental_score=80,
    )
    assert set(components) == {
        "trend",
        "rsi",
        "macd",
        "bollinger",
        "volume",
        "atr",
        "adx",
        "news",
        "fundamentals",
    }
    assert 0 <= score <= 100

    weak_score, _ = compute_ai_score(
        trend="🔴 STRONG BEARISH",
        rsi=80,
        macd_status="🔴 Bearish Crossover",
        bb_signal="🔴 Price Above Upper Band (Overbought)",
        volume_status="🟡 Low Volume",
        volatility_level="🔴 High",
        adx_strength="Weak",
        sentiment="🔴 BEARISH",
        fundamental_score=20,
    )
    assert weak_score < score
