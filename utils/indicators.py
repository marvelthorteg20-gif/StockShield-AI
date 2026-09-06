import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD, ADXIndicator
from ta.volatility import BollingerBands, AverageTrueRange

from analysis.ai_score import compute_ai_score
from analysis.patterns import detect_candlestick_patterns
from analysis.risk import (
    calculate_smart_levels,
    classify_adx_strength,
    classify_volatility,
)


def _rating_from_score(score):
    if score >= 90:
        return "★★★★★"
    if score >= 80:
        return "★★★★☆"
    if score >= 70:
        return "★★★☆☆"
    if score >= 60:
        return "★★☆☆☆"
    return "★☆☆☆☆"


def _confidence_from_score(score):
    if score >= 80:
        return "🟢 HIGH"
    if score >= 60:
        return "🟡 MEDIUM"
    return "🔴 LOW"


def _risk_from_score(score, rsi, volatility_level):
    if rsi > 70 or rsi < 30 or volatility_level == "🔴 High":
        return "🔴 HIGH"
    if score >= 80 and volatility_level == "🟢 Low":
        return "🟢 LOW"
    if _confidence_from_score(score) == "🟢 HIGH":
        return "🟢 LOW"
    return "🟡 MEDIUM"


def refine_ai_score(
    trend,
    rsi,
    macd_status,
    bb_signal,
    volume_status,
    volatility_level,
    adx_strength,
    sentiment,
    fundamental_score,
):
    score, _ = compute_ai_score(
        trend=trend,
        rsi=rsi,
        macd_status=macd_status,
        bb_signal=bb_signal,
        volume_status=volume_status,
        volatility_level=volatility_level,
        adx_strength=adx_strength,
        sentiment=sentiment,
        fundamental_score=fundamental_score,
    )
    confidence = _confidence_from_score(score)
    rating = _rating_from_score(score)
    risk = _risk_from_score(score, rsi, volatility_level)
    return score, confidence, rating, risk


def calculate_indicators(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info

    company_name = info.get("longName", symbol)
    sector = info.get("sector", "Unknown")

    history = stock.history(period="1y")

    if history.empty:
        raise Exception("No stock data found.")

    # =========================
    # Indicators
    # =========================
    history["SMA20"] = history["Close"].rolling(20).mean()
    history["EMA20"] = history["Close"].ewm(span=20, adjust=False).mean()

    history["RSI"] = RSIIndicator(
        close=history["Close"],
        window=14
    ).rsi()

    macd = MACD(history["Close"])
    history["MACD"] = macd.macd()
    history["MACD_SIGNAL"] = macd.macd_signal()

    bb = BollingerBands(
        close=history["Close"],
        window=20,
        window_dev=2
    )

    history["BB_UPPER"] = bb.bollinger_hband()
    history["BB_LOWER"] = bb.bollinger_lband()
    history["BB_MIDDLE"] = bb.bollinger_mavg()

    history["VOL_AVG20"] = history["Volume"].rolling(20).mean()

    atr_indicator = AverageTrueRange(
        high=history["High"],
        low=history["Low"],
        close=history["Close"],
        window=14,
    )
    history["ATR"] = atr_indicator.average_true_range()

    adx_indicator = ADXIndicator(
        high=history["High"],
        low=history["Low"],
        close=history["Close"],
        window=14,
    )
    history["ADX"] = adx_indicator.adx()

    latest = history.iloc[-1]

    rsi = latest["RSI"]
    atr = latest["ATR"]
    adx = latest["ADX"]

    # =========================
    # Trend
    # =========================
    if latest["Close"] > latest["EMA20"] > latest["SMA20"]:
        trend = "🟢 STRONG BULLISH"

    elif latest["Close"] > latest["SMA20"]:
        trend = "🟢 BULLISH"

    elif latest["Close"] < latest["EMA20"] < latest["SMA20"]:
        trend = "🔴 STRONG BEARISH"

    else:
        trend = "🟡 NEUTRAL"

    # =========================
    # MACD Status
    # =========================
    if latest["MACD"] > latest["MACD_SIGNAL"]:
        macd_status = "🟢 Bullish Crossover"

    elif latest["MACD"] < latest["MACD_SIGNAL"]:
        macd_status = "🔴 Bearish Crossover"

    else:
        macd_status = "🟡 Neutral"

    # =========================
    # Bollinger Signal
    # =========================
    if latest["Close"] > latest["BB_UPPER"]:
        bb_signal = "🔴 Price Above Upper Band (Overbought)"

    elif latest["Close"] < latest["BB_LOWER"]:
        bb_signal = "🟢 Price Below Lower Band (Oversold)"

    else:
        bb_signal = "🟡 Price Inside Bands"

    # =========================
    # Volume
    # =========================
    if latest["Volume"] > latest["VOL_AVG20"]:
        volume_status = "🟢 High Volume"
    else:
        volume_status = "🟡 Low Volume"

    # =========================
    # Price Change
    # =========================
    today_change = latest["Close"] - latest["Open"]
    today_percent = (today_change / latest["Open"]) * 100

    support = history["Low"].tail(20).min()
    resistance = history["High"].tail(20).max()

    high_52 = history["High"].max()
    low_52 = history["Low"].min()

    volatility_level = classify_volatility(atr, latest["Close"])
    adx_strength = classify_adx_strength(adx)
    patterns = detect_candlestick_patterns(history)
    smart_levels = calculate_smart_levels(
        entry=float(latest["Close"]),
        atr=float(atr) if atr == atr else 0.0,
        support=float(support),
        resistance=float(resistance),
    )

    # =========================
    # AI Score (technicals; news + fundamentals applied later)
    # =========================
    score, _ = compute_ai_score(
        trend=trend,
        rsi=rsi,
        macd_status=macd_status,
        bb_signal=bb_signal,
        volume_status=volume_status,
        volatility_level=volatility_level,
        adx_strength=adx_strength,
    )

    # =========================
    # Confidence
    # =========================
    confidence = _confidence_from_score(score)

    # =========================
    # Rating
    # =========================
    rating = _rating_from_score(score)

    # =========================
    # Risk
    # =========================
    risk = _risk_from_score(score, rsi, volatility_level)

    # =========================
    # Recommendation
    # =========================
    if trend == "🟢 STRONG BULLISH":
        if rsi > 70:
            recommendation = "🟡 HOLD"
            explanation = (
                "• Trend is bullish.\n"
                "• RSI is above 70.\n"
                "• Stock may be overbought.\n"
                "• Wait before buying."
            )
        else:
            recommendation = "🟢 BUY"
            explanation = (
                "• Trend is strongly bullish.\n"
                "• Price is above EMA20 and SMA20.\n"
                f"• RSI: {rsi:.2f}\n"
                f"• {macd_status}\n"
                f"• {bb_signal}\n"
                f"• {volume_status}\n"
                "• Technical indicators support buying."
            )

    elif trend == "🟢 BULLISH":
        recommendation = "🟢 BUY"
        explanation = (
            "• Trend is bullish.\n"
            f"• RSI: {rsi:.2f}\n"
            f"• {macd_status}\n"
            "• Momentum remains positive."
        )

    elif trend == "🔴 STRONG BEARISH":
        if rsi < 30:
            recommendation = "🟡 HOLD"
            explanation = (
                "• Trend is bearish.\n"
                "• RSI is below 30.\n"
                "• Stock may be oversold."
            )
        else:
            recommendation = "🔴 SELL"
            explanation = (
                "• Trend is bearish.\n"
                "• Price is below EMA20 and SMA20.\n"
                "• Technical indicators remain weak."
            )

    else:
        recommendation = "🟡 HOLD"
        explanation = (
            "• Trend is neutral.\n"
            "• Wait for a stronger signal."
        )

    return (
        history,
        trend,
        recommendation,
        explanation,
        company_name,
        sector,
        macd_status,
        score,
        confidence,
        rating,
        bb_signal,
        volume_status,
        risk,
        support,
        resistance,
        high_52,
        low_52,
        today_change,
        today_percent,
        atr,
        volatility_level,
        adx,
        adx_strength,
        patterns,
        smart_levels,
    )
