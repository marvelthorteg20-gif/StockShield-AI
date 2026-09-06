"""StockShield AI Streamlit dashboard.

Presentation only: all scores, signals, and risk numbers come from
``utils.pipeline.run_analysis`` (the same stack ``app.py`` uses).
"""

from __future__ import annotations

from typing import Any, Tuple

import streamlit as st

import config
from utils.app_log import get_logger
from utils.dashboard_ui import (
    THEME_CSS,
    clamp_pct,
    metric_card,
    tape,
    tone_from_signed,
    tone_from_text,
)
from utils.errors import EmptyDataError, InvalidTickerError, NetworkError, StockShieldError
from utils.session_log import log_event
from utils.symbols import validate_symbol

logger = get_logger("dashboard")


def validate_dashboard_inputs(
    symbol: Any,
    capital: Any,
    risk_pct: Any,
) -> Tuple[str, float, float]:
    """Normalize sidebar inputs or raise ``StockShieldError``."""
    ticker = validate_symbol(str(symbol or "").strip())
    try:
        capital_value = float(capital)
        risk_value = float(risk_pct)
    except (TypeError, ValueError) as exc:
        raise StockShieldError("Capital and risk must be numeric.") from exc
    if capital_value <= 0:
        raise StockShieldError("Capital must be greater than 0.")
    if risk_value <= 0 or risk_value > 100:
        raise StockShieldError("Risk % must be between 0 and 100.")
    return ticker, capital_value, risk_value


def _inject_theme() -> None:
    """Inject dashboard CSS once per page."""
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def _cards(*html_cards: str) -> None:
    """Render a row of metric cards."""
    st.markdown(tape(*html_cards), unsafe_allow_html=True)


def _render_company(result: Any) -> None:
    """Company tape: name, last, today, trend, recommendation."""
    latest = result.latest
    change_tone = tone_from_signed(result.today_percent)
    rec_tone = tone_from_text(result.recommendation)
    trend_tone = tone_from_text(result.trend)
    _cards(
        metric_card("🏢", "Company", result.company_name, result.sector, "neutral"),
        metric_card("💲", "Last", f"${float(latest['Close']):.2f}", None, change_tone),
        metric_card(
            "📈" if result.today_percent >= 0 else "📉",
            "Today",
            f"{result.today_percent:+.2f}%",
            f"{result.today_change:+.2f}",
            change_tone,
        ),
        metric_card("🧭", "Trend", result.trend, None, trend_tone),
        metric_card("🤖", "Rec", result.recommendation, None, rec_tone),
    )


def _render_chart_and_score(result: Any) -> None:
    """Draw the candlestick (lazy Plotly import) and AI score gauge."""
    from utils.plotly_charts import candlestick_figure, score_gauge
    chart_col, score_col = st.columns((2.15, 1), gap="medium")
    with chart_col:
        with st.expander("📊  Candlestick Chart", expanded=True):
            history = result.history
            required = {"Open", "High", "Low", "Close"}
            if history is None or getattr(history, "empty", True) or not required.issubset(history.columns):
                st.error("Candlestick data is incomplete.")
            else:
                st.plotly_chart(
                    candlestick_figure(history, f"{result.symbol}  ·  {result.company_name}"),
                    use_container_width=True,
                    config={"displaylogo": False, "scrollZoom": True},
                )
    with score_col:
        with st.expander("🧠  AI Score", expanded=True):
            st.plotly_chart(score_gauge(result.score), use_container_width=True)
            st.progress(clamp_pct(result.score), text=f"AI Score  {result.score}/100")
            st.caption(f"⭐ {result.rating}   ·   {result.confidence}")


def _render_decision(result: Any) -> None:
    """Decision-engine expander."""
    with st.expander("⚖️  Decision Engine", expanded=True):
        action = result.decision["action"]
        tone = tone_from_text(action)
        _cards(
            metric_card("⚡", "Action", action, result.star.get("display"), tone),
            metric_card("🎯", "Confidence", f"{result.decision['confidence']}%", None, "neutral"),
            metric_card("📊", "Probability", f"{result.decision['probability']}%", None, "neutral"),
            metric_card("⏳", "Horizon", result.decision["holding_period"], None, "neutral"),
            metric_card("📐", "R/R", str(result.decision["risk_reward_rating"]), None, "neutral"),
        )
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.progress(
                clamp_pct(result.decision["confidence"]),
                text=f"Confidence  {result.decision['confidence']}%",
            )
        with c2:
            st.progress(
                clamp_pct(result.decision["probability"]),
                text=f"Probability  {result.decision['probability']}%",
            )
        st.markdown("**Reasons**")
        for reason in result.decision.get("reasons") or []:
            st.markdown(f"- {reason}")


def _render_technicals(result: Any) -> None:
    """Technical indicator expander."""
    latest = result.latest
    with st.expander("📡  Technical Indicators", expanded=False):
        macd_tone = "up" if float(latest["MACD"]) >= float(latest["MACD_SIGNAL"]) else "down"
        _cards(
            metric_card("📉", "SMA20", f"${float(latest['SMA20']):.2f}"),
            metric_card("📈", "EMA20", f"${float(latest['EMA20']):.2f}"),
            metric_card("🌡️", "RSI", f"{result.rsi:.2f}"),
            metric_card("📶", "MACD", f"{float(latest['MACD']):.2f}", None, macd_tone),
            metric_card("📦", "Volume", result.volume_status, None, tone_from_text(result.volume_status)),
        )
        st.progress(clamp_pct(result.rsi), text=f"RSI  {result.rsi:.1f}")
        st.progress(clamp_pct(result.adx), text=f"ADX  {result.adx:.1f}")
        st.dataframe(
            {
                "Metric": [
                    "MACD Status",
                    "Bollinger",
                    "ATR",
                    "Volatility",
                    "Trend Strength",
                    "Support",
                    "Resistance",
                    "52W High",
                    "52W Low",
                ],
                "Value": [
                    result.macd_status,
                    result.bb_signal,
                    f"{result.atr:.2f}",
                    result.volatility_level,
                    result.adx_strength,
                    f"${result.support:.2f}",
                    f"${result.resistance:.2f}",
                    f"${result.high_52:.2f}",
                    f"${result.low_52:.2f}",
                ],
            },
            hide_index=True,
            use_container_width=True,
        )
        patterns = ", ".join(result.patterns) if result.patterns else "No pattern detected"
        st.caption(f"🕯️ Candlestick patterns: {patterns}")


def _render_fundamentals(result: Any) -> None:
    """Fundamental expander."""
    with st.expander("🏦  Fundamentals", expanded=False):
        st.progress(
            clamp_pct(result.fundamental_score),
            text=f"Fundamental Score  {result.fundamental_score}/100",
        )
        st.dataframe(
            {
                "Metric": [
                    "Market Cap",
                    "P/E Ratio",
                    "EPS",
                    "Dividend Yield",
                    "Beta",
                    "Revenue",
                    "Profit Margin",
                ],
                "Value": [
                    f"${result.market_cap:,}",
                    result.pe_ratio,
                    result.eps,
                    result.dividend,
                    result.beta,
                    f"${result.revenue:,}",
                    f"{result.profit_margin:.2%}",
                ],
            },
            hide_index=True,
            use_container_width=True,
        )


def _render_news(result: Any) -> None:
    """News expander."""
    with st.expander("📰  News", expanded=False):
        tone = tone_from_text(result.sentiment)
        _cards(metric_card("📡", "Sentiment", result.sentiment, None, tone))
        for item in result.news:
            st.markdown(f"- {item}")


def _render_risk_size_swing(result: Any) -> None:
    """Smart risk, position size, and swing plan columns."""
    sl = result.smart_levels
    pos = result.position
    sw = result.swing
    r1, r2, r3 = st.columns(3, gap="medium")
    with r1:
        with st.expander("🛡️  Smart Risk Management", expanded=True):
            _cards(
                metric_card("🎯", "Entry", f"${sl['entry']:.2f}"),
                metric_card("🛑", "Stop", f"${sl['stop_loss']:.2f}", None, "down"),
                metric_card("⚠️", "Risk", f"{sl['risk_pct']:.2f}%"),
            )
            st.metric("Target 1", f"${sl['target1']:.2f}")
            st.metric("Target 2", f"${sl['target2']:.2f}")
            st.metric("Risk/Reward", f"{sl['risk_reward']:.2f}")
    with r2:
        with st.expander("💼  Position Size", expanded=True):
            st.progress(
                clamp_pct(pos["allocation_pct"]),
                text=f"Allocation  {pos['allocation_pct']:.1f}%",
            )
            st.metric("Capital", f"${pos['capital']:,.2f}")
            st.metric("Risk", f"{pos['risk_pct']:.1f}%")
            st.metric("Maximum Loss", f"${pos['max_loss']:,.2f}")
            st.metric("Suggested Quantity", str(pos["quantity"]))
    with r3:
        with st.expander("🎢  Swing Plan", expanded=True):
            st.progress(
                clamp_pct(sw["probability"]),
                text=f"Success probability  {sw['probability']}%",
            )
            st.metric("Entry", f"${sw['entry']:.2f}")
            st.metric("Stop", f"${sw['stop_loss']:.2f}")
            st.metric("T1 / T2 / T3", f"${sw['target1']:.2f} · ${sw['target2']:.2f} · ${sw['target3']:.2f}")
            st.metric("Holding days", str(sw["holding_days"]))


def _render_summary(result: Any) -> None:
    """AI narrative expander."""
    with st.expander("🧾  AI Summary", expanded=True):
        st.write(result.summary)


def _render_result(result: Any) -> None:
    """Full dashboard body for a completed AnalysisResult."""
    _render_company(result)
    _render_chart_and_score(result)
    _render_decision(result)
    tech, fund = st.columns(2, gap="medium")
    with tech:
        _render_technicals(result)
    with fund:
        _render_fundamentals(result)
        _render_news(result)
    _render_risk_size_swing(result)
    _render_summary(result)


def _run_analysis_with_progress(ticker: str, capital_value: float, risk_value: float):
    """Run the shared pipeline with a progress bar (lazy pipeline import)."""
    from utils.pipeline import run_analysis

    bar = st.progress(12, text="Connecting to market data…")
    try:
        bar.progress(35, text="Fetching quotes, news, and fundamentals…")
        with st.spinner("Running StockShield analysis…"):
            result = run_analysis(ticker, capital=capital_value, risk_pct=risk_value)
        bar.progress(82, text="Rendering terminal…")
        bar.progress(100, text="Live")
        return result
    finally:
        pass


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(
        page_title="StockShield AI",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_theme()
    st.title("📈  StockShield AI")
    st.markdown('<div class="ss-kicker">TERMINAL  ·  DARK BOOK  ·  SAME ENGINES AS THE CLI</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️  Analysis")
        symbol = st.text_input("📌  Stock Symbol", value="AAPL")
        capital = st.number_input("💵  Capital", min_value=100.0, value=10000.0, step=100.0)
        risk_pct = st.number_input(
            "⚠️  Risk %",
            min_value=0.1,
            max_value=10.0,
            value=float(config.RISK_PERCENT),
            step=0.1,
        )
        analyze = st.button("▶  Analyze", type="primary", use_container_width=True)

    if analyze:
        try:
            ticker, capital_value, risk_value = validate_dashboard_inputs(
                symbol, capital, risk_pct
            )
            result = _run_analysis_with_progress(ticker, capital_value, risk_value)
            st.session_state["stockshield_result"] = result
            log_event(ticker, event="dashboard_analysis")
        except InvalidTickerError as exc:
            log_event(str(symbol or "UNKNOWN"), errors=[str(exc)], event="dashboard_error")
            st.error(str(exc))
            return
        except EmptyDataError as exc:
            log_event(str(symbol or "UNKNOWN"), errors=[str(exc)], event="dashboard_error")
            st.error(str(exc))
            return
        except NetworkError as exc:
            log_event(str(symbol or "UNKNOWN"), errors=[str(exc)], event="dashboard_error")
            st.error(str(exc))
            return
        except StockShieldError as exc:
            log_event(str(symbol or "UNKNOWN"), errors=[str(exc)], event="dashboard_error")
            st.error(str(exc))
            return
        except Exception as exc:
            logger.exception("Unexpected dashboard error for %s", symbol or "UNKNOWN")
            log_event(str(symbol or "UNKNOWN"), errors=[repr(exc)], event="dashboard_error")
            st.error("Unexpected error. See logs/ for details.")
            return

    result = st.session_state.get("stockshield_result")
    if result is None:
        st.info("📌 Enter a symbol, capital, and risk % in the sidebar, then click **Analyze**.")
        return
    _render_result(result)


if __name__ == "__main__":
    main()
