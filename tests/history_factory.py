import pandas as pd


def make_history(rows, start=100.0, drift=0.4, volume=1_000_000, gap=0.0, volume_spike=1.0):
    records = []
    price = start
    for index in range(rows):
        if index == rows - 1 and gap:
            open_px = price * (1 + gap)
        else:
            open_px = price
        close = open_px + drift
        high = max(open_px, close) + 0.4
        low = min(open_px, close) - 0.3
        vol = volume * volume_spike if index == rows - 1 else volume
        records.append(
            {
                "Open": open_px,
                "High": high,
                "Low": low,
                "Close": close,
                "Volume": vol,
            }
        )
        price = close
    return pd.DataFrame(records)
