import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands


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

    latest = history.iloc[-1]

    rsi = latest["RSI"]

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

    # =========================
    # AI Score
    # =========================
    score = 40

    if trend == "🟢 STRONG BULLISH":
        score += 20
    elif trend == "🟢 BULLISH":
        score += 10
    elif trend == "🔴 STRONG BEARISH":
        score -= 20

    if 45 <= rsi <= 60:
        score += 15
    elif 60 < rsi <= 70:
        score += 8
    elif rsi > 70:
        score -= 10
    elif rsi < 30:
        score += 5

    if macd_status == "🟢 Bullish Crossover":
        score += 15
    else:
        score -= 10

    if latest["Close"] > latest["EMA20"]:
        score += 10

    if latest["Close"] > latest["SMA20"]:
        score += 5

    if bb_signal == "🟢 Price Below Lower Band (Oversold)":
        score += 5
    elif bb_signal == "🔴 Price Above Upper Band (Overbought)":
        score -= 5

    if volume_status == "🟢 High Volume":
        score += 10

    if today_percent > 2:
        score += 5
    elif today_percent < -2:
        score -= 10

    score = max(0, min(score, 100))

    # =========================
    # Confidence
    # =========================
    if score >= 80:
        confidence = "🟢 HIGH"
    elif score >= 60:
        confidence = "🟡 MEDIUM"
    else:
        confidence = "🔴 LOW"

    # =========================
    # Rating
    # =========================
    if score >= 90:
        rating = "★★★★★"
    elif score >= 80:
        rating = "★★★★☆"
    elif score >= 70:
        rating = "★★★☆☆"
    elif score >= 60:
        rating = "★★☆☆☆"
    else:
        rating = "★☆☆☆☆"

    # =========================
    # Risk
    # =========================
    if rsi > 70 or rsi < 30:
        risk = "🔴 HIGH"
    elif confidence == "🟢 HIGH":
        risk = "🟢 LOW"
    else:
        risk = "🟡 MEDIUM"

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
    )