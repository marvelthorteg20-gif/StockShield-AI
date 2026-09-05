import requests

API_KEY = "9S8DLJBP2UN5RIEW"


def get_news_sentiment(symbol):
    url = (
        "https://www.alphavantage.co/query"
        f"?function=NEWS_SENTIMENT"
        f"&tickers={symbol}"
        f"&limit=5"
        f"&apikey={API_KEY}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # API limit reached
        if "Information" in data:
            return ["⚪ API rate limit reached. Please try again later."], "⚪ UNKNOWN"

        # Invalid symbol
        if "Error Message" in data:
            return ["⚪ Invalid stock symbol."], "⚪ UNKNOWN"

    except Exception:
        return ["⚪ Unable to fetch news"], "⚪ UNKNOWN"

    news_list = []
    total_score = 0

    feed = data.get("feed", [])

    if not feed:
        return ["⚪ No News Found"], "⚪ UNKNOWN"

    for article in feed[:5]:
        title = article.get("title", "No Title")
        score = article.get("overall_sentiment_score", 0)

        total_score += score

        if score >= 0.35:
            emoji = "🟢"
        elif score <= -0.35:
            emoji = "🔴"
        else:
            emoji = "🟡"

        news_list.append(f"{emoji} {title}")

    avg = total_score / len(feed[:5])

    if avg >= 0.35:
        overall = "🟢 BULLISH"
    elif avg <= -0.35:
        overall = "🔴 BEARISH"
    else:
        overall = "🟡 NEUTRAL"

    return news_list, overall