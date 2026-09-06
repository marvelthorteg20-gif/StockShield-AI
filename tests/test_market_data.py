from unittest.mock import MagicMock, patch

import pandas as pd

import config
from tests.history_factory import make_history
from utils.errors import EmptyDataError, InvalidTickerError, NetworkError
from utils.fundamentals import get_fundamentals
from utils.market_data import get_ticker_bundle, reset_cache, validate_symbol


def test_validate_symbol():
    assert validate_symbol("aapl") == "AAPL"
    try:
        validate_symbol("$$$")
        raise AssertionError("expected InvalidTickerError")
    except InvalidTickerError:
        pass


def test_yahoo_cache_avoids_duplicate_calls():
    reset_cache()
    history = make_history(40)
    mock_ticker = MagicMock()
    mock_ticker.info = {"longName": "Apple Inc.", "sector": "Technology"}
    mock_ticker.history.return_value = history
    with patch("utils.market_data.yf.Ticker", return_value=mock_ticker) as ctor:
        first = get_ticker_bundle("AAPL")
        second = get_ticker_bundle("AAPL")
        assert ctor.call_count == 1
        assert mock_ticker.history.call_count == 1
        assert first["info"]["longName"] == "Apple Inc."
        assert second is first


def test_empty_history_raises():
    reset_cache()
    mock_ticker = MagicMock()
    mock_ticker.info = {}
    mock_ticker.history.return_value = pd.DataFrame()
    with patch("utils.market_data.yf.Ticker", return_value=mock_ticker):
        try:
            get_ticker_bundle("ZZZZ")
            raise AssertionError("expected EmptyDataError")
        except EmptyDataError as exc:
            assert str(exc) == "No stock data found."


def test_network_error_wrapping():
    reset_cache()
    with patch("utils.market_data.yf.Ticker", side_effect=OSError("connection timeout")):
        try:
            get_ticker_bundle("AAPL")
            raise AssertionError("expected NetworkError")
        except NetworkError:
            pass


def test_missing_fundamentals_do_not_crash():
    history = make_history(20)
    with patch(
        "utils.fundamentals.get_ticker_bundle",
        return_value={"info": {}, "history": history, "symbol": "AAPL"},
    ):
        payload = get_fundamentals("AAPL")
        assert payload[0] == 0
        assert payload[-1] == 50


def test_config_defaults_match_live_cli():
    assert config.ATR_LENGTH == 14
    assert config.RSI_PERIOD == 14
    assert config.MACD_FAST == 12
    assert config.MACD_SLOW == 26
    assert config.MACD_SIGNAL == 9
    assert config.RISK_PERCENT == 2.0
    assert config.EXPORT_FOLDER == "reports"
    assert config.THEME in ("color", "classic")
