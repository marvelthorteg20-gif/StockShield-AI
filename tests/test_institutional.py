from utils.institutional import detect_institutional_signals
from tests.history_factory import make_history


def test_detects_unusual_volume_and_gap_up():
    history = make_history(30, start=100, drift=0.1, volume=1_000_000, gap=0.03, volume_spike=3.0)
    signals = detect_institutional_signals(history)
    assert signals["unusual_volume"]["detected"] is True
    assert signals["gap_up"]["detected"] is True
    assert 0 <= signals["unusual_volume"]["confidence"] <= 99


def test_detects_near_52w_high():
    history = make_history(30, start=100, drift=0.2)
    close = float(history["Close"].iloc[-1])
    signals = detect_institutional_signals(history, high_52=close * 1.01, low_52=close * 0.5)
    assert signals["near_52w_high"]["detected"] is True
    assert signals["near_52w_low"]["detected"] is False


def test_detects_gap_down_and_breakdown():
    history = make_history(25, start=120, drift=-0.6, volume=800_000, gap=-0.04)
    close = float(history["Close"].iloc[-1])
    signals = detect_institutional_signals(
        history,
        high_52=close * 1.4,
        low_52=close * 0.99,
        support=close + 1,
        resistance=close + 10,
    )
    assert signals["gap_down"]["detected"] is True
    assert signals["near_52w_low"]["detected"] is True


def test_all_institutional_keys_present():
    history = make_history(15, start=50, drift=0.05)
    signals = detect_institutional_signals(history)
    assert set(signals) == {
        "unusual_volume",
        "breakout",
        "breakdown",
        "near_52w_high",
        "near_52w_low",
        "gap_up",
        "gap_down",
    }
