"""Investor Partner — premium chat shell (no LLM, no analysis engine)."""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from components.investment_profile import (
    PROFILE_READY_MESSAGE,
    consume_profile_ready_event,
    is_profile_complete,
    render_investment_profile,
)
from components.portfolio_builder import (
    EXPLAINED_KEY,
    portfolio_narrative,
    render_portfolio_builder,
)

TITLE = "🧠 Investor Partner"
SUBTITLE = "Your Personal AI Investment Partner"
TAGLINE = "Think Smarter. Invest Wiser. Never Invest Alone."
INPUT_PLACEHOLDER = "Ask Investor Partner..."

INTENTS: tuple[str, ...] = (
    "Greeting",
    "Investment Advice",
    "Stock Analysis",
    "Portfolio",
    "Learning",
    "Comparison",
    "Market News",
    "Unknown",
)

SUGGESTED_QUESTIONS: tuple[str, ...] = (
    "I don't know what to do",
    "Should I buy this stock?",
    "Explain RSI",
    "Build my portfolio",
    "Compare Apple vs Microsoft",
    "What is my risk?",
)

WELCOME_MESSAGE = (
    "Welcome. I'm Investor Partner — here to think with you, not replace your judgment.\n\n"
    "Ask a question, or pick a prompt on the left. I will never place a trade for you, "
    "and I will not silently run the StockShield engine. When you want numbers, "
    "use Analyze in the sidebar."
)

_MESSAGES_KEY = "ss_ip_messages"
_PENDING_KEY = "ss_ip_pending"

_CSS = """
<style>
.ip-wrap { margin: 0.6rem 0 1.2rem 0; }
.ip-title { color: #e8eef7; font-size: 1.55rem; font-weight: 700; margin: 0; }
.ip-sub { color: #99f6e4; font-size: 1.02rem; margin: 0.15rem 0 0.2rem 0; }
.ip-tag { color: #8b9bb4; font-size: 0.88rem; letter-spacing: 0.04em; margin: 0 0 0.8rem 0; }
.ip-thread {
  max-height: 420px;
  overflow-y: auto;
  padding: 0.75rem 0.85rem;
  background: linear-gradient(180deg, #101722 0%, #0c1118 100%);
  border: 1px solid #243044;
  border-radius: 14px;
}
.ip-bubble {
  max-width: 92%;
  margin: 0.45rem 0;
  padding: 0.7rem 0.9rem;
  border-radius: 14px;
  line-height: 1.45;
  font-size: 0.95rem;
  white-space: pre-wrap;
}
.ip-partner {
  background: #162033;
  border: 1px solid #243044;
  color: #e8eef7;
  border-bottom-left-radius: 4px;
}
.ip-user {
  background: #134e4a;
  border: 1px solid #115e59;
  color: #ccfbf1;
  margin-left: auto;
  border-bottom-right-radius: 4px;
}
.ip-who {
  font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase;
  color: #8b9bb4; margin-bottom: 0.25rem;
}
</style>
"""

_DONT_KNOW_REPLY = (
    "That's completely okay.\n\n"
    "Let's build an investment plan together.\n\n"
    "Before recommending anything, I'd like to know:\n"
    "• Your investment goal\n"
    "• Your budget\n"
    "• Your investment horizon\n"
    "• Your risk tolerance\n\n"
    "Once I know these, I'll guide you step by step."
)

_REPLIES: dict[str, str] = {
    "Greeting": (
        "Hello. I'm Investor Partner.\n\n"
        "Tell me what you want to work on — a ticker, a portfolio question, "
        "or a concept you'd like explained. We'll go one clear step at a time."
    ),
    "Investment Advice": (
        "I can help you think through a decision, but I will not issue a buy or sell order.\n\n"
        "Share your goal, budget, time horizon, and risk comfort. Then we can map "
        "whether this idea even belongs in your plan — before looking at any chart."
    ),
    "Stock Analysis": (
        "For live scores, RSI, MACD, and risk levels, run Analyze in the sidebar. "
        "That uses the same StockShield engine as the CLI.\n\n"
        "I can then help you interpret those existing outputs in plain language. "
        "I do not recalculate indicators in this chat."
    ),
    "Portfolio": (
        "We can sketch a portfolio framework here — allocation buckets, time horizon, "
        "and how much risk you are willing to take.\n\n"
        "I will not size positions from this chat. Use Analyze for quantity and "
        "risk numbers from the existing engine, then we can discuss how they fit."
    ),
    "Learning": (
        "Happy to explain the idea in practical terms.\n\n"
        "RSI, for example, is a 0–100 momentum reading StockShield already computes. "
        "High readings often mean stretched buying; low readings often mean stretched selling. "
        "It is a context tool, not a standalone buy signal."
    ),
    "Comparison": (
        "A side-by-side view works best with two completed analyses.\n\n"
        "Analyze each symbol in the sidebar, then come back and tell me which two names "
        "you want compared — trend, score, and risk using those existing results. "
        "I will not invent new numbers here."
    ),
    "Market News": (
        "Headline sentiment in StockShield comes from the existing news module after Analyze.\n\n"
        "I do not fetch a live wire from this chat. Run Analyze for the current symbol "
        "to load stored headlines, then ask me to help you read the tone."
    ),
    "Unknown": (
        "I want to be precise, and I'm not sure what you need yet.\n\n"
        "Try a prompt from the left, or tell me whether this is about a stock, "
        "your portfolio, a concept, or a comparison."
    ),
}


def classify_intent(text: str) -> str:
    """Map free text to a coarse intent. Keyword rules only — no LLM."""
    raw = str(text or "").strip()
    lowered = raw.lower()
    if not lowered:
        return "Unknown"
    if any(token in lowered for token in (" vs ", "versus", "compare ")):
        return "Comparison"
    if lowered.startswith("explain") or lowered.startswith("what is ") or "what is rsi" in lowered:
        if "risk" in lowered and "rsi" not in lowered:
            return "Investment Advice"
        return "Learning"
    if "portfolio" in lowered or "allocation" in lowered or "diversif" in lowered:
        return "Portfolio"
    if "news" in lowered or "headline" in lowered:
        return "Market News"
    if any(token in lowered for token in ("rsi", "macd", "sma", "ema", "analy")):
        return "Stock Analysis"
    if (
        "don't know" in lowered
        or "dont know" in lowered
        or "should i buy" in lowered
        or "should i sell" in lowered
        or "what is my risk" in lowered
        or lowered.startswith("invest")
    ):
        return "Investment Advice"
    if lowered in {"hi", "hello", "hey"} or lowered.startswith(("hi ", "hello ", "hey ")):
        return "Greeting"
    return "Unknown"


def partner_reply(text: str) -> str:
    """Return the canned professional reply for the detected intent."""
    lowered = str(text or "").strip().lower()
    if "don't know" in lowered or "dont know" in lowered:
        return _DONT_KNOW_REPLY
    return _REPLIES[classify_intent(text)]


def _ensure_history() -> list[dict[str, Any]]:
    history = st.session_state.get(_MESSAGES_KEY)
    if not isinstance(history, list) or not history:
        history = [{"role": "partner", "text": WELCOME_MESSAGE}]
        st.session_state[_MESSAGES_KEY] = history
    return history


def _append_turn(user_text: str) -> None:
    text = str(user_text or "").strip()
    if not text:
        return
    history = _ensure_history()
    history.append({"role": "user", "text": text})
    history.append({"role": "partner", "text": partner_reply(text)})
    st.session_state[_MESSAGES_KEY] = history


def _bubble_html(role: str, text: str) -> str:
    kind = "ip-user" if role == "user" else "ip-partner"
    who = "You" if role == "user" else "Investor Partner"
    body = html.escape(text).replace("\n", "<br>")
    return f'<div class="ip-bubble {kind}"><div class="ip-who">{who}</div>{body}</div>'


def render_investor_partner() -> None:
    """Premium chat layout with suggested prompts, history, and send box."""
    st.markdown(_CSS, unsafe_allow_html=True)
    pending = st.session_state.pop(_PENDING_KEY, None)
    if pending:
        _append_turn(str(pending))

    st.markdown('<div class="ip-wrap">', unsafe_allow_html=True)
    st.markdown(f'<p class="ip-title">{html.escape(TITLE)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="ip-sub">{html.escape(SUBTITLE)}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="ip-tag">{html.escape(TAGLINE)}</p>', unsafe_allow_html=True)

    render_investment_profile()
    if consume_profile_ready_event():
        history = _ensure_history()
        history.append({"role": "partner", "text": PROFILE_READY_MESSAGE})
        st.session_state[_MESSAGES_KEY] = history
    if is_profile_complete() and not st.session_state.get(EXPLAINED_KEY):
        history = _ensure_history()
        profile = st.session_state.get("ss_ip_profile") or {}
        history.append({"role": "partner", "text": portfolio_narrative(profile)})
        st.session_state[_MESSAGES_KEY] = history
        st.session_state[EXPLAINED_KEY] = True
    if is_profile_complete():
        render_portfolio_builder()
    history = _ensure_history()

    left, center = st.columns([1, 2.4], gap="large")
    with left:
        st.markdown("**Suggested Questions**")
        for index, prompt in enumerate(SUGGESTED_QUESTIONS):
            if st.button(prompt, key=f"ss_ip_suggest_{index}", use_container_width=True):
                st.session_state[_PENDING_KEY] = prompt
                st.rerun()
    with center:
        st.markdown("**Conversation**")
        thread = "".join(_bubble_html(item.get("role", "partner"), str(item.get("text", ""))) for item in history)
        st.markdown(f'<div class="ip-thread">{thread}</div>', unsafe_allow_html=True)
        st.text_input(INPUT_PLACEHOLDER, key="ss_ip_draft", label_visibility="collapsed", placeholder=INPUT_PLACEHOLDER)
        if st.button("Send", type="primary", key="ss_ip_send"):
            st.session_state[_PENDING_KEY] = st.session_state.get("ss_ip_draft", "")
            st.session_state["ss_ip_draft"] = ""
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
