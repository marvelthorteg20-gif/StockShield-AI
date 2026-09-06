# Changelog

All notable changes to StockShield AI are documented in this file.

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
