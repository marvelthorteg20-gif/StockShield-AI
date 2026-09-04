from utils.stock_fetcher import fetch_stock

symbol = input("Enter Stock Symbol: ").upper()

data = fetch_stock(symbol)

print("\nStock Information\n")

for key, value in data.items():
    print(f"{key}: {value}")