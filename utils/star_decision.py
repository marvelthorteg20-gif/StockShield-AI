"""Star-rated trade decision overlay. Does not replace generate_decision()."""

from __future__ import annotations

from typing import Any, Dict, Optional

STAR_MAP = {
    "Strong Buy": ("★★★★★", "STRONG BUY"),
    "Buy": ("★★★★", "BUY"),
    "Accumulate": ("★★★★", "BUY"),
    "Hold": ("★★★", "HOLD"),
    "Reduce": ("★★", "SELL"),
    "Sell": ("★★", "SELL"),
    "Strong Sell": ("★", "STRONG SELL"),
}


def rate_star_decision(decision: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Convert the existing decision-engine action into a 5-star rating."""
    action = (decision or {}).get("action", "Hold")
    stars, label = STAR_MAP.get(action, ("★★★", "HOLD"))
    reasons = list(decision.get("reasons") or [])
    why = reasons[:6] if reasons else ["Signals are mixed; wait for confirmation."]
    return {
        "stars": stars,
        "label": label,
        "display": f"{stars} {label}",
        "why": why,
        "source_action": action,
    }
