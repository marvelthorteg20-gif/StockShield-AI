"""v2 UI architecture: presentation modules import cleanly and stay off the engine."""

from __future__ import annotations

import importlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = (
    "utils.pipeline",
    "utils.indicators",
    "utils.market_data",
    "utils.decision_engine",
    "yfinance",
    "import app",
    "import streamlit_app",
    "from app ",
    "from streamlit_app",
)

UI_MODULES = [
    "components",
    "components.header",
    "components.sidebar",
    "components.metrics",
    "components.charts",
    "components.tabs",
    "components.footer",
    "pages",
    "pages.overview",
    "pages.technical",
    "pages.fundamentals",
    "pages.news",
    "pages.reports",
    "pages.portfolio",
    "pages.watchlist",
]


def _iter_ui_sources() -> list[Path]:
    paths: list[Path] = []
    for folder in ("components", "pages"):
        paths.extend(sorted((ROOT / folder).glob("*.py")))
    return paths


def test_v2_ui_modules_import():
    for name in UI_MODULES:
        module = importlib.import_module(name)
        assert module is not None


def test_v2_ui_sources_do_not_touch_analysis_stack():
    for path in _iter_ui_sources():
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN:
            assert token not in text, f"{path.name} must not reference {token}"


def test_expected_v2_files_exist():
    for relative in (
        "components/header.py",
        "components/sidebar.py",
        "components/metrics.py",
        "components/charts.py",
        "components/tabs.py",
        "components/footer.py",
        "pages/overview.py",
        "pages/technical.py",
        "pages/fundamentals.py",
        "pages/news.py",
        "pages/reports.py",
        "pages/portfolio.py",
        "pages/watchlist.py",
    ):
        assert (ROOT / relative).is_file()


def test_header_declares_v2_badge():
    text = (ROOT / "components" / "header.py").read_text(encoding="utf-8")
    assert "v2 Development" in text
    assert "datetime" in text


def test_sidebar_declares_trading_terminal_sections():
    text = (ROOT / "components" / "sidebar.py").read_text(encoding="utf-8")
    for label in (
        "SEARCH",
        "WATCHLIST",
        "GLOBAL MARKETS",
        "MARKET OVERVIEW",
        "MARKET STATUS",
        "SETTINGS",
        "AAPL",
        "MSFT",
        "NVDA",
        "TSLA",
        "GOOGL",
    ):
        assert label in text


def test_kpi_items_use_existing_analysis_fields_only():
    from types import SimpleNamespace

    from components.metrics import KPI_LABELS, kpi_items_from_result

    result = SimpleNamespace(
        latest={"Close": 100.5},
        today_percent=1.25,
        score=72,
        recommendation="BUY",
        confidence="High",
        volatility_level="Medium",
    )
    items = kpi_items_from_result(result)
    labels = [item["label"] for item in items]
    assert labels == list(KPI_LABELS)
    values = {item["label"]: item["value"] for item in items}
    assert values["Current Price"] == "$100.50"
    assert values["AI Score"] == 72
    assert values["Recommendation"] == "BUY"
    assert values["Confidence"] == "High"
    assert values["Risk Level"] == "Medium"
