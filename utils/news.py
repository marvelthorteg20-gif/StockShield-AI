"""News sentiment via Alpha Vantage (return values unchanged)."""

from __future__ import annotations

import time
from typing import List, Tuple

import requests

import config
from utils.market_data import add_news_timing


def get_news_sentiment(symbol: str) -> Tuple[List[str], str]:
    """Fetch headlines and an overall sentiment label.

    Rate-limit, invalid-symbol, and transport failures keep the same
    fallback strings the CLI already displays.
    """
    url = (
        "https://www.alphavantage.co/query"
        f"?function=NEWS_SENTIMENT"
        f"&tickers={symbol}"
        f"&limit=5"
        f"&apikey={config.NEWS_API_KEY}"
    )

    try:
        started = time.perf_counter()
        response = requests.get(url, timeout=config.NEWS_TIMEOUT_SECONDS)
        add_news_timing(time.perf_counter() - started)
        response.raise_for_status()
        data = response.json()

        if "Information" in data:
            return ["⚪ API rate limit reached. Please try again later."], "⚪ UNKNOWN"

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
