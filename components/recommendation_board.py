"""Premium cards for ranked stock suggestions (existing engine output only)."""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from utils.stock_recommendations import (
    NARRATED_KEY,
    RECS_KEY,
    TOP_N,
    maybe_build_suggestions,
    recommendations_narrative,
)

_MESSAGES_KEY = "ss_ip_messages"

_CSS = """
<style>
.ip-rec-wrap {
  background: linear-gradient(180deg, #121a28 0%, #0c1118 100%);
  border: 1px solid #243044;
  border-radius: 14px;
  padding: 1rem 1.1rem;
  margin: 0.85rem 0 0 0;
}
.ip-rec-card {
  background: #162033;
  border: 1px solid #243044;
  border-left: 3px solid #26a69a;
  border-radius: 12px;
  padding: 0.75rem 0.85rem;
  margin: 0.45rem 0;
}
.ip-rec-top {
  display: flex; justify-content: space-between; gap: 0.6rem; align-items: baseline;
}
.ip-rec-ticker { color: #99f6e4; font-size: 1.05rem; font-weight: 700; letter-spacing: 0.04em; }
.ip-rec-co { color: #e8eef7; font-size: 0.92rem; }
.ip-rec-meta { color: #8b9bb4; font-size: 0.78rem; letter-spacing: 0.04em; text-transform: uppercase; }
.ip-rec-score { color: #f0b429; font-size: 1.15rem; font-weight: 700; }
.ip-rec-why { color: #c5d0e0; font-size: 0.84rem; line-height: 1.45; margin-top: 0.4rem; }
</style>
"""


def _price_label(price: Any) -> str:
    try:
        return f"${float(price):.2f}"
    except (TypeError, ValueError):
        return "—"


def render_recommendation_board() -> None:
    """Show top ranked suggestions after Generate Stock Suggestions."""
    if not st.session_state.get("ss_ip_stock_suggestions_requested"):
        return
    st.markdown(_CSS, unsafe_allow_html=True)
    with st.spinner("Running the existing StockShield engine on sector candidates…"):
        rows = maybe_build_suggestions()
    st.markdown('<div class="ip-rec-wrap">', unsafe_allow_html=True)
    st.markdown("**AI Stock Recommendations**")
    st.caption("Ranked by existing AI Score. Same engine as Analyze — not a new model and not a trade ticket.")
    if not rows:
        st.info("No ranked snapshots yet. Sector candidates will appear here after the engine returns.")
        st.markdown("</div>", unsafe_allow_html=True)
        return
    top = rows[:TOP_N]
    header = (
        "| Ticker | Company | Current Price | AI Score | Recommendation | Confidence |\n"
        "| --- | --- | ---: | ---: | --- | --- |\n"
    )
    body = "".join(
        f"| {row.get('ticker')} | {row.get('company')} | {_price_label(row.get('price'))} "
        f"| {row.get('score')} | {row.get('recommendation')} | {row.get('confidence')} |\n"
        for row in top
    )
    st.markdown(header + body)
    for row in top:
        ticker = html.escape(str(row.get("ticker") or ""))
        company = html.escape(str(row.get("company") or ""))
        rec = html.escape(str(row.get("recommendation") or ""))
        confidence = html.escape(str(row.get("confidence") or ""))
        sleeve = html.escape(str(row.get("sleeve") or ""))
        why = html.escape(str(row.get("why") or ""))
        st.markdown(
            f'<div class="ip-rec-card"><div class="ip-rec-top">'
            f'<div><div class="ip-rec-ticker">{ticker}</div>'
            f'<div class="ip-rec-co">{company}</div></div>'
            f'<div class="ip-rec-score">{int(row.get("score") or 0)}</div></div>'
            f'<div class="ip-rec-meta">{sleeve} · {_price_label(row.get("price"))} · {rec} · {confidence}</div>'
            f'<div class="ip-rec-why">{why}</div></div>',
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)
    if not st.session_state.get(NARRATED_KEY):
        history = st.session_state.get(_MESSAGES_KEY)
        if isinstance(history, list):
            history.append({"role": "partner", "text": recommendations_narrative(top)})
            st.session_state[_MESSAGES_KEY] = history
        st.session_state[NARRATED_KEY] = True
    st.session_state[RECS_KEY] = rows
