"""File-based application logger.

CLI user-facing ``print`` statements stay in ``app.py``. Use this logger for
API failures, unexpected exceptions, and diagnostic traces.
"""

from __future__ import annotations

import logging
import os
from typing import Optional

import config

_CONFIGURED = False
_LOGGER_NAME = "stockshield"


def configure_logging(log_dir: Optional[str] = None) -> logging.Logger:
    """Attach a file handler under ``logs/`` once per process."""
    global _CONFIGURED
    logger = logging.getLogger(_LOGGER_NAME)
    if _CONFIGURED:
        return logger

    folder = log_dir or config.LOG_FOLDER
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, config.LOG_FILE_NAME)
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    )
    logger.setLevel(logging.INFO)
    if not any(
        isinstance(existing, logging.FileHandler)
        and getattr(existing, "baseFilename", "") == os.path.abspath(path)
        for existing in logger.handlers
    ):
        logger.addHandler(handler)
    logger.propagate = False
    _CONFIGURED = True
    return logger


def get_logger(name: str = _LOGGER_NAME) -> logging.Logger:
    """Return a child logger under the StockShield hierarchy."""
    configure_logging()
    if name == _LOGGER_NAME:
        return logging.getLogger(_LOGGER_NAME)
    return logging.getLogger(f"{_LOGGER_NAME}.{name}")
