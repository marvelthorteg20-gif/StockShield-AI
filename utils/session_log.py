"""JSON-lines session logging under ``logs/``."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import config
from utils.app_log import get_logger

logger = get_logger("session")


def _ensure_log_dir() -> str:
    """Create the log folder if needed and return its path."""
    folder = config.LOG_FOLDER
    os.makedirs(folder, exist_ok=True)
    return folder


def log_event(
    ticker: str,
    *,
    analysis_time: Optional[float] = None,
    errors: Optional[List[str]] = None,
    exports: Optional[Dict[str, str]] = None,
    event: str = "analysis",
    extra: Optional[Dict[str, Any]] = None,
) -> str:
    """Append one structured log row and return the log file path."""
    folder = _ensure_log_dir()
    path = os.path.join(folder, config.JSONL_LOG_NAME)
    record = {
        "ticker": ticker,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "analysis_time": analysis_time,
        "errors": errors or [],
        "export_history": exports or {},
        "event": event,
    }
    if extra:
        record.update(extra)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, default=str) + "\n")
    if errors:
        logger.warning("event=%s ticker=%s errors=%s", event, ticker, errors)
    else:
        logger.info("event=%s ticker=%s", event, ticker)
    return path
