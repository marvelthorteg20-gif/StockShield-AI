import yfinance as yf

def get_stock_data(symbol):
    stock = yf.Ticker(symbol)

    info = stock.info

    # Get one year of historical data
    history = stock.history(period="1y")

    return info, history