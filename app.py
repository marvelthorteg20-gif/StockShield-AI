from data.fetch_stock import get_stock_data
from indicators.sma import calculate_sma
from indicators.ema import calculate_ema
from analysis.trend import analyze_trend

print("=" * 50)
print("        StockShield AI")
print("=" * 50)

ticker = input("Enter Stock Symbol: ").upper()

info, history = get_stock_data(ticker)

if history.empty:
    print("Invalid Stock Symbol")
else:
    history = calculate_sma(history)
    history = calculate_ema(history)

    trend = analyze_trend(history)

    print("\nCompany:", info.get("longName", "N/A"))
    print("Current Price:", info.get("currentPrice", "N/A"))

    print("\nLatest Technical Indicators")
    print("----------------------------")

    print("SMA 20 :", round(history["SMA20"].iloc[-1], 2))
    print("SMA 50 :", round(history["SMA50"].iloc[-1], 2))
    print("SMA 200:", round(history["SMA200"].iloc[-1], 2))
    print("EMA 20 :", round(history["EMA20"].iloc[-1], 2))
    print("EMA 50 :", round(history["EMA50"].iloc[-1], 2))
   
    print()
    print("Trend Analysis")
    print("----------------------------")
    print("Market Trend:", trend)