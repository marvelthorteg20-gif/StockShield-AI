# StockShield AI 1.0 Release Notes

**Version:** 1.0.0  
**Date:** 2026-09-06

StockShield AI 1.0 is the first public release of the professional equity terminal. It packages the existing CLI, Streamlit dashboard, and analysis engines without adding indicators or changing calculations.

## Highlights

- **CLI terminal** (`python app.py`) with the historical print layout, PDF/CSV/JSON export, and a benchmark footer
- **Dark Streamlit dashboard** (`streamlit run dashboard.py`) over the same `run_analysis()` pipeline
- **Cached Yahoo Finance** fetches (one info+history bundle per symbol inside the TTL)
- **Graceful API failures** for news and Yahoo metadata; empty history still raises `No stock data found.`
- **Windows and Linux** path handling via `pathlib`, headless matplotlib (`MPLBACKEND=Agg`), and CI on both OSes
- **Fast startup**: Streamlit first paint skips yfinance/Plotly; the CLI loads mplfinance only when drawing a chart

## What 1.0 does not include

- No new trading indicators
- No new AI scoring or decision rules
- No live order routing or broker adapters
- This is not investment advice

## Install

Python 3.10+ (3.11 recommended).

Linux / macOS:

```bash
git clone https://github.com/marvelthorteg20-gif/StockShield-AI.git
cd StockShield-AI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows (cmd):

```bat
git clone https://github.com/marvelthorteg20-gif/StockShield-AI.git
cd StockShield-AI
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python app.py
streamlit run dashboard.py
pytest
flake8
```

## Upgrade notes

Operators coming from the Phase 4/5 development branches should keep `config.py` windows at their defaults to preserve indicator output. Set `ALPHA_VANTAGE_API_KEY` if you outgrow the bundled news key.

## Files added for 1.0

- `RELEASE_NOTES.md` (this file)
- `SECURITY.md`
- `docs/assets/logo.png`, `docs/assets/banner.png`
- `docs/screenshots/` stills and demo GIF
- `docs/sample-reports/` example JSON/CSV/PDF
- GitHub Actions matrix: Ubuntu + Windows

## License

MIT. See [LICENSE](LICENSE).
