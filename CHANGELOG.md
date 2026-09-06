# Changelog

All notable changes to StockShield AI are documented in this file.

## [1.0.0] - 2026-09-06

First public release. No new indicators or scoring rules.

### Added
- Project logo, banner, demo GIF, and sample JSON/CSV/PDF reports under `docs/`
- `RELEASE_NOTES.md`, `SECURITY.md`, `.env.example`
- GitHub Actions matrix: Ubuntu + Windows
- `config.VERSION = "1.0.0"`

### Changed
- CLI loads mplfinance only when drawing a chart
- Export helpers use `pathlib` (same files, Windows-safe paths)
- README is the GitHub landing page

### Removed
- Dead matplotlib GUI probe `test_chart.py`
- Internal phase reports from the repository root

## [0.6.0] - 2026-09-06

### Added
- `utils/symbols.py` so Streamlit first paint can validate tickers without yfinance.
- `utils/app_log.py` file logging for API and unexpected failures.
- Architecture diagrams, CLI/dashboard screenshots, and a GIF in the README.
- Graceful Yahoo `info` failures (empty metadata; history still required).

### Changed
- Named constants in `config.py` for SMA/EMA/BB/ADX windows (same numeric values).
- Lazy pipeline/Plotly imports in both Streamlit entry points.
- Types and docstrings across analysis and utility modules.
- Duplicate numeric helpers routed through `utils.common` where behavior matches.

### Fixed
- News and Yahoo metadata errors are logged instead of failing silently.

## [0.5.0] - 2026-09-06

### Added
- Dark Streamlit dashboard (`streamlit_app.py`) over the shared analysis pipeline.
- `utils/pipeline.py` so CLI and UI run the same engines.
- GitHub Actions CI (`pytest` + `flake8`).
- Plotly candlestick + AI score gauge helpers.

### Changed
- `requirements.txt` lists direct dependencies only.
- README documents CLI and dashboard usage.

## [0.4.0] - 2026-09-06

### Added
- Production configuration via `config.py` (ATR, RSI, MACD, risk %, export folder, theme).
- Yahoo Finance request cache to avoid duplicate `.info` / history calls.
- Structured JSONL logging under `logs/` (ticker, timestamp, runtime, errors, exports).
- Benchmark footer: runtime, peak memory, API response time.
- Robust errors for invalid tickers, empty data, network failures, and sparse fundamentals.
- CLI loading spinner and optional ANSI colors.
- Public-release docs: README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT.

### Changed
- `calculate_indicators` and `get_fundamentals` share one cached Yahoo bundle.
- News and Yahoo helpers record latency for the benchmark panel.

### Fixed
- Missing fundamental fields no longer crash the CLI.

## [0.3.0] - 2026-09-06

- Multi-timeframe analysis, institutional signals, S/R engine, star rating,
  swing plan, position sizing, AI summary, and PDF/CSV/JSON export.

## [0.2.0] - 2026-09-06

- ATR, ADX, candlestick patterns, smart risk, weighted AI score, decision engine.

## [0.1.0]

- Initial SMA/EMA, RSI, MACD, Bollinger, news, fundamentals, and chart CLI.
