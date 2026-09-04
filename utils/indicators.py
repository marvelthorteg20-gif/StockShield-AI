import yfinance as yf


def calculate_indicators(symbol):
    """
    Download historical data and calculate indicators.
    """

    stock = yf.Ticker(symbol)

    history = stock.history(period="3mo")

    # Calculate SMA20
    history["SMA20"] = history["Close"].rolling(window=20).mean()

    # Calculate EMA20
    history["EMA20"] = history["Close"].ewm(span=20, adjust=False).mean()

    # Determine Trend
    latest = history.iloc[-1]

    if latest["Close"] > latest["EMA20"] > latest["SMA20"]:
        trend = "🟢 STRONG BULLISH"

    elif latest["Close"] > latest["SMA20"]:
        trend = "🟢 BULLISH"

    elif latest["Close"] < latest["EMA20"] < latest["SMA20"]:
        trend = "🔴 STRONG BEARISH"

    else:
        trend = "🟡 NEUTRAL"

    return history, trend