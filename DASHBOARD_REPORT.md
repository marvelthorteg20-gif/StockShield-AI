# Dashboard Report

Date: 2026-09-06

## What was built

`dashboard.py` is a Streamlit front end for StockShield AI. It does not calculate indicators, scores, or risk itself. It calls `utils.pipeline.run_analysis()`, which is the same orchestration path `app.py` uses.

Launch:

```bash
streamlit run dashboard.py
python app.py   # CLI unchanged
```

## UI

Dark theme (`.streamlit/config.toml`).

**Sidebar:** Stock Symbol, Capital, Risk %, Analyze.

**Main page:** Company Information, Candlestick Chart, AI Score, Decision Engine, Technical Indicators, Fundamentals, News, Smart Risk Management, Position Size, Swing Plan, AI Summary.

No extra analysis products were added in this file (no new indicators, no new scoring).

## Reuse

| Dashboard section | Source |
| --- | --- |
| Company / technicals / ATR / ADX / patterns | `calculate_indicators` via pipeline |
| AI Score / rating / confidence | `refine_ai_score` / `compute_ai_score` |
| Decision Engine | `generate_decision` |
| Fundamentals | `get_fundamentals` |
| News | `get_news_sentiment` |
| Smart risk | `calculate_smart_levels` |
| Swing plan | `build_swing_plan` |
| Position size | `calculate_position` |
| AI Summary | `generate_ai_summary` |
| Candlestick / gauge | existing `utils.plotly_charts` |

## Error handling

Sidebar values go through `validate_dashboard_inputs` (ticker format, capital > 0, risk in (0, 100]). Analysis failures are mapped to Streamlit errors:

- `InvalidTickerError`
- `EmptyDataError`
- `NetworkError`
- other `StockShieldError`
- unexpected exceptions (generic message + `logs/`)

Incomplete OHLC frames show a chart error instead of crashing. The last successful result is kept in `st.session_state` so widget reruns do not wipe the page.

## `app.py`

Not modified in this change. CLI still prints the existing analysis blocks.

## Tests

```bash
pytest
flake8
```

**46 passed.** Four new tests cover dashboard input validation. Existing analyzer, decision-engine, pipeline, and production tests still pass.

## Files

| File | Action |
| --- | --- |
| `dashboard.py` | created |
| `tests/test_dashboard.py` | created |
| `DASHBOARD_REPORT.md` | created |
| `README.md` | usage line for `dashboard.py` |
| `setup.cfg` | flake8 ignore for `dashboard.py` long lines |

Calculation modules were not edited.
