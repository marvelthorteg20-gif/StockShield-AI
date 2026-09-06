from utils.errors import InvalidTickerError, StockShieldError
from dashboard import validate_dashboard_inputs


def test_validate_dashboard_inputs_ok():
    ticker, capital, risk = validate_dashboard_inputs("aapl", 10000, 2)
    assert ticker == "AAPL"
    assert capital == 10000.0
    assert risk == 2.0


def test_validate_dashboard_rejects_bad_ticker():
    try:
        validate_dashboard_inputs("$$$", 10000, 2)
        raise AssertionError("expected InvalidTickerError")
    except InvalidTickerError:
        pass


def test_validate_dashboard_rejects_bad_capital():
    try:
        validate_dashboard_inputs("AAPL", 0, 2)
        raise AssertionError("expected StockShieldError")
    except StockShieldError:
        pass


def test_validate_dashboard_rejects_bad_risk():
    try:
        validate_dashboard_inputs("AAPL", 10000, 0)
        raise AssertionError("expected StockShieldError")
    except StockShieldError:
        pass
