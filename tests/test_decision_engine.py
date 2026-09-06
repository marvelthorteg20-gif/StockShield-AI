from utils.decision_engine import generate_decision


def _strong_buy_inputs():
    return dict(
        trend="🟢 STRONG BULLISH",
        rsi=55,
        macd_status="🟢 Bullish Crossover",
        bb_signal="🟡 Price Inside Bands",
        atr=2.1,
        adx=32,
        volume_status="🟢 High Volume",
        news_sentiment="🟢 BULLISH",
        fundamental_score=88,
        risk_level="🟢 LOW",
        candlestick_pattern=["Morning Star"],
        risk_reward=2.0,
    )


def test_strong_buy_rule():
    decision = generate_decision(**_strong_buy_inputs())
    assert decision["action"] == "Strong Buy"
    assert decision["confidence"] == 92
    assert 0 <= decision["probability"] <= 100
    assert decision["holding_period"] in (
        "Intraday",
        "Swing",
        "Position",
        "Long Term",
    )
    assert decision["risk_reward_rating"] in (
        "Excellent",
        "Good",
        "Average",
        "Poor",
    )
    assert any("strongly bullish" in reason.lower() for reason in decision["reasons"])
    assert any("macd" in reason.lower() for reason in decision["reasons"])
    assert any("fundamental" in reason.lower() for reason in decision["reasons"])


def test_reduce_rule():
    decision = generate_decision(
        trend="🟡 NEUTRAL",
        rsi=74,
        macd_status="🔴 Bearish Crossover",
        bb_signal="🔴 Price Above Upper Band (Overbought)",
        atr=3.4,
        adx=18,
        volume_status="🟡 Low Volume",
        news_sentiment="🔴 BEARISH",
        fundamental_score=48,
        risk_level="🔴 HIGH",
        candlestick_pattern=["Bearish Engulfing"],
        risk_reward=1.2,
    )
    assert decision["action"] == "Reduce"
    assert decision["confidence"] >= 60
    assert any("overbought" in reason.lower() for reason in decision["reasons"])
    assert any("negative" in reason.lower() or "bearish" in reason.lower() for reason in decision["reasons"])


def test_strong_sell_on_aligned_weakness():
    decision = generate_decision(
        trend="🔴 STRONG BEARISH",
        rsi=78,
        macd_status="🔴 Bearish Crossover",
        bb_signal="🔴 Price Above Upper Band (Overbought)",
        atr=5.0,
        adx=42,
        volume_status="🟢 High Volume",
        news_sentiment="🔴 BEARISH",
        fundamental_score=22,
        risk_level="🔴 HIGH",
        candlestick_pattern=["Evening Star"],
        risk_reward=2.0,
    )
    assert decision["action"] in ("Sell", "Strong Sell")
    assert decision["confidence"] >= 50


def test_hold_on_mixed_signals():
    decision = generate_decision(
        trend="🟡 NEUTRAL",
        rsi=50,
        macd_status="🟡 Neutral",
        bb_signal="🟡 Price Inside Bands",
        atr=1.8,
        adx=16,
        volume_status="🟡 Low Volume",
        news_sentiment="🟡 NEUTRAL",
        fundamental_score=50,
        risk_level="🟡 MEDIUM",
        candlestick_pattern=[],
        risk_reward=2.0,
    )
    assert decision["action"] == "Hold"
    assert 20 <= decision["confidence"] <= 70


def test_weak_adx_caps_strong_buy():
    inputs = _strong_buy_inputs()
    inputs["adx"] = 14
    inputs["news_sentiment"] = "🟡 NEUTRAL"
    decision = generate_decision(**inputs)
    assert decision["action"] in ("Buy", "Accumulate", "Hold")
    assert decision["action"] != "Strong Buy"


def test_decision_includes_all_output_fields():
    decision = generate_decision(**_strong_buy_inputs())
    assert set(decision) >= {
        "action",
        "confidence",
        "reasons",
        "holding_period",
        "probability",
        "risk_reward_rating",
    }
    assert isinstance(decision["reasons"], list)
    assert len(decision["reasons"]) >= 8
    assert decision["action"] in (
        "Strong Buy",
        "Buy",
        "Accumulate",
        "Hold",
        "Reduce",
        "Sell",
        "Strong Sell",
    )
