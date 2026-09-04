import yfinance as yf


def fetch_stock(symbol):
    """
    Fetch stock information using Yahoo Finance.
    """

    stock = yf.Ticker(symbol)

    info = stock.info

    return {
        "Company": info.get("longName"),
        "Current Price": info.get("currentPrice"),
        "Previous Close": info.get("previousClose"),
        "Open": info.get("open"),
        "Day High": info.get("dayHigh"),
        "Day Low": info.get("dayLow"),
        "Market Cap": info.get("marketCap"),
        "Volume": info.get("volume"),
    }