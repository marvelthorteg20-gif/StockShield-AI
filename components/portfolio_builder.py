"""Rule-based AI portfolio allocation for Investor Partner (no analysis engine)."""

from __future__ import annotations

from typing import Any, Sequence

import plotly.graph_objects as go
import streamlit as st

from components.investment_profile import PROFILE_KEY, is_profile_complete

SUGGESTIONS_KEY = "ss_ip_stock_suggestions_requested"
EXPLAINED_KEY = "ss_ip_portfolio_explained"
GENERATE_LABEL = "Generate Stock Suggestions"

ALLOCATIONS: dict[str, tuple[tuple[str, int], ...]] = {
    "Conservative": (
        ("Index Funds", 40),
        ("Banking", 20),
        ("Healthcare", 20),
        ("Gold", 10),
        ("Cash", 10),
    ),
    "Moderate": (
        ("Index Funds", 30),
        ("Technology", 25),
        ("Banking", 20),
        ("Healthcare", 15),
        ("Cash", 10),
    ),
    "Aggressive": (
        ("Technology", 40),
        ("AI & Semiconductor", 25),
        ("Index Funds", 15),
        ("Healthcare", 10),
        ("Cash", 10),
    ),
}

REASONS: dict[str, dict[str, str]] = {
    "Conservative": {
        "Index Funds": "Broad market exposure keeps the core of the plan diversified and low-maintenance.",
        "Banking": "Established financials can add income and stability without stretching into high beta.",
        "Healthcare": "Defensive demand helps cushion drawdowns if growth assets stall.",
        "Gold": "A small hard-asset sleeve can offset inflation and equity stress.",
        "Cash": "Dry powder covers short-term needs so you are not forced to sell in a dip.",
    },
    "Moderate": {
        "Index Funds": "The index core still anchors the book while leaving room for satellite growth.",
        "Technology": "A measured growth sleeve can compound wealth if your horizon is measured in years.",
        "Banking": "Financials balance the tech tilt with cash-flow and domestic cycle exposure.",
        "Healthcare": "Quality defensives reduce the chance the whole book moves as one trade.",
        "Cash": "Liquidity remains for rebalancing and unexpected expenses.",
    },
    "Aggressive": {
        "Technology": "The growth engine of an aggressive plan — higher expected return with higher path risk.",
        "AI & Semiconductor": "A concentrated innovation sleeve for long-horizon builders who accept volatility.",
        "Index Funds": "A remaining market core stops the book from becoming a single-theme bet.",
        "Healthcare": "A defensive minority sleeve so a growth shock is not a total-plan shock.",
        "Cash": "Even aggressive plans keep a cash buffer for entries and personal cash-flow.",
    },
}

_COLORS = ("#26a69a", "#42a5f5", "#f0b429", "#ce93d8", "#8b9bb4", "#ef5350")

_CSS = """
<style>
.ip-alloc {
  background: linear-gradient(180deg, #121a28 0%, #0c1118 100%);
  border: 1px solid #243044;
  border-radius: 14px;
  padding: 1rem 1.1rem;
  margin: 0 0 1rem 0;
}
.ip-alloc-card {
  background: #162033;
  border: 1px solid #243044;
  border-top: 3px solid #26a69a;
  border-radius: 12px;
  padding: 0.7rem 0.8rem;
  min-height: 7.5rem;
}
.ip-alloc-name { color: #8b9bb4; font-size: 0.75rem; letter-spacing: 0.08em; text-transform: uppercase; }
.ip-alloc-pct { color: #e8eef7; font-size: 1.35rem; font-weight: 700; margin: 0.2rem 0; }
.ip-alloc-why { color: #c5d0e0; font-size: 0.82rem; line-height: 1.4; }
</style>
"""


def allocation_for_risk(risk: str) -> tuple[tuple[str, int], ...]:
    """Return sleeve weights for a risk label. Unknown risk uses Moderate."""
    return ALLOCATIONS.get(str(risk or "").strip(), ALLOCATIONS["Moderate"])


def allocation_from_profile(profile: dict[str, Any] | None) -> tuple[tuple[str, int], ...]:
    """Read Risk from the stored Investment Profile and return allocation tuples."""
    risk = ""
    if isinstance(profile, dict):
        risk = str(profile.get("Risk") or "")
    return allocation_for_risk(risk)


def why_for_sleeve(risk: str, sleeve: str) -> str:
    """Return the canned explanation for one sleeve under a risk plan."""
    table = REASONS.get(str(risk or "").strip()) or REASONS["Moderate"]
    return table.get(sleeve, "This sleeve is part of the selected risk plan.")


def portfolio_narrative(profile: dict[str, Any] | None) -> str:
    """Investor Partner explanation of the full allocation."""
    risk = "Moderate"
    if isinstance(profile, dict) and profile.get("Risk"):
        risk = str(profile["Risk"])
    lines = [
        f"Here is a starter allocation for a {risk.lower()} profile.",
        "These weights are planning rules, not live trades, and they do not call the StockShield engine.",
        "",
    ]
    for sleeve, pct in allocation_for_risk(risk):
        lines.append(f"• {sleeve} {pct}% — {why_for_sleeve(risk, sleeve)}")
    return "\n".join(lines)


def allocation_pie(slices: Sequence[tuple[str, int]], title: str = "Allocation") -> go.Figure:
    """Dark Plotly pie of existing allocation weights."""
    labels = [name for name, _ in slices]
    values = [pct for _, pct in slices]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.48,
            marker=dict(colors=list(_COLORS[: len(labels)]), line=dict(color="#0c1118", width=2)),
            textinfo="label+percent",
            hovertemplate="%{label}: %{value}%<extra></extra>",
        )
    )
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color="#d1d4dc")),
        template="plotly_dark",
        paper_bgcolor="#0e1420",
        plot_bgcolor="#0e1420",
        font=dict(color="#d1d4dc", family="IBM Plex Sans, Segoe UI, sans-serif"),
        margin=dict(l=16, r=16, t=48, b=16),
        height=360,
        showlegend=False,
    )
    return fig


def render_portfolio_builder() -> None:
    """Show allocation cards, pie, reasons, and the suggestions placeholder button."""
    if not is_profile_complete():
        return
    profile = dict(st.session_state.get(PROFILE_KEY) or {})
    risk = str(profile.get("Risk") or "Moderate")
    slices = allocation_from_profile(profile)
    st.markdown(_CSS, unsafe_allow_html=True)
    st.markdown('<div class="ip-alloc">', unsafe_allow_html=True)
    st.markdown("**AI Portfolio Builder**")
    st.caption(f"Personalized from your {risk} investment profile. Planning only — not a trade ticket.")

    cols = st.columns(len(slices))
    for column, (sleeve, pct) in zip(cols, slices):
        with column:
            st.markdown(
                f'<div class="ip-alloc-card"><div class="ip-alloc-name">{sleeve}</div>'
                f'<div class="ip-alloc-pct">{pct}%</div>'
                f'<div class="ip-alloc-why">{why_for_sleeve(risk, sleeve)}</div></div>',
                unsafe_allow_html=True,
            )

    st.plotly_chart(
        allocation_pie(slices, f"{risk} allocation"),
        use_container_width=True,
        config={"displaylogo": False},
    )
    if st.button(GENERATE_LABEL, type="primary", key="ss_ip_gen_stocks_btn"):
        st.session_state[SUGGESTIONS_KEY] = True
    if st.session_state.get(SUGGESTIONS_KEY):
        st.info("Stock suggestions are not generated yet. That slice comes next.")
    st.markdown("</div>", unsafe_allow_html=True)
