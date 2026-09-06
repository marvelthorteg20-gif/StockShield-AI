from utils.star_decision import rate_star_decision


def test_star_maps_strong_buy():
    rated = rate_star_decision({"action": "Strong Buy", "reasons": ["Trend is strongly bullish."]})
    assert rated["display"] == "★★★★★ STRONG BUY"
    assert rated["why"]


def test_star_maps_hold_and_sell():
    hold = rate_star_decision({"action": "Hold", "reasons": []})
    assert hold["label"] == "HOLD"
    sell = rate_star_decision({"action": "Sell", "reasons": ["MACD is bearish."]})
    assert sell["display"] == "★★ SELL"
    strong = rate_star_decision({"action": "Strong Sell", "reasons": ["Trend is strongly bearish."]})
    assert strong["display"] == "★ STRONG SELL"
