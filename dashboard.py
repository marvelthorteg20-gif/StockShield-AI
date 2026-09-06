"""StockShield AI Streamlit dashboard.

Presentation only: all scores, signals, and risk numbers come from
``utils.pipeline.run_analysis`` (the same stack ``app.py`` uses).
"""

from __future__ import annotations

from typing import Any, Tuple

import streamlit as st

import config
from utils.errors import EmptyDataError, InvalidTickerError, NetworkError, StockShieldError
from utils.market_data import validate_symbol
from utils.pipeline import run_analysis
from utils.plotly_charts import candlestick_figure, score_gauge
from utils.session_log import log_event


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
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.1rem; max-width: 1320px; }
        div[data-testid="stMetric"] {
            background: #151c2c;
            border: 1px solid #243044;
            border-radius: 12px;
            padding: 0.55rem 0.75rem;
        }
        section[data-testid="stSidebar"] {
            background: #101827;
        }
        h1, h2, h3 { letter-spacing: 0.01em; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _section(title: str) -> None:
    st.markdown(f"### {title}")


def _render_result(result: Any) -> None:
    latest = result.latest
    _section("Company Information")
    a, b, c, d = st.columns(4)
    a.metric("Company", result.company_name)
    b.metric("Sector", result.sector)
    c.metric("Price", f"${float(latest['Close']):.2f}")
    d.metric("Today", f"{result.today_percent:+.2f}%")

    chart_col, score_col = st.columns((2.1, 1))
    with chart_col:
        _section("Candlestick Chart")
        history = result.history
        required = {"Open", "High", "Low", "Close"}
        if history is None or getattr(history, "empty", True) or not required.issubset(history.columns):
            st.error("Candlestick data is incomplete.")
        else:
            st.plotly_chart(
                candlestick_figure(history, f"{result.company_name} · {result.symbol}"),
                use_container_width=True,
            )
    with score_col:
        _section("AI Score")
        st.plotly_chart(score_gauge(result.score), use_container_width=True)
        st.metric("Rating", result.rating)
        st.metric("Confidence", result.confidence)
        st.metric("Recommendation", result.recommendation)

    _section("Decision Engine")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Action", result.decision["action"])
    d2.metric("Confidence", f"{result.decision['confidence']}%")
    d3.metric("Probability", f"{result.decision['probability']}%")
    d4.metric("Holding Period", result.decision["holding_period"])
    st.write("Risk/Reward:", result.decision["risk_reward_rating"])
    for reason in result.decision.get("reasons") or []:
        st.markdown(f"- {reason}")

    tech_col, fund_col = st.columns(2)
    with tech_col:
        _section("Technical Indicators")
        st.dataframe(
            {
                "Metric": [
                    "SMA20",
                    "EMA20",
                    "RSI",
                    "Trend",
                    "MACD",
                    "Signal Line",
                    "MACD Status",
                    "Bollinger",
                    "Volume",
                    "ATR",
                    "Volatility",
                    "ADX",
                    "Trend Strength",
                    "Support",
                    "Resistance",
                ],
                "Value": [
                    f"${float(latest['SMA20']):.2f}",
                    f"${float(latest['EMA20']):.2f}",
                    f"{result.rsi:.2f}",
                    result.trend,
                    f"{float(latest['MACD']):.2f}",
                    f"{float(latest['MACD_SIGNAL']):.2f}",
                    result.macd_status,
                    result.bb_signal,
                    result.volume_status,
                    f"{result.atr:.2f}",
                    result.volatility_level,
                    f"{result.adx:.2f}",
                    result.adx_strength,
                    f"${result.support:.2f}",
                    f"${result.resistance:.2f}",
                ],
            },
            hide_index=True,
            use_container_width=True,
        )
        patterns = ", ".join(result.patterns) if result.patterns else "No pattern detected"
        st.caption(f"Candlestick patterns: {patterns}")
    with fund_col:
        _section("Fundamentals")
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
                    "Fundamental Score",
                ],
                "Value": [
                    f"${result.market_cap:,}",
                    result.pe_ratio,
                    result.eps,
                    result.dividend,
                    result.beta,
                    f"${result.revenue:,}",
                    f"{result.profit_margin:.2%}",
                    f"{result.fundamental_score}/100",
                ],
            },
            hide_index=True,
            use_container_width=True,
        )

    _section("News")
    st.write("Overall sentiment:", result.sentiment)
    for item in result.news:
        st.markdown(f"- {item}")

    risk_col, size_col, swing_col = st.columns(3)
    with risk_col:
        _section("Smart Risk Management")
        sl = result.smart_levels
        st.metric("Entry Price", f"${sl['entry']:.2f}")
        st.metric("Stop Loss", f"${sl['stop_loss']:.2f}")
        st.metric("Risk %", f"{sl['risk_pct']:.2f}%")
        st.metric("Target 1", f"${sl['target1']:.2f}")
        st.metric("Target 2", f"${sl['target2']:.2f}")
        st.metric("Risk/Reward", f"{sl['risk_reward']:.2f}")
    with size_col:
        _section("Position Size")
        pos = result.position
        st.metric("Capital", f"${pos['capital']:,.2f}")
        st.metric("Risk", f"{pos['risk_pct']:.1f}%")
        st.metric("Maximum Loss", f"${pos['max_loss']:,.2f}")
        st.metric("Suggested Quantity", str(pos["quantity"]))
        st.metric("Allocation", f"{pos['allocation_pct']:.2f}%")
    with swing_col:
        _section("Swing Plan")
        sw = result.swing
        st.metric("Entry Price", f"${sw['entry']:.2f}")
        st.metric("Stop Loss", f"${sw['stop_loss']:.2f}")
        st.metric("Target 1", f"${sw['target1']:.2f}")
        st.metric("Target 2", f"${sw['target2']:.2f}")
        st.metric("Target 3", f"${sw['target3']:.2f}")
        st.metric("Holding Days", str(sw["holding_days"]))
        st.metric("Probability", f"{sw['probability']}%")

    _section("AI Summary")
    st.write(result.summary)


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(
        page_title="StockShield AI",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_theme()
    st.title("StockShield AI")
    st.caption("Professional dashboard · same engines as the CLI")

    with st.sidebar:
        st.header("Analysis")
        symbol = st.text_input("Stock Symbol", value="AAPL")
        capital = st.number_input("Capital", min_value=100.0, value=10000.0, step=100.0)
        risk_pct = st.number_input(
            "Risk %",
            min_value=0.1,
            max_value=10.0,
            value=float(config.RISK_PERCENT),
            step=0.1,
        )
        analyze = st.button("Analyze", type="primary", use_container_width=True)

    if analyze:
        try:
            ticker, capital_value, risk_value = validate_dashboard_inputs(
                symbol, capital, risk_pct
            )
            with st.spinner("Running StockShield analysis…"):
                result = run_analysis(
                    ticker, capital=capital_value, risk_pct=risk_value
                )
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
            log_event(str(symbol or "UNKNOWN"), errors=[repr(exc)], event="dashboard_error")
            st.error("Unexpected error. See logs/ for details.")
            return

    result = st.session_state.get("stockshield_result")
    if result is None:
        st.info("Enter a symbol, capital, and risk % in the sidebar, then click **Analyze**.")
        return
    _render_result(result)


if __name__ == "__main__":
    main()
