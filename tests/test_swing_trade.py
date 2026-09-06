from utils.swing_trade import build_swing_plan


def test_swing_plan_has_three_targets():
    plan = build_swing_plan(entry=100, stop_loss=95, target1=110, target2=115, atr=2.0, probability=70)
    assert plan["entry"] == 100
    assert plan["stop_loss"] == 95
    assert plan["target1"] == 110
    assert plan["target2"] == 115
    assert plan["target3"] > plan["target2"]
    assert 3 <= plan["holding_days"] <= 45
    assert plan["probability"] == 70
