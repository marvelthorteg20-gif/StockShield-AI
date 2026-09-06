from utils.dashboard_ui import clamp_pct, tone_from_signed, tone_from_text
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


def test_ui_tone_helpers():
    assert tone_from_signed(1.2) == "up"
    assert tone_from_signed(-0.4) == "down"
    assert tone_from_text("🟢 BUY") == "up"
    assert tone_from_text("🔴 SELL") == "down"
    assert tone_from_text("HOLD") == "neutral"
    assert clamp_pct(50) == 50
    assert clamp_pct(150) == 100
    assert clamp_pct(-3) == 0
