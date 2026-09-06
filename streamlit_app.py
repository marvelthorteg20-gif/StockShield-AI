"""StockShield AI Streamlit dashboard (dark, responsive)."""

from __future__ import annotations

import os
import tempfile

import streamlit as st

import config
from utils.errors import StockShieldError
from utils.export_report import export_csv, export_json, export_pdf
from utils.pipeline import INSTITUTIONAL_LABELS, run_analysis
from utils.plotly_charts import candlestick_figure, score_gauge
from utils.session_log import log_event

st.set_page_config(
    page_title="StockShield AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _card(title: str) -> None:
    st.markdown(f"### {title}")


def render_dashboard() -> None:
    """Draw the professional analysis workspace."""
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.2rem; max-width: 1400px; }
        div[data-testid="stMetric"] {
            background: #151c2c;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 0.6rem 0.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("StockShield AI")
    st.caption("Professional equity terminal · dark workspace")

    with st.sidebar:
        st.header("Controls")
        symbol = st.text_input("Stock Symbol", value="AAPL").strip().upper()
        capital = st.number_input("Capital", min_value=100.0, value=10000.0, step=100.0)
        risk_pct = st.number_input(
            "Risk %",
            min_value=0.1,
            max_value=10.0,
            value=float(config.RISK_PERCENT),
            step=0.1,
        )
        analyze = st.button("Analyze", type="primary", use_container_width=True)
        st.markdown("---")
        st.caption("Yahoo Finance · Alpha Vantage news")

    if not analyze:
        st.info("Enter a symbol in the sidebar and click **Analyze**.")
        return

    try:
        with st.spinner("Fetching market data and running the engine…"):
            result = run_analysis(symbol, capital=capital, risk_pct=risk_pct)
    except StockShieldError as exc:
        log_event(symbol or "UNKNOWN", errors=[str(exc)], event="dashboard_error")
        st.error(str(exc))
        return
    except Exception as exc:
        log_event(symbol or "UNKNOWN", errors=[repr(exc)], event="dashboard_error")
        st.error("Unexpected error. See logs/ for details.")
        return

    log_event(result.symbol, event="dashboard_analysis")

    _card("Company Information")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Company", result.company_name)
    c2.metric("Sector", result.sector)
    c3.metric("Price", f"${float(result.latest['Close']):.2f}")
    c4.metric("Today", f"{result.today_percent:+.2f}%")

    left, right = st.columns((2, 1))
    with left:
        _card("Live Candlestick Chart")
        st.plotly_chart(
            candlestick_figure(result.history, f"{result.company_name} · {result.symbol}"),
            use_container_width=True,
        )
    with right:
        _card("AI Score Gauge")
        st.plotly_chart(score_gauge(result.score), use_container_width=True)
        st.metric("Rating", result.rating)
        st.metric("Confidence", result.confidence)

    _card("Decision Engine")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Action", result.decision["action"])
    d2.metric("Confidence", f"{result.decision['confidence']}%")
    d3.metric("Probability", f"{result.decision['probability']}%")
    d4.metric("Holding", result.decision["holding_period"])
    st.write("**Risk/Reward:**", result.decision["risk_reward_rating"])
    st.write("**Trade rating:**", result.star["display"])
    for reason in result.decision["reasons"]:
        st.markdown(f"- {reason}")

    tech, fund = st.columns(2)
    with tech:
        _card("Technical Indicators")
        latest = result.latest
        st.dataframe(
            {
                "Metric": [
                    "SMA20",
                    "EMA20",
                    "RSI",
                    "Trend",
                    "MACD",
                    "Signal",
                    "MACD Status",
                    "Bollinger",
                    "Volume",
                    "ATR",
                    "Volatility",
                    "ADX",
                    "Trend Strength",
                    "Support",
                    "Resistance",
                    "52W High",
                    "52W Low",
                    "Recommendation",
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
                    f"${result.high_52:.2f}",
                    f"${result.low_52:.2f}",
                    result.recommendation,
                ],
            },
            hide_index=True,
            use_container_width=True,
        )
        st.write("**Patterns:**", ", ".join(result.patterns) or "No pattern detected")
    with fund:
        _card("Fundamentals")
        st.dataframe(
            {
                "Metric": [
                    "Market Cap",
                    "P/E",
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

    _card("News Sentiment")
    st.write("Overall:", result.sentiment)
    for item in result.news:
        st.markdown(f"- {item}")

    r1, r2, r3 = st.columns(3)
    with r1:
        _card("Smart Risk")
        sl = result.smart_levels
        st.metric("Entry", f"${sl['entry']:.2f}")
        st.metric("Stop Loss", f"${sl['stop_loss']:.2f}")
        st.metric("Risk %", f"{sl['risk_pct']:.2f}%")
        st.metric("Target 1", f"${sl['target1']:.2f}")
        st.metric("Target 2", f"${sl['target2']:.2f}")
        st.metric("R/R", f"{sl['risk_reward']:.2f}")
    with r2:
        _card("Swing Plan")
        sw = result.swing
        st.metric("Entry", f"${sw['entry']:.2f}")
        st.metric("Stop", f"${sw['stop_loss']:.2f}")
        st.metric("T1 / T2 / T3", f"${sw['target1']:.2f} / ${sw['target2']:.2f} / ${sw['target3']:.2f}")
        st.metric("Holding days", str(sw["holding_days"]))
        st.metric("Success %", f"{sw['probability']}%")
    with r3:
        _card("Position Size")
        pos = result.position
        st.metric("Capital", f"${pos['capital']:,.2f}")
        st.metric("Risk", f"{pos['risk_pct']:.1f}%")
        st.metric("Max loss", f"${pos['max_loss']:,.2f}")
        st.metric("Quantity", str(pos["quantity"]))
        st.metric("Allocation", f"{pos['allocation_pct']:.2f}%")

    _card("Multi-Timeframe Analysis")
    tf = result.timeframes
    tcols = st.columns(5)
    for col, key in zip(tcols, ("1D", "1W", "1M", "3M", "1Y")):
        col.metric(key, tf[key])
    st.metric("Overall Trend Alignment", f"{tf['alignment']}%")

    _card("Institutional Signals")
    rows = []
    for key, label in INSTITUTIONAL_LABELS:
        payload = result.institutional[key]
        rows.append(
            {
                "Signal": label,
                "Detected": "Yes" if payload["detected"] else "No",
                "Confidence": f"{payload['confidence']}%",
            }
        )
    st.dataframe(rows, hide_index=True, use_container_width=True)

    _card("Support & Resistance")
    if result.sr_levels:
        st.dataframe(
            [
                {
                    "Strength": "★" * item["strength"],
                    "Kind": item["kind"],
                    "Price": f"${item['price']:.2f}",
                    "Name": item["name"],
                }
                for item in result.sr_levels
            ],
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.write("Levels unavailable")

    _card("AI Summary")
    st.write(result.summary)

    _card("Export")
    payload = result.export_payload()
    tmp = tempfile.mkdtemp(prefix="stockshield_")
    json_path = export_json(payload, os.path.join(tmp, f"{result.symbol}.json"))
    csv_path = export_csv(payload, os.path.join(tmp, f"{result.symbol}.csv"))
    pdf_path = export_pdf(
        payload,
        os.path.join(tmp, f"{result.symbol}.pdf"),
        title=f"StockShield AI - {result.symbol}",
    )
    b1, b2, b3 = st.columns(3)
    with open(json_path, "rb") as handle:
        b1.download_button("Download JSON", handle, file_name=f"{result.symbol}.json")
    with open(csv_path, "rb") as handle:
        b2.download_button("Download CSV", handle, file_name=f"{result.symbol}.csv")
    with open(pdf_path, "rb") as handle:
        b3.download_button("Download PDF", handle, file_name=f"{result.symbol}.pdf")


render_dashboard()
