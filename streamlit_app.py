"""StockShield AI Streamlit dashboard (dark, responsive)."""

from __future__ import annotations

import os
import tempfile

import streamlit as st

from components.header import render_header
from components.metrics import render_metrics
from components.sidebar import render_sidebar
from utils.app_log import get_logger
from utils.errors import StockShieldError
from utils.session_log import log_event

logger = get_logger("streamlit_app")

st.set_page_config(
    page_title="StockShield AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _card(title: str) -> None:
    """Section heading used by the legacy Streamlit layout."""
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

    render_header()
    controls = render_sidebar()
    symbol = controls["symbol"]
    capital = controls["capital"]
    risk_pct = controls["risk_pct"]
    analyze = controls["analyze"]

    if not analyze:
        render_metrics()
        st.info("Enter a symbol in the sidebar and click **Analyze**.")
        return

    from components.charts import render_charts
    from utils.export_report import export_csv, export_json, export_pdf
    from utils.pipeline import INSTITUTIONAL_LABELS, run_analysis
    from utils.plotly_charts import score_gauge

    try:
        with st.spinner("Fetching market data and running the engine…"):
            result = run_analysis(symbol, capital=capital, risk_pct=risk_pct)
    except StockShieldError as exc:
        log_event(symbol or "UNKNOWN", errors=[str(exc)], event="dashboard_error")
        st.error(str(exc))
        return
    except Exception as exc:
        log_event(symbol or "UNKNOWN", errors=[repr(exc)], event="dashboard_error")
        logger.exception("Dashboard analysis failed for %s", symbol or "UNKNOWN")
        st.error("Unexpected error. See logs/ for details.")
        return

    log_event(result.symbol, event="dashboard_analysis")

    render_metrics(result=result)

    _card("Company Information")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Company", result.company_name)
    c2.metric("Sector", result.sector)
    c3.metric("Price", f"${float(result.latest['Close']):.2f}")
    c4.metric("Today", f"{result.today_percent:+.2f}%")

    left, right = st.columns((2, 1))
    with left:
        _card("Live Trading Chart")
        render_charts(result, show_classic=True)
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
                    f"{result.pe_ratio}",
                    f"{result.eps}",
                    f"{result.dividend}",
                    f"{result.beta}",
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
