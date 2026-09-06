from utils.position_sizing import calculate_position, parse_capital


def test_parse_capital():
    assert parse_capital("$10,000") == 10000
    assert parse_capital("") == 10000
    assert parse_capital("bad") == 10000


def test_position_size_two_percent_risk():
    result = calculate_position(capital=10000, entry=100, stop_loss=95, risk_pct=2.0)
    assert result["max_loss"] == 200
    assert result["quantity"] == 40
    assert round(result["allocation_pct"], 2) == 40.0
    assert result["risk_pct"] == 2.0
