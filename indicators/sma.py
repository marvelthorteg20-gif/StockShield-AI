def calculate_sma(history):
    history["SMA20"] = history["Close"].rolling(window=20).mean()
    history["SMA50"] = history["Close"].rolling(window=50).mean()
    history["SMA200"] = history["Close"].rolling(window=200).mean()

    return history
