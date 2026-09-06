# StockShield AI

Professional equity analysis for operators who want a terminal, not a toy.

StockShield combines technicals, fundamentals, news, risk, and a decision engine into one Python package. Use the **CLI** for scripted runs or the **Streamlit dashboard** for an interactive dark workspace.

## Project Overview

StockShield AI scores a ticker from Yahoo Finance prices and Alpha Vantage news, then produces:

- Trend, oscillators, volatility, and volume
- A weighted AI score and a Strong Buy → Strong Sell decision
- Smart stops, swing targets, and 2% position sizing
- Multi-timeframe alignment, institutional structure flags, and confluence S/R
- PDF / CSV / JSON export plus a narrative summary

Nothing here is a broker, a signal subscription, or investment advice.

The CLI print layout, indicator formulas, and decision-engine rules are frozen. Phase 5 hardens packaging, logging, types, and load time without changing those outputs.

## Features

- SMA20, EMA20, RSI, MACD, Bollinger Bands, ATR, ADX, volume
- Candlestick patterns (Hammer, Doji, Engulfing, Morning/Evening Star)
- Fundamentals and news sentiment
- AI score, decision engine, star rating
- Smart risk, swing plan, position sizing
- Multi-timeframe analysis and institutional signals
- Pivot / Fibonacci / dynamic support & resistance
- CLI terminal and Streamlit dark dashboard
- Cached Yahoo requests (one bundle per symbol/TTL), JSONL + file logs, benchmark footer
- Graceful Yahoo `info` and news failures (history and CLI fallbacks unchanged)

## Architecture

```
app.py                 CLI (exact historical print layout)
dashboard.py           Fast-paint Streamlit terminal (lazy pipeline/Plotly)
streamlit_app.py       Alternate dashboard (same engines)
utils/pipeline.py      Shared analysis orchestration
utils/indicators.py    Technical snapshot
utils/market_data.py   Cached Yahoo bundle
utils/symbols.py       Ticker validation (no yfinance)
utils/app_log.py       File logger (API / unexpected errors)
analysis/              Score, patterns, risk math
config.py              ATR / RSI / MACD / risk / export / theme
```

```mermaid
flowchart TD
    CLI["app.py CLI"] --> PIPE["utils.pipeline.run_analysis"]
    UI["dashboard.py Streamlit"] --> VAL["utils.symbols.validate_symbol"]
    UI -->|"on Analyze"| PIPE
    PIPE --> IND["utils.indicators"]
    PIPE --> FUND["utils.fundamentals"]
    PIPE --> NEWS["utils.news"]
    PIPE --> DEC["utils.decision_engine"]
    PIPE --> MTF["utils.multi_timeframe"]
    PIPE --> INST["utils.institutional"]
    PIPE --> SR["utils.levels"]
    PIPE --> SW["utils.swing_trade"]
    PIPE --> POS["utils.position_sizing"]
    IND --> MD["utils.market_data cache"]
    FUND --> MD
    MD --> YF["Yahoo Finance"]
    NEWS --> AV["Alpha Vantage"]
    CLI --> EXP["utils.export_report"]
    CLI --> LOGS["logs/stockshield.jsonl"]
    CLI --> FILELOG["logs/stockshield.log"]
    UI --> LOGS
```

```mermaid
sequenceDiagram
    participant User
    participant UI as Streamlit
    participant Pipe as pipeline
    participant Cache as market_data
    participant YF as Yahoo
    participant AV as Alpha Vantage
    User->>UI: open dashboard
    Note over UI: First paint: no yfinance / Plotly / pipeline
    User->>UI: Analyze
    UI->>Pipe: run_analysis(symbol, capital, risk)
    Pipe->>Cache: get_ticker_bundle
    alt cache fresh
        Cache-->>Pipe: info + history
    else cache miss
        Cache->>YF: Ticker.info (optional)
        Cache->>YF: Ticker.history
        Cache-->>Pipe: bundle
    end
    Pipe->>AV: NEWS_SENTIMENT
    AV-->>Pipe: headlines or fallback strings
    Pipe-->>UI: AnalysisResult
```

Yahoo is called **once per symbol/period** inside the TTL (`CACHE_TTL_SECONDS`). Fundamentals reuse that bundle. News is a separate Alpha Vantage HTTP call.

## Screenshots

![CLI screenshot](docs/screenshots/cli.png)

![Dashboard screenshot](docs/screenshots/dashboard.png)

Walkthrough animation:

![Analyze flow](docs/screenshots/analyze-flow.gif)

Text capture of the CLI layout: [`docs/screenshots/cli-sample.txt`](docs/screenshots/cli-sample.txt)

## Installation

Python 3.10+ recommended.

```bash
git clone https://github.com/marvelthorteg20-gif/StockShield-AI.git
cd StockShield-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Fresh-clone check (same as CI):

```bash
pytest
flake8
```

## Usage

CLI:

```bash
python app.py
```

You will be prompted for a symbol and capital. Reports land in `reports/`. Tune windows in `config.py`. User-facing analysis still uses `print`; diagnostics go to `logs/`.

Dashboard:

```bash
streamlit run dashboard.py
```

(`streamlit_app.py` remains available.) Dark theme is set in `.streamlit/config.toml`.
Sidebar: symbol, capital, risk %, Analyze. Plotly and the analysis pipeline load only after Analyze.

Tests and lint (same as GitHub Actions):

```bash
pytest
flake8
```

## Future Roadmap

- Watchlist / multi-ticker batch from the dashboard
- Optional HTML report theme
- Swap-in news providers besides Alpha Vantage
- Paper-trading adapters (no live order routing in this repo)

## License

MIT. See [LICENSE](LICENSE).

Please read [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).
