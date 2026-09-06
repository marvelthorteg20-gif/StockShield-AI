def _ohlc(row):
    return float(row["Open"]), float(row["High"]), float(row["Low"]), float(row["Close"])


def _body(open_price, close):
    return abs(close - open_price)


def _range(high, low):
    return high - low


def is_doji(open_price, high, low, close, body_ratio=0.1):
    candle_range = _range(high, low)
    if candle_range <= 0:
        return abs(close - open_price) < 1e-9
    return _body(open_price, close) / candle_range <= body_ratio


def is_hammer(open_price, high, low, close):
    body = _body(open_price, close)
    candle_range = _range(high, low)
    if candle_range <= 0 or body <= 0:
        return False

    upper = high - max(open_price, close)
    lower = min(open_price, close) - low

    return (
        lower >= 2 * body
        and upper <= max(body * 0.5, candle_range * 0.1)
        and body / candle_range <= 0.4
        and max(open_price, close) >= low + 0.6 * candle_range
    )


def is_bullish_engulfing(prev, curr):
    po, _, _, pc = prev
    o, _, _, c = curr
    return pc < po and c > o and o <= pc and c >= po and _body(o, c) > _body(po, pc)


def is_bearish_engulfing(prev, curr):
    po, _, _, pc = prev
    o, _, _, c = curr
    return pc > po and c < o and o >= pc and c <= po and _body(o, c) > _body(po, pc)


def is_morning_star(first, second, third):
    o1, _, _, c1 = first
    o2, h2, l2, c2 = second
    o3, _, _, c3 = third

    body1 = _body(o1, c1)
    body2 = _body(o2, c2)
    body3 = _body(o3, c3)
    range2 = _range(h2, l2)

    if c1 >= o1 or c3 <= o3:
        return False
    if body1 <= 0 or body3 <= 0:
        return False
    if body2 > 0.5 * body1 and (range2 <= 0 or body2 / range2 > 0.4):
        return False

    midpoint = (o1 + c1) / 2
    return c3 > midpoint and max(o2, c2) < min(o1, c1)


def is_evening_star(first, second, third):
    o1, _, _, c1 = first
    o2, h2, l2, c2 = second
    o3, _, _, c3 = third

    body1 = _body(o1, c1)
    body2 = _body(o2, c2)
    body3 = _body(o3, c3)
    range2 = _range(h2, l2)

    if c1 <= o1 or c3 >= o3:
        return False
    if body1 <= 0 or body3 <= 0:
        return False
    if body2 > 0.5 * body1 and (range2 <= 0 or body2 / range2 > 0.4):
        return False

    midpoint = (o1 + c1) / 2
    return c3 < midpoint and min(o2, c2) > max(o1, c1)


def detect_candlestick_patterns(history):
    """Return pattern names completed on the latest candle."""
    if history is None or len(history) < 1:
        return []

    latest = _ohlc(history.iloc[-1])
    patterns = []

    if is_doji(*latest):
        patterns.append("Doji")
    if is_hammer(*latest):
        patterns.append("Hammer")

    if len(history) >= 2:
        prev = _ohlc(history.iloc[-2])
        if is_bullish_engulfing(prev, latest):
            patterns.append("Bullish Engulfing")
        if is_bearish_engulfing(prev, latest):
            patterns.append("Bearish Engulfing")

    if len(history) >= 3:
        first = _ohlc(history.iloc[-3])
        second = _ohlc(history.iloc[-2])
        if is_morning_star(first, second, latest):
            patterns.append("Morning Star")
        if is_evening_star(first, second, latest):
            patterns.append("Evening Star")

    return patterns
