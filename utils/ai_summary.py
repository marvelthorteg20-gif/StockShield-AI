"""Professional narrative summary built from computed signals (no LLM call)."""

from __future__ import annotations


def _text(value):
    return str(value or "")


def _institutional_tone(signals):
    detected = [name for name, payload in (signals or {}).items() if payload.get("detected")]
    if not detected:
        return "Institutional participation is currently average."
    if "unusual_volume" in detected and ("breakout" in detected or "gap_up" in detected):
        return "Institutional participation looks elevated, with unusual volume confirming the move."
    if "breakdown" in detected or "gap_down" in detected:
        return "Institutional flow currently leans defensive."
    return "Institutional participation is mixed, with a few notable structure signals."


def generate_ai_summary(
    company_name,
    trend,
    rsi,
    macd_status,
    fundamental_score,
    atr,
    adx,
    risk_level,
    sentiment,
    star_label,
    alignment,
    institutional_signals,
    volatility_level=None,
):
    """Return a ChatGPT-style professional market paragraph."""
    name = company_name or "The stock"
    rsi_value = float(rsi) if rsi == rsi else 50.0
    fund = float(fundamental_score) if fundamental_score == fundamental_score else 50.0
    atr_value = float(atr) if atr == atr else 0.0
    adx_value = float(adx) if adx == adx else 0.0

    trend_l = _text(trend).lower()
    if "bullish" in trend_l:
        tape = "technically bullish"
    elif "bearish" in trend_l:
        tape = "technically bearish"
    else:
        tape = "technically mixed"

    if 45 <= rsi_value <= 65:
        rsi_line = "RSI remains healthy"
    elif rsi_value > 70:
        rsi_line = "RSI is stretched into overbought territory"
    elif rsi_value < 30:
        rsi_line = "RSI is oversold and may attract mean-reversion buyers"
    else:
        rsi_line = f"RSI is at {rsi_value:.0f}"

    macd_l = _text(macd_status).lower()
    if "bullish" in macd_l:
        macd_line = "MACD confirms the uptrend"
    elif "bearish" in macd_l:
        macd_line = "MACD is signaling downside momentum"
    else:
        macd_line = "MACD is not yet decisive"

    if fund > 80:
        fund_line = "strong fundamentals"
    elif fund >= 60:
        fund_line = "supportive fundamentals"
    else:
        fund_line = "only mixed fundamentals"

    inst_line = _institutional_tone(institutional_signals)

    vol_l = _text(volatility_level).lower()
    risk_word = _text(risk_level).replace("HIGH", "high").replace("LOW", "low").replace("MEDIUM", "moderate")
    if "HIGH" in _text(risk_level) or "high" in vol_l:
        risk_line = f"Risk remains {risk_word.split()[-1] if risk_word else 'moderate'} because ATR has increased during recent sessions"
    else:
        risk_line = f"Risk remains {risk_word.split()[-1] if risk_word else 'moderate'}"

    if "BUY" in _text(star_label) and "SELL" not in _text(star_label):
        close_line = "Overall probability favors continuation toward resistance."
    elif "SELL" in _text(star_label):
        close_line = "Overall probability favors further pressure toward support."
    else:
        close_line = "Overall probability favors a range-bound wait for confirmation."

    news_l = _text(sentiment).lower()
    if "bullish" in news_l:
        news_bit = " News flow is constructive."
    elif "bearish" in news_l or "negative" in news_l:
        news_bit = " News flow is a headwind."
    else:
        news_bit = ""

    return (
        f"{name} remains {tape} with improving momentum and {fund_line}. "
        f"{rsi_line} while {macd_line}. {inst_line} "
        f"{risk_line}. Multi-timeframe alignment is {int(alignment)}%. "
        f"{close_line}{news_bit}"
    )
