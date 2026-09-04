from utils.indicators import calculate_indicators

symbol = input("Enter Stock Symbol: ").upper()

history, trend = calculate_indicators(symbol)

latest = history.iloc[-1]

print("\nStock Analysis")
print("-" * 40)

print(f"Current Price : {latest['Close']:.2f}")
print(f"SMA20         : {latest['SMA20']:.2f}")
print(f"EMA20         : {latest['EMA20']:.2f}")
print(f"Trend         : {trend}")