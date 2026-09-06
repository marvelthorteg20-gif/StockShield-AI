"""Presentation helpers for the StockShield Streamlit dashboard.

No market math lives here — only colors, cards, CSS, and progress display.
"""

from __future__ import annotations

from typing import Optional

UP = "#26a69a"
DOWN = "#ef5350"
NEUTRAL = "#8b9bb4"
GOLD = "#f0b429"

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
  font-family: "IBM Plex Sans", "Segoe UI", sans-serif;
}
.block-container {
  padding-top: 0.75rem;
  padding-bottom: 2rem;
  max-width: 1440px;
  padding-left: 1.1rem;
  padding-right: 1.1rem;
}
section[data-testid="stSidebar"] {
  background: #0c1018;
  border-right: 1px solid #1e2a3a;
}
div[data-testid="stExpander"] {
  background: #121826;
  border: 1px solid #1e2a3a;
  border-radius: 10px;
  margin-bottom: 0.7rem;
}
div[data-testid="stExpander"] details {
  padding: 0.15rem 0.25rem;
}
.ss-tape {
  display: flex;
  flex-wrap: wrap;
  gap: 0.55rem;
  margin: 0.35rem 0 0.9rem 0;
}
.ss-card {
  flex: 1 1 140px;
  min-width: 120px;
  background: linear-gradient(180deg, #161d2b 0%, #10151f 100%);
  border: 1px solid #243044;
  border-radius: 10px;
  padding: 0.7rem 0.85rem;
}
.ss-card.up { border-top: 3px solid #26a69a; }
.ss-card.down { border-top: 3px solid #ef5350; }
.ss-card.neutral { border-top: 3px solid #3d4f66; }
.ss-label {
  color: #8b9bb4;
  font-size: 0.72rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  font-weight: 600;
}
.ss-value {
  color: #e8eef7;
  font-family: "IBM Plex Mono", ui-monospace, monospace;
  font-size: 1.22rem;
  font-weight: 600;
  margin-top: 0.2rem;
}
.ss-delta { font-size: 0.85rem; font-weight: 600; margin-top: 0.15rem; }
.ss-delta.up, .ss-value.up { color: #26a69a; }
.ss-delta.down, .ss-value.down { color: #ef5350; }
.ss-delta.neutral { color: #8b9bb4; }
.ss-kicker {
  color: #8b9bb4;
  font-size: 0.82rem;
  margin-bottom: 0.4rem;
}
@media (max-width: 768px) {
  .block-container { padding-left: 0.6rem; padding-right: 0.6rem; }
  .ss-card { flex: 1 1 100%; }
  div[data-testid="stHorizontalBlock"] {
    flex-direction: column !important;
    gap: 0.5rem !important;
  }
}
</style>
"""


def tone_from_signed(value: float) -> str:
    """Green for non-negative, red for negative."""
    return "up" if float(value) >= 0 else "down"


def tone_from_text(text: str) -> str:
    """Map existing labels to up/down/neutral without changing the labels."""
    blob = str(text or "").upper()
    if any(token in blob for token in ("STRONG SELL", "SELL", "BEARISH", "REDUCE", "BREAKDOWN", "GAP DOWN")):
        return "down"
    if any(token in blob for token in ("STRONG BUY", "BUY", "BULLISH", "ACCUMULATE", "BREAKOUT", "GAP UP")):
        return "up"
    return "neutral"


def metric_card(
    icon: str,
    label: str,
    value: str,
    delta: Optional[str] = None,
    tone: str = "neutral",
) -> str:
    """HTML metric tile used in the ticker tape and KPI strips."""
    delta_html = f'<div class="ss-delta {tone}">{delta}</div>' if delta else ""
    return (
        f'<div class="ss-card {tone}">'
        f'<div class="ss-label">{icon} {label}</div>'
        f'<div class="ss-value {tone}">{value}</div>'
        f"{delta_html}</div>"
    )


def tape(*cards: str) -> str:
    """Wrap metric cards in a wrapping flex row (stacks on mobile)."""
    return '<div class="ss-tape">' + "".join(cards) + "</div>"


def clamp_pct(value: float, high: float = 100.0) -> int:
    """Progress-bar percent from an existing 0–N reading."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0
    if number < 0:
        return 0
    if number > high:
        return 100
    return int(round(100.0 * number / high))
