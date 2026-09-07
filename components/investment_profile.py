"""Multi-step AI investment profile wizard for Investor Partner."""

from __future__ import annotations

from typing import Any

import streamlit as st

PROFILE_KEY = "ss_ip_profile"
STEP_KEY = "ss_ip_profile_step"
JUST_COMPLETED_KEY = "ss_ip_profile_just_completed"
START_INVESTING_KEY = "ss_ip_start_investing"

GOALS: tuple[str, ...] = (
    "Wealth Creation",
    "Passive Income",
    "Retirement",
    "Short-Term Trading",
    "Child Education",
)
RISK_LEVELS: tuple[str, ...] = (
    "Conservative",
    "Moderate",
    "Aggressive",
)
HORIZONS: tuple[str, ...] = (
    "6 Months",
    "1 Year",
    "3 Years",
    "5+ Years",
)
EXPERIENCE_LEVELS: tuple[str, ...] = (
    "Beginner",
    "Intermediate",
    "Advanced",
)

PROFILE_READY_MESSAGE = (
    "Perfect.\n\n"
    "I've created your investment profile.\n\n"
    "From now on I'll personalize every recommendation according to your goals."
)

START_INVESTING_LABEL = "Start Investing"

_CSS = """
<style>
.ip-wiz {
  background: linear-gradient(180deg, #121a28 0%, #0c1118 100%);
  border: 1px solid #243044;
  border-radius: 14px;
  padding: 1rem 1.1rem 1.15rem 1.1rem;
  margin: 0 0 1rem 0;
}
.ip-wiz-kicker {
  color: #99f6e4; font-size: 0.78rem; letter-spacing: 0.12em;
  text-transform: uppercase; font-weight: 700; margin: 0 0 0.35rem 0;
}
.ip-wiz-step { color: #8b9bb4; font-size: 0.88rem; margin: 0 0 0.8rem 0; }
.ip-rupee { color: #f0b429; font-size: 1.6rem; font-weight: 700; margin-top: 0.55rem; }
.ip-profile-row { color: #e8eef7; margin: 0.25rem 0; font-size: 0.95rem; }
.ip-profile-label {
  color: #8b9bb4; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.08em;
}
</style>
"""


def empty_draft() -> dict[str, Any]:
    """Default draft answers stored in session_state while the wizard runs."""
    return {
        "budget": 10000.0,
        "goal": GOALS[0],
        "risk": RISK_LEVELS[1],
        "horizon": HORIZONS[2],
        "experience": EXPERIENCE_LEVELS[0],
    }


def format_profile(answers: dict[str, Any]) -> dict[str, str]:
    """Normalize wizard answers into the displayed Investment Profile card."""
    budget = float(answers.get("budget") or 0)
    return {
        "Budget": f"₹{budget:,.0f}",
        "Goal": str(answers.get("goal") or "—"),
        "Risk": str(answers.get("risk") or "—"),
        "Experience": str(answers.get("experience") or "—"),
        "Horizon": str(answers.get("horizon") or "—"),
    }


def is_profile_complete() -> bool:
    """True when a finished profile dict is stored in session_state."""
    profile = st.session_state.get(PROFILE_KEY)
    return isinstance(profile, dict) and all(
        key in profile for key in ("Budget", "Goal", "Risk", "Experience", "Horizon")
    )


def consume_profile_ready_event() -> bool:
    """Return True once after the wizard completes, then clear the flag."""
    return bool(st.session_state.pop(JUST_COMPLETED_KEY, False))


def _draft() -> dict[str, Any]:
    draft = st.session_state.get("ss_ip_profile_draft")
    if not isinstance(draft, dict):
        draft = empty_draft()
        st.session_state["ss_ip_profile_draft"] = draft
    return draft


def _finish_wizard(draft: dict[str, Any]) -> None:
    st.session_state[PROFILE_KEY] = format_profile(draft)
    st.session_state[JUST_COMPLETED_KEY] = True
    st.session_state[STEP_KEY] = 6


def render_investment_profile() -> dict[str, str] | None:
    """Render the onboarding wizard or the completed profile card."""
    st.markdown(_CSS, unsafe_allow_html=True)
    if is_profile_complete():
        return _render_completed_card()
    _render_wizard()
    return None


def _render_completed_card() -> dict[str, str]:
    profile = dict(st.session_state[PROFILE_KEY])
    st.markdown('<div class="ip-wiz">', unsafe_allow_html=True)
    st.markdown('<p class="ip-wiz-kicker">Investment Profile</p>', unsafe_allow_html=True)
    for label, value in profile.items():
        st.markdown(
            f'<div class="ip-profile-row"><span class="ip-profile-label">{label}</span>'
            f"<br>{value}</div>",
            unsafe_allow_html=True,
        )
    if st.button(START_INVESTING_LABEL, type="primary", key="ss_ip_start_investing_btn"):
        st.session_state[START_INVESTING_KEY] = True
    if st.session_state.get(START_INVESTING_KEY):
        st.caption("Use Search in the sidebar and click Analyze when you are ready.")
    st.markdown("</div>", unsafe_allow_html=True)
    return profile


def _render_wizard() -> None:
    draft = _draft()
    step = int(st.session_state.get(STEP_KEY) or 1)
    step = min(max(step, 1), 5)
    st.session_state[STEP_KEY] = step

    st.markdown('<div class="ip-wiz">', unsafe_allow_html=True)
    st.markdown('<p class="ip-wiz-kicker">Build your investment profile</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="ip-wiz-step">Step {step} of 5</p>', unsafe_allow_html=True)

    if step == 1:
        st.markdown("**Investment Budget**")
        rupee, field = st.columns([1, 8])
        with rupee:
            st.markdown('<p class="ip-rupee">₹</p>', unsafe_allow_html=True)
        with field:
            draft["budget"] = float(
                st.number_input(
                    "Investment Budget",
                    min_value=1000.0,
                    value=float(draft.get("budget") or 10000.0),
                    step=1000.0,
                    key="ss_ip_budget",
                )
            )
    elif step == 2:
        if "ss_ip_goal" not in st.session_state:
            st.session_state["ss_ip_goal"] = draft.get("goal") or GOALS[0]
        draft["goal"] = st.radio("Investment Goal", GOALS, key="ss_ip_goal")
    elif step == 3:
        if "ss_ip_risk" not in st.session_state:
            st.session_state["ss_ip_risk"] = draft.get("risk") or RISK_LEVELS[1]
        draft["risk"] = st.radio("Risk Tolerance", RISK_LEVELS, key="ss_ip_risk")
    elif step == 4:
        if "ss_ip_horizon" not in st.session_state:
            st.session_state["ss_ip_horizon"] = draft.get("horizon") or HORIZONS[2]
        draft["horizon"] = st.radio("Investment Horizon", HORIZONS, key="ss_ip_horizon")
    else:
        if "ss_ip_experience" not in st.session_state:
            st.session_state["ss_ip_experience"] = draft.get("experience") or EXPERIENCE_LEVELS[0]
        draft["experience"] = st.radio("Experience", EXPERIENCE_LEVELS, key="ss_ip_experience")

    st.session_state["ss_ip_profile_draft"] = draft
    back, nxt = st.columns(2)
    with back:
        if step > 1 and st.button("Back", key="ss_ip_wiz_back"):
            st.session_state[STEP_KEY] = step - 1
            st.rerun()
    with nxt:
        next_label = "Create Profile" if step == 5 else "Next"
        if st.button(next_label, type="primary", key="ss_ip_wiz_next"):
            if step == 5:
                _finish_wizard(draft)
            else:
                st.session_state[STEP_KEY] = step + 1
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
