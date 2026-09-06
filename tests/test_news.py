from unittest.mock import MagicMock, patch

from utils.news import get_news_sentiment


def test_news_rate_limit_message_unchanged():
    response = MagicMock()
    response.json.return_value = {"Information": "Thank you for using Alpha Vantage!"}
    response.raise_for_status.return_value = None
    with patch("utils.news.requests.get", return_value=response):
        headlines, sentiment = get_news_sentiment("AAPL")
    assert headlines == ["⚪ API rate limit reached. Please try again later."]
    assert sentiment == "⚪ UNKNOWN"


def test_news_network_failure_message_unchanged():
    with patch("utils.news.requests.get", side_effect=OSError("No internet")):
        headlines, sentiment = get_news_sentiment("AAPL")
    assert headlines == ["⚪ Unable to fetch news"]
    assert sentiment == "⚪ UNKNOWN"
