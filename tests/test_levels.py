from utils.levels import calculate_sr_engine
from tests.history_factory import make_history


def test_sr_engine_returns_ranked_levels():
    history = make_history(80, start=90, drift=0.25)
    levels = calculate_sr_engine(history)
    assert levels
    assert "price" in levels[0]
    assert "strength" in levels[0]
    strengths = [item["strength"] for item in levels]
    assert strengths == sorted(strengths, reverse=True)
    assert any("Fib" in item["name"] or "Fibonacci" in item["family"] for item in levels)
    assert any("Pivot" in item["family"] or "Pivot" in item["name"] for item in levels)
    assert any(item["family"] == "Dynamic" or "Dynamic" in item["name"] for item in levels)
