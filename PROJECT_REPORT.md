# StockShield AI — Project Report (Phase 4)

Date: 2026-09-06

This report describes the Streamlit dashboard, architecture cleanup, CI, and dependency trim. No new trading indicators were added. Existing CLI section text and analysis formulas were not redesigned.

## Files created

| File | Purpose |
| --- | --- |
| `streamlit_app.py` | Dark, wide Streamlit dashboard |
| `utils/pipeline.py` | Shared `run_analysis()` used by CLI and UI |
| `utils/plotly_charts.py` | Candlestick + AI Score gauge (Plotly) |
| `.streamlit/config.toml` | Streamlit dark theme |
| `.github/workflows/ci.yml` | GitHub Actions: `flake8` then `pytest` |
| `pytest.ini` | pytest `pythonpath` and test discovery |
| `setup.cfg` | flake8 settings |
| `tests/test_pipeline.py` | Pipeline and chart-builder tests |
| `docs/screenshots/README.md` | Screenshot placeholder notes |
| `PROJECT_REPORT.md` | This document |

## Files modified

| File | Why |
| --- | --- |
| `app.py` | CLI now calls `run_analysis()` then prints the same sections |
| `README.md` | Overview, features, architecture, usage, roadmap, license |
| `CHANGELOG.md` | 0.5.0 notes |
| `requirements.txt` | Direct dependencies only (UTF-8) |
| `utils/export_report.py` | Timezone-aware UTC timestamps |
| `utils/indicators.py` | Unused import removed |
| `utils/institutional.py`, `utils/levels.py`, `utils/ai_summary.py` | flake8 line length / unused locals |
| `analysis/risk.py`, `analysis/trend.py` | Lint only; stop/target math unchanged |
| `indicators/sma.py`, `indicators/ema.py` | flake8 (blank lines / unused import) |

## Architecture improvements

- One orchestration path: `run_analysis(symbol, capital, risk_pct)` composes indicators, fundamentals, news, decision engine, timeframes, institutional signals, S/R, swing plan, sizing, and summary.
- The CLI is a printer over that result object. The dashboard is a viewer over the same object.
- Yahoo caching (`utils.market_data`) is unchanged: fundamentals still reuse the indicator fetch.
- Errors remain `StockShieldError` subclasses; both front-ends log via `utils.session_log`.
- `config.py` still owns ATR/RSI/MACD windows, default risk %, export folder, and theme.

## Performance improvements

- No second Yahoo round-trip for fundamentals (existing cache).
- Dashboard charts are Plotly figures built from the in-memory history frame (no extra market calls).
- `requirements.txt` no longer pins ~60 transitive wheels, which speeds clean CI installs.

## Dashboard (working)

`streamlit run streamlit_app.py` serves HTTP 200 on port 8501 in this environment.

Sidebar: symbol, capital, risk %, Analyze.

Main page: company info, candlestick, AI score gauge, decision card, technicals, fundamentals, news, smart risk, swing plan, position size, multi-timeframe, institutional signals, S/R, AI summary, JSON/CSV/PDF download buttons.

Theme: `.streamlit/config.toml` dark (`#0b1220` / `#22c55e`).

## Tests and CI

- Full suite: **42 passed** (`pytest`)
- Lint: **flake8 clean**
- Workflow: `.github/workflows/ci.yml` on `push`/`pull_request` to `main`

Existing tests were not rewritten except incidental flake8-safe formatting. New tests cover the pipeline and Plotly helpers.

## Remaining recommendations

- Capture real `docs/screenshots/cli.png` and `dashboard.png` from a human session.
- Add a Streamlit Cloud `secrets` path if the Alpha Vantage key should not live in `config.py`.
- Optional: disk cache for Yahoo if agents restart often.
- `test_chart.py` is a manual Matplotlib GUI script and is excluded from flake8 on purpose.

## Verification commands

```bash
pytest
flake8
python app.py
streamlit run streamlit_app.py
```
