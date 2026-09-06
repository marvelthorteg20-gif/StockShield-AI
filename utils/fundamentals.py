import yfinance as yf


def get_fundamentals(symbol):
    stock = yf.Ticker(symbol)
    info = stock.info

    market_cap = info.get("marketCap", 0)
    pe_ratio = info.get("trailingPE", 0)
    eps = info.get("trailingEps", 0)
    beta = info.get("beta", 0)
    dividend = info.get("dividendYield", 0)
    revenue = info.get("totalRevenue", 0)
    profit_margin = info.get("profitMargins", 0)

    score = 50

    # PE Ratio
    if pe_ratio:
        if pe_ratio < 25:
            score += 10
        else:
            score -= 5

    # EPS
    if eps and eps > 0:
        score += 10

    # Revenue
    if revenue and revenue > 0:
        score += 10

    # Profit Margin
    if profit_margin:
        if profit_margin > 0.15:
            score += 10

    # Beta
    if beta:
        if beta < 1.2:
            score += 10
        else:
            score -= 5

    score = max(0, min(score, 100))

    return (
        market_cap,
        pe_ratio,
        eps,
        dividend,
        beta,
        revenue,
        profit_margin,
        score,
    )