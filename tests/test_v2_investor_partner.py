"""Investor Partner foundation: intent router plus AppTest coverage."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

from components.investor_partner import (
    SUGGESTED_QUESTIONS,
    TAGLINE,
    TITLE,
    classify_intent,
    partner_reply,
)


def test_intent_router_covers_required_categories():
    assert classify_intent("hello") == "Greeting"
    assert classify_intent("I don't know what to do") == "Investment Advice"
    assert classify_intent("Should I buy this stock?") == "Investment Advice"
    assert classify_intent("Explain RSI") == "Learning"
    assert classify_intent("Build my portfolio") == "Portfolio"
    assert classify_intent("Compare Apple vs Microsoft") == "Comparison"
    assert classify_intent("What is my risk?") == "Investment Advice"
    assert classify_intent("Show me the latest news") == "Market News"
    assert classify_intent("Walk me through this analysis") == "Stock Analysis"
    assert classify_intent("asdf qwerty") == "Unknown"


def test_dont_know_reply_matches_spec():
    reply = partner_reply("I don't know what to do.")
    assert "That's completely okay." in reply
    assert "Your investment goal" in reply
    assert "Your budget" in reply
    assert "Your investment horizon" in reply
    assert "Your risk tolerance" in reply


def _partner_harness() -> None:
    from components.investor_partner import render_investor_partner

    render_investor_partner()


def test_investor_partner_apptest_layout_and_welcome():
    at = AppTest.from_function(_partner_harness, default_timeout=30)
    at.run()
    assert not at.exception
    blob = " ".join(str(item.value) for item in at.markdown)
    assert TITLE in blob
    assert "Your Personal AI Investment Partner" in blob
    assert TAGLINE in blob
    assert "Never Invest Alone" in blob
    buttons = [btn.label for btn in at.button]
    for prompt in SUGGESTED_QUESTIONS:
        assert prompt in buttons
    assert "Send" in buttons
    placeholders = [box.placeholder for box in at.text_input] + [box.label for box in at.text_input]
    assert any("Ask Investor Partner" in str(value) for value in placeholders)
    assert "Welcome." in blob
    assert "Analyze in the sidebar" in blob


def test_investor_partner_suggested_prompt_stores_session_history():
    at = AppTest.from_function(_partner_harness, default_timeout=30)
    at.run()
    at.button(key="ss_ip_suggest_0").click().run()
    assert not at.exception
    history = at.session_state["ss_ip_messages"]
    texts = [item["text"] for item in history]
    assert "I don't know what to do" in texts
    assert any("That's completely okay." in text for text in texts)
