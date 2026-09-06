import json
import os
import tempfile

import config
from utils.benchmark import Benchmark
from utils.cli import RED, color_enabled, paint, spinner
from utils.session_log import log_event


def test_session_log_writes_ticker_and_exports():
    original = config.LOG_FOLDER
    with tempfile.TemporaryDirectory() as folder:
        config.LOG_FOLDER = folder
        try:
            path = log_event(
                "AAPL",
                analysis_time=1.25,
                errors=["boom"],
                exports={"json": "a.json"},
                event="analysis",
            )
            assert os.path.isfile(path)
            with open(path, encoding="utf-8") as handle:
                row = json.loads(handle.readline())
            assert row["ticker"] == "AAPL"
            assert row["analysis_time"] == 1.25
            assert row["errors"] == ["boom"]
            assert row["export_history"]["json"] == "a.json"
            assert "timestamp" in row
        finally:
            config.LOG_FOLDER = original


def test_benchmark_snapshot_keys():
    stats = Benchmark().snapshot()
    assert stats["runtime_s"] >= 0
    assert stats["memory_mb"] >= 0
    assert stats["api_s"] >= 0


def test_paint_classic_theme_is_plain():
    original = config.THEME
    config.THEME = "classic"
    try:
        assert paint("hello", RED) == "hello"
        assert color_enabled() is False
    finally:
        config.THEME = original


def test_spinner_is_noop_off_tty():
    with spinner("Loading"):
        pass
