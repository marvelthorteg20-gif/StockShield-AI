def classify_volatility(atr, price):
    if atr is None or price in (None, 0) or atr != atr:
        return "🟡 Moderate"

    atr_pct = (atr / price) * 100

    if atr_pct < 1.5:
        return "🟢 Low"
    if atr_pct < 3.0:
        return "🟡 Moderate"
    return "🔴 High"


def classify_adx_strength(adx):
    if adx is None or adx != adx:
        return "Weak"
    if adx < 20:
        return "Weak"
    if adx < 40:
        return "Moderate"
    return "Strong"


def calculate_smart_levels(entry, atr, support, resistance):
    """ATR + support stop, with 2R / 3R targets."""
    if entry is None or entry != entry:
        raise ValueError("Invalid entry price")

    atr_value = 0.0 if atr is None or atr != atr else max(float(atr), 0.0)
    support_value = float(support) if support is not None and support == support else entry
    _ = float(resistance) if resistance is not None and resistance == resistance else entry

    atr_stop = entry - (1.5 * atr_value if atr_value > 0 else entry * 0.02)
    support_stop = support_value - (0.25 * atr_value)

    candidates = [level for level in (atr_stop, support_stop, support_value) if level < entry]
    stop_loss = max(candidates) if candidates else atr_stop

    if stop_loss >= entry:
        stop_loss = entry * 0.98

    risk_amount = entry - stop_loss
    if risk_amount <= 0:
        risk_amount = entry * 0.02
        stop_loss = entry - risk_amount

    target1 = entry + (2.0 * risk_amount)
    target2 = entry + (3.0 * risk_amount)

    risk_pct = (risk_amount / entry) * 100
    reward = target1 - entry
    risk_reward = reward / risk_amount if risk_amount else 0.0

    return {
        "entry": entry,
        "stop_loss": stop_loss,
        "risk_pct": risk_pct,
        "target1": target1,
        "target2": target2,
        "risk_reward": risk_reward,
    }
