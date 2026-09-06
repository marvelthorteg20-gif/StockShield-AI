from utils.indicators import calculate_indicators
from utils.chart import plot_stock_chart
from utils.news import get_news_sentiment
from utils.fundamentals import get_fundamentals

print("=" * 45)
print("        📈 STOCKSHIELD AI")
print("=" * 45)

symbol = input("Enter Stock Symbol: ").upper()

(
    history,
    trend,
    recommendation,
    explanation,
    company_name,
    sector,
    macd_status,
    score,
    confidence,
    rating,
    bb_signal,
    volume_status,
    risk,
    support,
    resistance,
    high_52,
    low_52,
    today_change,
    today_percent
) = calculate_indicators(symbol)

(
    market_cap,
    pe_ratio,
    eps,
    dividend,
    beta,
    revenue,
    profit_margin,
    fundamental_score,
) = get_fundamentals(symbol)


# Fetch latest news
news, sentiment = get_news_sentiment(symbol)

latest = history.iloc[-1]
rsi = latest["RSI"]

print("\n📊 Stock Analysis")
print("-" * 45)

print(f"🏢 Company       : {company_name}")
print(f"🏭 Sector        : {sector}")
print()
print(f"💰 Current Price : ${latest['Close']:.2f}")
print(f"📉 SMA20         : ${latest['SMA20']:.2f}")
print(f"📈 EMA20         : ${latest['EMA20']:.2f}")
print(f"📊 RSI           : {rsi:.2f}")
print(f"📊 Trend         : {trend}")
print(f"📈 MACD          : {latest['MACD']:.2f}")
print(f"📉 Signal Line   : {latest['MACD_SIGNAL']:.2f}")
print(f"📊 MACD Status   : {macd_status}")
print(f"🧠 AI Score      : {score}/100")
print(f"⭐ Stock Rating : {rating}")
print(f"🎯 Confidence    : {confidence}")
print(f"📊 Bollinger     : {bb_signal}")
print(f"📦 Volume        : {volume_status}")
print(f"⚠️ Risk Level     : {risk}")
print(f"🟢 Support      : ${support:.2f}")
print(f"🔴 Resistance   : ${resistance:.2f}")
print(f"📈 52W High     : ${high_52:.2f}")
print(f"📉 52W Low      : ${low_52:.2f}")
target_price = resistance
upside = ((target_price - latest["Close"]) / latest["Close"]) * 100

print(f"🎯 Target Price : ${target_price:.2f}")
print(f"📈 Upside       : {upside:+.2f}%")
print(f"📅 Today's Move : {today_change:+.2f} ({today_percent:+.2f}%)")
print(f"🤖 Recommendation : {recommendation}")
print("\n📰 Latest News")
print("-" * 45)

print("\n📑 Fundamental Analysis")
print("---------------------------------------------")
print(f"💼 Market Cap       : ${market_cap:,}")
print(f"📊 P/E Ratio        : {pe_ratio}")
print(f"💵 EPS              : {eps}")
print(f"💰 Dividend Yield   : {dividend}")
print(f"📈 Beta             : {beta}")
print(f"🏢 Revenue          : ${revenue:,}")
print(f"📊 Profit Margin    : {profit_margin:.2%}")
print(f"🧠 Fundamental Score: {fundamental_score}/100")
for item in news:
    print(item)

print()
print("Overall Sentiment :", sentiment)

print("\n📝 Explanation:")
print(explanation)

print("-" * 45)
plot_stock_chart(history, company_name)