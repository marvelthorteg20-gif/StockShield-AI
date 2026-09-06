from utils.ai_summary import generate_ai_summary


def test_ai_summary_mentions_key_context():
    text = generate_ai_summary(
        company_name="Apple",
        trend="🟢 STRONG BULLISH",
        rsi=54,
        macd_status="🟢 Bullish Crossover",
        fundamental_score=85,
        atr=7.6,
        adx=15,
        risk_level="🟡 MEDIUM",
        sentiment="🟡 NEUTRAL",
        star_label="BUY",
        alignment=82,
        institutional_signals={"unusual_volume": {"detected": False}},
        volatility_level="🟡 Moderate",
    )
    assert "Apple" in text
    assert "technically bullish" in text
    assert "RSI remains healthy" in text
    assert "MACD confirms the uptrend" in text
    assert "fundamentals" in text
    assert "resistance" in text
    assert "82%" in text
