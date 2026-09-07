"""AI investment profile wizard: session storage plus AppTest coverage."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

from components.investment_profile import (
    PROFILE_READY_MESSAGE,
    START_INVESTING_LABEL,
    format_profile,
)


def test_format_profile_maps_wizard_answers():
    card = format_profile(
        {
            "budget": 25000,
            "goal": "Retirement",
            "risk": "Conservative",
            "horizon": "5+ Years",
            "experience": "Beginner",
        }
    )
    assert card["Budget"] == "₹25,000"
    assert card["Goal"] == "Retirement"
    assert card["Risk"] == "Conservative"
    assert card["Experience"] == "Beginner"
    assert card["Horizon"] == "5+ Years"


def _wizard_harness() -> None:
    from components.investor_partner import render_investor_partner

    render_investor_partner()


def test_profile_wizard_apptest_starts_on_budget_step():
    at = AppTest.from_function(_wizard_harness, default_timeout=30)
    at.run()
    assert not at.exception
    blob = " ".join(str(item.value) for item in at.markdown)
    assert "Investment Budget" in blob or any(
        "Investment Budget" in str(box.label) for box in at.number_input
    )
    assert "₹" in blob
    assert "Step 1 of 5" in blob
    assert "Next" in [btn.label for btn in at.button]


def test_profile_wizard_completion_stores_profile_and_partner_message():
    at = AppTest.from_function(_wizard_harness, default_timeout=30)
    at.run()
    at.number_input(key="ss_ip_budget").set_value(50000).run()
    for _ in range(5):
        at.button(key="ss_ip_wiz_next").click().run()
        assert not at.exception
    profile = at.session_state["ss_ip_profile"]
    assert profile["Budget"] == "₹50,000"
    assert profile["Goal"] == "Wealth Creation"
    assert profile["Risk"] == "Moderate"
    assert profile["Horizon"] == "3 Years"
    assert profile["Experience"] == "Beginner"
    blob = " ".join(str(item.value) for item in at.markdown)
    assert "Investment Profile" in blob
    assert START_INVESTING_LABEL in [btn.label for btn in at.button]
    history = at.session_state["ss_ip_messages"]
    assert any(PROFILE_READY_MESSAGE in item["text"] for item in history)


def test_start_investing_button_sets_session_flag():
    at = AppTest.from_function(_wizard_harness, default_timeout=30)
    at.run()
    for _ in range(5):
        at.button(key="ss_ip_wiz_next").click().run()
    at.button(key="ss_ip_start_investing_btn").click().run()
    assert not at.exception
    assert at.session_state["ss_ip_start_investing"] is True
