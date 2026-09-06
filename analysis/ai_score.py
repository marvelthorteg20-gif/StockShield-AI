def _clamp(value, low=0, high=100):
    return max(low, min(high, value))


def _trend_score(trend):
    if trend == "🟢 STRONG BULLISH":
        return 90
    if trend == "🟢 BULLISH":
        return 75
    if trend == "🔴 STRONG BEARISH":
        return 15
    return 50


def _rsi_score(rsi):
    if rsi != rsi:
        return 50
    if 45 <= rsi <= 60:
        return 85
    if 60 < rsi <= 70:
        return 70
    if rsi > 70:
        return 30
    if rsi < 30:
        return 60
    if 30 <= rsi < 45:
        return 55
    return 50


def _macd_score(macd_status):
    if macd_status == "🟢 Bullish Crossover":
        return 80
    if macd_status == "🔴 Bearish Crossover":
        return 25
    return 50


def _bb_score(bb_signal):
    if bb_signal == "🟢 Price Below Lower Band (Oversold)":
        return 70
    if bb_signal == "🔴 Price Above Upper Band (Overbought)":
        return 30
    return 55


def _volume_score(volume_status):
    if volume_status == "🟢 High Volume":
        return 75
    return 45


def _atr_score(volatility_level):
    if volatility_level == "🟢 Low":
        return 80
    if volatility_level == "🔴 High":
        return 30
    return 60


def _adx_score(adx_strength):
    if adx_strength == "Strong":
        return 85
    if adx_strength == "Moderate":
        return 65
    return 40


def _news_score(sentiment):
    if sentiment == "🟢 BULLISH":
        return 80
    if sentiment == "🔴 BEARISH":
        return 20
    return 50


def compute_ai_score(
    trend,
    rsi,
    macd_status,
    bb_signal,
    volume_status,
    volatility_level,
    adx_strength,
    sentiment=None,
    fundamental_score=50,
):
    """Weighted AI score from trend, oscillators, volatility, news, and fundamentals."""
    try:
        fund = float(fundamental_score)
        if fund != fund:
            fund = 50.0
    except (TypeError, ValueError):
        fund = 50.0

    components = {
        "trend": _trend_score(trend),
        "rsi": _rsi_score(rsi),
        "macd": _macd_score(macd_status),
        "bollinger": _bb_score(bb_signal),
        "volume": _volume_score(volume_status),
        "atr": _atr_score(volatility_level),
        "adx": _adx_score(adx_strength),
        "news": _news_score(sentiment),
        "fundamentals": _clamp(fund),
    }

    weights = {
        "trend": 0.18,
        "rsi": 0.12,
        "macd": 0.12,
        "bollinger": 0.08,
        "volume": 0.08,
        "atr": 0.08,
        "adx": 0.10,
        "news": 0.12,
        "fundamentals": 0.12,
    }

    score = sum(components[name] * weights[name] for name in weights)
    return int(round(_clamp(score))), components
