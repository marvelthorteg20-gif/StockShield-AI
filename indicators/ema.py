def calculate_ema(history):

    history["EMA20"] = history["Close"].ewm(span=20, adjust=False).mean()

    history["EMA50"] = history["Close"].ewm(span=50, adjust=False).mean()

    return history
