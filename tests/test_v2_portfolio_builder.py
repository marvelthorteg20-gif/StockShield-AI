"""AI Portfolio Builder: allocation rules plus AppTest coverage."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

from components.portfolio_builder import (
    ALLOCATIONS,
    GENERATE_LABEL,
    SUGGESTIONS_KEY,
    allocation_for_risk,
    allocation_from_profile,
    allocation_pie,
    portfolio_narrative,
)


def test_allocation_tables_match_specified_weights():
    assert ALLOCATIONS["Conservative"] == (
        ("Index Funds", 40),
        ("Banking", 20),
        ("Healthcare", 20),
        ("Gold", 10),
        ("Cash", 10),
    )
    assert ALLOCATIONS["Moderate"] == (
        ("Index Funds", 30),
        ("Technology", 25),
        ("Banking", 20),
        ("Healthcare", 15),
        ("Cash", 10),
    )
    assert ALLOCATIONS["Aggressive"] == (
        ("Technology", 40),
        ("AI & Semiconductor", 25),
        ("Index Funds", 15),
        ("Healthcare", 10),
        ("Cash", 10),
    )
    for slices in ALLOCATIONS.values():
        assert sum(pct for _, pct in slices) == 100


def test_unknown_risk_falls_back_to_moderate():
    assert allocation_for_risk("Mystery") == ALLOCATIONS["Moderate"]
    assert allocation_from_profile({"Risk": "Aggressive"}) == ALLOCATIONS["Aggressive"]


def test_partner_narrative_explains_each_sleeve():
    text = portfolio_narrative({"Risk": "Conservative"})
    assert "conservative" in text.lower()
    assert "Index Funds 40%" in text
    assert "Gold 10%" in text
    assert "StockShield engine" in text


def test_allocation_pie_uses_profile_weights():
    fig = allocation_pie(ALLOCATIONS["Moderate"], "Moderate allocation")
    assert list(fig.data[0].labels) == [
        "Index Funds",
        "Technology",
        "Banking",
        "Healthcare",
        "Cash",
    ]
    assert list(fig.data[0].values) == [30, 25, 20, 15, 10]


def _partner_harness() -> None:
    from components.investor_partner import render_investor_partner

    render_investor_partner()


def _complete_default_wizard(at: AppTest) -> AppTest:
    at.run()
    for _ in range(5):
        at.button(key="ss_ip_wiz_next").click().run()
        assert not at.exception
    return at


def test_portfolio_builder_apptest_shows_moderate_cards_and_pie():
    at = _complete_default_wizard(AppTest.from_function(_partner_harness, default_timeout=30))
    profile = at.session_state["ss_ip_profile"]
    assert profile["Risk"] == "Moderate"
    blob = " ".join(str(item.value) for item in at.markdown)
    assert "AI Portfolio Builder" in blob
    assert "Index Funds" in blob
    assert "30%" in blob
    assert "Technology" in blob
    assert "25%" in blob
    assert "Banking" in blob
    assert "20%" in blob
    assert "Healthcare" in blob
    assert "15%" in blob
    assert "Cash" in blob
    assert "10%" in blob
    charts = at.get("plotly_chart")
    assert len(charts) >= 1
    spec = charts[0].proto.spec
    assert '"type":"pie"' in spec
    assert '"values":[30,25,20,15,10]' in spec
    assert GENERATE_LABEL in [btn.label for btn in at.button]
    history = at.session_state["ss_ip_messages"]
    partner_text = " ".join(item["text"] for item in history if item.get("role") == "partner")
    assert "Index Funds 30%" in partner_text
    assert "Technology 25%" in partner_text


def test_generate_stock_suggestions_does_not_invent_tickers():
    at = _complete_default_wizard(AppTest.from_function(_partner_harness, default_timeout=30))
    at.button(key="ss_ip_gen_stocks_btn").click().run()
    assert not at.exception
    assert at.session_state[SUGGESTIONS_KEY] is True
    blob = " ".join(str(item.value) for item in at.markdown)
    info_text = " ".join(str(item.value) for item in at.info)
    assert "not generated yet" in info_text.lower()
    for ticker in ("AAPL", "MSFT", "NVDA", "TSLA", "GOOGL"):
        assert ticker not in blob
    history = at.session_state["ss_ip_messages"]
    partner_text = " ".join(item["text"] for item in history if item.get("role") == "partner")
    for ticker in ("AAPL", "MSFT", "NVDA"):
        assert ticker not in partner_text
