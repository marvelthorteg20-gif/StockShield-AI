import mplfinance as mpf


def plot_stock_chart(history, company_name):
    # Keep only required columns
    data = history[["Open", "High", "Low", "Close", "Volume"]].copy()

    # Moving averages to display
    mav = (20,)

    # EMA20 overlay
    ema20 = mpf.make_addplot(
        history["EMA20"],
        color="green",
        width=1
    )

    mpf.plot(
        data,
        type="candle",
        style="yahoo",
        title=f"{company_name} Stock Price",
        ylabel="Price ($)",
        volume=True,
        mav=mav,
        addplot=ema20,
        figsize=(12, 8),
        tight_layout=True
    )