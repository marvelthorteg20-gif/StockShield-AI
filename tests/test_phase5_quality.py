"""Isolation and graceful-API tests for Phase 5 production hardening."""

from __future__ import annotations

import subprocess
import sys
from unittest.mock import MagicMock, patch

from tests.history_factory import make_history
from utils.market_data import get_ticker_bundle, reset_cache, validate_symbol
from utils.symbols import validate_symbol as validate_from_symbols


def test_validate_symbol_reexport_matches_symbols_module():
    assert validate_symbol("msft") == validate_from_symbols("msft") == "MSFT"


def test_yahoo_info_failure_still_returns_history():
    reset_cache()
    history = make_history(30)

    class FakeTicker:
        """Yahoo ticker whose .info fails but history succeeds."""

        def __init__(self) -> None:
            self.history = MagicMock(return_value=history)

        @property
        def info(self) -> dict:
            raise RuntimeError("info down")

    with patch("utils.market_data.yf.Ticker", return_value=FakeTicker()):
        bundle = get_ticker_bundle("AAPL")
    assert bundle["info"] == {}
    assert not bundle["history"].empty


def test_dashboard_import_does_not_load_yfinance():
    code = (
        "import sys\n"
        "banned = {'yfinance', 'utils.pipeline', 'utils.plotly_charts'}\n"
        "import dashboard\n"
        "loaded = set(sys.modules) & banned\n"
        "assert not loaded, loaded\n"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        check=False,
        capture_output=True,
        text=True,
        cwd=".",
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
