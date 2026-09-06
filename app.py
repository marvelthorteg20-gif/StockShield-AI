"""StockShield AI command-line trading terminal."""

from __future__ import annotations

import sys

import config
from utils.indicators import calculate_indicators, refine_ai_score
from utils.chart import plot_stock_chart
from utils.news import get_news_sentiment
from utils.fundamentals import get_fundamentals
from utils.decision_engine import generate_decision
from utils.multi_timeframe import analyze_timeframes
from utils.institutional import detect_institutional_signals
from utils.levels import calculate_sr_engine
from utils.star_decision import rate_star_decision
from utils.swing_trade import build_swing_plan
from utils.position_sizing import calculate_position, parse_capital
from utils.ai_summary import generate_ai_summary
from utils.export_report import export_reports
from utils.errors import StockShieldError
from utils.cli import BOLD, CYAN, RED, paint, spinner
from utils.benchmark import Benchmark
from utils.session_log import log_event


def main() -> int:
    """Run the interactive terminal. Returns a process exit code."""
    bench = Benchmark()
    ticker = ""
    try:
        print("=" * 45)
        print(paint("        📈 STOCKSHIELD AI", BOLD + CYAN))
        print("=" * 45)

        ticker = input("Enter Stock Symbol: ").upper()
        capital = parse_capital(input("Enter Capital (default $10,000): "))

        with spinner("Fetching market data"):
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
                today_percent,
                atr,
                volatility_level,
                adx,
                adx_strength,
                patterns,
                smart_levels,
            ) = calculate_indicators(ticker)

            (
                market_cap,
                pe_ratio,
                eps,
                dividend,
                beta,
                revenue,
                profit_margin,
                fundamental_score,
            ) = get_fundamentals(ticker)

            news, sentiment = get_news_sentiment(ticker)

        score, confidence, rating, risk = refine_ai_score(
            trend=trend,
            rsi=history.iloc[-1]["RSI"],
            macd_status=macd_status,
            bb_signal=bb_signal,
            volume_status=volume_status,
            volatility_level=volatility_level,
            adx_strength=adx_strength,
            sentiment=sentiment,
            fundamental_score=fundamental_score,
        )

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
        print(f"📏 ATR({config.ATR_LENGTH})       : {atr:.2f}")
        print(f"🌡️ Volatility    : {volatility_level}")
        print(f"📐 ADX(14)       : {adx:.2f}")
        print(f"💪 Trend Strength: {adx_strength}")
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

        print("\n🛡️ Smart Risk Management")
        print("-" * 45)
        print(f"🎯 Entry Price         : ${smart_levels['entry']:.2f}")
        print(f"🛑 Suggested Stop Loss : ${smart_levels['stop_loss']:.2f}")
        print(f"⚠️ Risk %              : {smart_levels['risk_pct']:.2f}%")
        print(f"🎯 Target 1            : ${smart_levels['target1']:.2f}")
        print(f"🎯 Target 2            : ${smart_levels['target2']:.2f}")
        print(f"📊 Risk/Reward         : {smart_levels['risk_reward']:.2f}")

        print("\n🕯️ Candlestick Patterns")
        print("-" * 45)
        if patterns:
            for pattern in patterns:
                print(f"• {pattern}")
        else:
            print("• No pattern detected")

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

        decision = generate_decision(
            trend=trend,
            rsi=rsi,
            macd_status=macd_status,
            bb_signal=bb_signal,
            atr=atr,
            adx=adx,
            volume_status=volume_status,
            news_sentiment=sentiment,
            fundamental_score=fundamental_score,
            risk_level=risk,
            candlestick_pattern=patterns,
            risk_reward=smart_levels["risk_reward"],
        )

        print()
        print("=" * 34)
        print("🧠 AI DECISION ENGINE")
        print("=" * 34)
        print()
        print(f"Action           : {decision['action']}")
        print(f"Confidence       : {decision['confidence']}%")
        print(f"Probability      : {decision['probability']}%")
        print(f"Holding Period   : {decision['holding_period']}")
        print(f"Risk Reward      : {decision['risk_reward_rating']}")
        print()
        print("Reasons")
        for reason in decision["reasons"]:
            print(f"• {reason}")

        print("\n📰 Latest News")
        print("-" * 45)
        for item in news:
            print(item)

        print()
        print("Overall Sentiment :", sentiment)

        print("\n📝 Explanation:")
        print(explanation)

        timeframes = analyze_timeframes(history)
        print("\n📡 Multi-Timeframe Analysis")
        print("-" * 45)
        print(f"1D  : {timeframes['1D']}")
        print(f"1W  : {timeframes['1W']}")
        print(f"1M  : {timeframes['1M']}")
        print(f"3M  : {timeframes['3M']}")
        print(f"1Y  : {timeframes['1Y']}")
        print()
        print(f"Overall Trend Alignment: {timeframes['alignment']}%")

        inst_signals = detect_institutional_signals(
            history,
            high_52=high_52,
            low_52=low_52,
            support=support,
            resistance=resistance,
        )
        print("\n🏛️ Institutional Signals")
        print("-" * 45)
        signal_labels = (
            ("unusual_volume", "Unusual Volume"),
            ("breakout", "Breakout"),
            ("breakdown", "Breakdown"),
            ("near_52w_high", "Near 52 Week High"),
            ("near_52w_low", "Near 52 Week Low"),
            ("gap_up", "Gap Up"),
            ("gap_down", "Gap Down"),
        )
        for key, label in signal_labels:
            payload = inst_signals[key]
            mark = "✔ Yes" if payload["detected"] else "✖ No"
            print(f"{label:<20}: {mark:<8} (Confidence {payload['confidence']}%)")

        sr_levels = calculate_sr_engine(history)
        print("\n📐 Support & Resistance Engine")
        print("-" * 45)
        if sr_levels:
            for level in sr_levels:
                stars = "★" * level["strength"]
                print(
                    f"{stars:<6} {level['kind']:<11} ${level['price']:.2f}  {level['name']}"
                )
        else:
            print("• Levels unavailable")

        star = rate_star_decision(decision)
        print("\n⭐ Trade Rating")
        print("-" * 45)
        print(star["display"])
        print("Why:")
        for reason in star["why"]:
            print(f"• {reason}")

        swing = build_swing_plan(
            entry=smart_levels["entry"],
            stop_loss=smart_levels["stop_loss"],
            target1=smart_levels["target1"],
            target2=smart_levels["target2"],
            atr=atr,
            probability=decision["probability"],
        )
        print("\n📈 Swing Trading")
        print("-" * 45)
        print(f"Entry Price           : ${swing['entry']:.2f}")
        print(f"Stop Loss             : ${swing['stop_loss']:.2f}")
        print(f"Target 1              : ${swing['target1']:.2f}")
        print(f"Target 2              : ${swing['target2']:.2f}")
        print(f"Target 3              : ${swing['target3']:.2f}")
        print(f"Expected Holding Days : {swing['holding_days']}")
        print(f"Probability of Success: {swing['probability']}%")

        position = calculate_position(
            capital=capital,
            entry=swing["entry"],
            stop_loss=swing["stop_loss"],
            risk_pct=config.RISK_PERCENT,
        )
        print("\n💼 Position Sizing")
        print("-" * 45)
        print(f"Capital               : ${position['capital']:,.2f}")
        print(f"Risk                  : {position['risk_pct']:.0f}%")
        print(f"Maximum Loss          : ${position['max_loss']:,.2f}")
        print(f"Suggested Quantity    : {position['quantity']}")
        print(f"Portfolio Allocation %: {position['allocation_pct']:.2f}%")

        summary = generate_ai_summary(
            company_name=company_name,
            trend=trend,
            rsi=rsi,
            macd_status=macd_status,
            fundamental_score=fundamental_score,
            atr=atr,
            adx=adx,
            risk_level=risk,
            sentiment=sentiment,
            star_label=star["label"],
            alignment=timeframes["alignment"],
            institutional_signals=inst_signals,
            volatility_level=volatility_level,
        )
        print("\n🧾 AI Summary")
        print("-" * 45)
        print(summary)

        report_payload = {
            "symbol": ticker,
            "company": company_name,
            "price": float(latest["Close"]),
            "trend": trend,
            "rsi": float(rsi),
            "macd_status": macd_status,
            "ai_score": score,
            "recommendation": recommendation,
            "decision": decision,
            "star_rating": star["display"],
            "timeframes": timeframes,
            "institutional": inst_signals,
            "support_resistance": sr_levels,
            "swing": swing,
            "position": position,
            "summary": summary,
            "news_sentiment": sentiment,
            "fundamental_score": fundamental_score,
        }
        export_paths = export_reports(
            report_payload, config.EXPORT_FOLDER, symbol=ticker
        )
        print("\n📁 Exported Reports")
        print("-" * 45)
        print(f"JSON : {export_paths['json']}")
        print(f"CSV  : {export_paths['csv']}")
        print(f"PDF  : {export_paths['pdf']}")

        print("-" * 45)
        try:
            plot_stock_chart(history, company_name)
        except Exception as exc:
            log_event(ticker, errors=[f"chart: {exc}"], event="chart_error")
            print("Chart unavailable in this environment.")

        stats = bench.snapshot()
        print()
        print("⚙️ Benchmark")
        print("-" * 45)
        print(f"Runtime            : {stats['runtime_s']:.2f}s")
        print(f"Peak Memory        : {stats['memory_mb']:.2f} MB")
        print(f"API Response Time  : {stats['api_s']:.2f}s")

        log_event(
            ticker,
            analysis_time=stats["runtime_s"],
            exports=export_paths,
            event="analysis",
            extra={"memory_mb": stats["memory_mb"], "api_s": stats["api_s"]},
        )
        return 0

    except StockShieldError as exc:
        print(paint(f"\n❌ {exc}", RED))
        log_event(ticker or "UNKNOWN", errors=[str(exc)], event="error")
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.")
        return 130
    except Exception as exc:
        print(paint("\n❌ Unexpected error. See logs/ for details.", RED))
        log_event(ticker or "UNKNOWN", errors=[repr(exc)], event="error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
