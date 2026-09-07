"""AI stock recommendations: consume run_analysis output, rank by AI Score."""

from __future__ import annotations

from types import SimpleNamespace

from streamlit.testing.v1 import AppTest

from components.portfolio_builder import GENERATE_LABEL
from utils.stock_recommendations import (
    RECS_KEY,
    SECTOR_CANDIDATES,
    candidates_for_allocation,
    generate_recommendations,
    recommendations_narrative,
    row_from_result,
    sort_rows,
    why_from_result,
)


def _result(symbol: str, score: int, company: str | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        symbol=symbol,
        company_name=company or f"{symbol} Corp",
        latest={"Close": 123.45},
        score=score,
        recommendation="BUY",
        confidence="High",
        trend="BULLISH",
        sentiment="POSITIVE",
        rsi=58.0,
        explanation=f"• Existing engine likes {symbol}.",
        summary=f"{symbol} summary from the existing engine.",
    )


def test_sector_candidates_match_spec_examples():
    assert SECTOR_CANDIDATES["Technology"] == ("AAPL", "MSFT", "NVDA")
    assert SECTOR_CANDIDATES["Banking"] == ("JPM", "BAC", "WFC")
    assert SECTOR_CANDIDATES["Healthcare"] == ("JNJ", "PFE", "LLY")
    assert SECTOR_CANDIDATES["Cash"] == ()


def test_candidates_skip_cash_and_dedupe_tickers():
    pairs = candidates_for_allocation(
        (
            ("Technology", 40),
            ("AI & Semiconductor", 25),
            ("Cash", 10),
        )
    )
    tickers = [item[1] for item in pairs]
    assert "AAPL" in tickers
    assert tickers.count("NVDA") == 1


def test_generate_recommendations_sorts_by_existing_ai_score():
    calls: list[str] = []

    def fake_analyze(symbol: str, capital: float = 0, risk_pct: float = 0):
        calls.append(symbol)
        scores = {"NVDA": 91, "AAPL": 80, "MSFT": 70, "JPM": 60, "BAC": 50, "WFC": 40}
        return _result(symbol, scores.get(symbol, 10))

    rows = generate_recommendations(
        (("Technology", 25), ("Banking", 20), ("Cash", 10)),
        analyze=fake_analyze,
        capital=10_000,
        risk_pct=2.0,
    )
    assert calls == ["AAPL", "MSFT", "NVDA", "JPM", "BAC", "WFC"]
    assert [row["ticker"] for row in rows] == ["NVDA", "AAPL", "MSFT", "JPM", "BAC", "WFC"]
    assert rows[0]["score"] == 91
    assert rows[0]["company"] == "NVDA Corp"
    assert rows[0]["price"] == 123.45


def test_why_uses_existing_engine_fields_only():
    text = why_from_result(_result("AAPL", 80, "Apple"), "Technology")
    assert "AAPL" in text
    assert "80/100" in text
    assert "BUY" in text
    assert "Existing engine likes AAPL" in text
    assert "Technology" in text


def test_row_from_result_maps_display_fields():
    row = row_from_result(_result("MSFT", 77, "Microsoft"), "Technology")
    assert row["ticker"] == "MSFT"
    assert row["company"] == "Microsoft"
    assert row["recommendation"] == "BUY"
    assert row["confidence"] == "High"


def test_sort_rows_is_stable_on_score():
    rows = sort_rows(
        [
            {"ticker": "AAA", "score": 10},
            {"ticker": "BBB", "score": 50},
            {"ticker": "CCC", "score": 50},
        ]
    )
    assert rows[0]["ticker"] == "BBB"
    assert rows[1]["ticker"] == "CCC"


def test_narrative_explains_ranked_picks():
    rows = [
        row_from_result(_result("NVDA", 91), "Technology"),
        row_from_result(_result("AAPL", 80), "Technology"),
    ]
    text = recommendations_narrative(rows, limit=2)
    assert "AI Score" in text
    assert "NVDA" in text
    assert "AAPL" in text


def _partner_harness() -> None:
    import streamlit as st
    from types import SimpleNamespace

    from components.investor_partner import render_investor_partner
    from utils.stock_recommendations import ANALYZE_KEY as KEY

    def fake_analyze(symbol: str, capital: float = 0, risk_pct: float = 0):
        table = {
            "AAPL": 88,
            "MSFT": 76,
            "NVDA": 94,
            "JPM": 71,
            "BAC": 64,
            "WFC": 58,
            "JNJ": 69,
            "PFE": 55,
            "LLY": 82,
            "SPY": 73,
            "QQQ": 79,
            "VTI": 72,
            "GLD": 61,
            "AVGO": 85,
            "AMD": 77,
        }
        return SimpleNamespace(
            symbol=symbol,
            company_name=f"{symbol} Inc",
            latest={"Close": 123.45},
            score=table.get(symbol, 40),
            recommendation="BUY",
            confidence="High",
            trend="BULLISH",
            sentiment="POSITIVE",
            rsi=58.0,
            explanation=f"• Existing engine likes {symbol}.",
            summary=f"{symbol} summary from the existing engine.",
        )

    st.session_state[KEY] = fake_analyze
    render_investor_partner()


def _complete_default_wizard(at: AppTest) -> AppTest:
    at.run()
    for _ in range(5):
        at.button(key="ss_ip_wiz_next").click().run()
        assert not at.exception
    return at


def test_generate_stock_suggestions_apptest_ranks_and_explains():
    at = _complete_default_wizard(AppTest.from_function(_partner_harness, default_timeout=30))
    at.button(key="ss_ip_gen_stocks_btn").click().run()
    assert not at.exception
    rows = at.session_state[RECS_KEY]
    assert rows
    scores = [int(row["score"]) for row in rows]
    assert scores == sorted(scores, reverse=True)
    assert rows[0]["ticker"] == "NVDA"
    blob = " ".join(str(item.value) for item in at.markdown)
    assert "AI Stock Recommendations" in blob
    assert "NVDA" in blob
    assert "Current Price" in blob
    assert "AI Score" in blob
    assert "Recommendation" in blob
    assert "Confidence" in blob
    assert "$123.45" in blob
    assert GENERATE_LABEL in [btn.label for btn in at.button]
    history = at.session_state["ss_ip_messages"]
    partner = " ".join(item["text"] for item in history if item.get("role") == "partner")
    assert "NVDA" in partner
    assert "StockShield" in partner


def test_generate_without_analyzer_under_pytest_does_not_call_pipeline():
    def _bare_harness() -> None:
        from components.investor_partner import render_investor_partner

        render_investor_partner()

    at = AppTest.from_function(_bare_harness, default_timeout=30)
    at.run()
    for _ in range(5):
        at.button(key="ss_ip_wiz_next").click().run()
    at.button(key="ss_ip_gen_stocks_btn").click().run()
    assert not at.exception
    assert RECS_KEY not in at.session_state or not at.session_state[RECS_KEY]
    info_text = " ".join(str(item.value) for item in at.info)
    assert "No ranked snapshots yet" in info_text
