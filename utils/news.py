"""News sentiment via Alpha Vantage (return values unchanged)."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple

import requests

import config
from utils.app_log import get_logger
from utils.market_data import add_news_timing

logger = get_logger("news")

NewsResult = Tuple[List[str], str]


def get_news_sentiment(symbol: str) -> NewsResult:
    """Fetch headlines and an overall sentiment label.

    Rate-limit, invalid-symbol, and transport failures keep the same
    fallback strings the CLI already displays.
    """
    url = (
        f"{config.ALPHA_VANTAGE_BASE_URL}"
        f"?function=NEWS_SENTIMENT"
        f"&tickers={symbol}"
        f"&limit={config.NEWS_HEADLINE_LIMIT}"
        f"&apikey={config.NEWS_API_KEY}"
    )

    try:
        started = time.perf_counter()
        response = requests.get(url, timeout=config.NEWS_TIMEOUT_SECONDS)
        add_news_timing(time.perf_counter() - started)
        response.raise_for_status()
        data: Dict[str, Any] = response.json()

        if "Information" in data:
            logger.info("Alpha Vantage rate-limit payload for %s", symbol)
            return ["⚪ API rate limit reached. Please try again later."], "⚪ UNKNOWN"

        if "Error Message" in data:
            logger.info("Alpha Vantage error payload for %s", symbol)
            return ["⚪ Invalid stock symbol."], "⚪ UNKNOWN"

    except Exception as exc:
        logger.warning("News fetch failed for %s: %s", symbol, exc)
        return ["⚪ Unable to fetch news"], "⚪ UNKNOWN"

    news_list: List[str] = []
    total_score = 0.0

    feed = data.get("feed", [])

    if not feed:
        return ["⚪ No News Found"], "⚪ UNKNOWN"

    limit = config.NEWS_HEADLINE_LIMIT
    for article in feed[:limit]:
        title = article.get("title", "No Title")
        score = article.get("overall_sentiment_score", 0)

        total_score += score

        if score >= config.NEWS_SENTIMENT_BULLISH:
            emoji = "🟢"
        elif score <= config.NEWS_SENTIMENT_BEARISH:
            emoji = "🔴"
        else:
            emoji = "🟡"

        news_list.append(f"{emoji} {title}")

    avg = total_score / len(feed[:limit])

    if avg >= config.NEWS_SENTIMENT_BULLISH:
        overall = "🟢 BULLISH"
    elif avg <= config.NEWS_SENTIMENT_BEARISH:
        overall = "🔴 BEARISH"
    else:
        overall = "🟡 NEUTRAL"

    return news_list, overall
