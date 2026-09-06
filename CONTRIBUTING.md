# Contributing to StockShield AI

Thanks for helping improve StockShield. This document is the shortest path to a clean pull request.

## Development setup

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:

```bat
py -3 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Tests and lint (same as GitHub Actions):

```bash
pytest
flake8
```

On headless Linux, set `MPLBACKEND=Agg` if you exercise the CLI chart helper.

## Guidelines

1. Do not remove existing CLI sections or change analysis formulas unless a bug is proven.
2. New behavior belongs in a dedicated module under `utils/` or `analysis/` with tests in `tests/`.
3. Tune windows and folders in `config.py` instead of hard-coding magic numbers.
4. Yahoo data must go through `utils.market_data.get_ticker_bundle` so the cache stays coherent.
5. Keep functions typed and documented (PEP 257). Follow PEP 8 (flake8 line length 120).
6. Never commit `logs/*.log`, generated `reports/`, or `__pycache__/`. Sample reports belong in `docs/sample-reports/`.

## Pull requests

- Open against `main`.
- Include tests for every new module.
- Update `CHANGELOG.md` and `RELEASE_NOTES.md` when the user-facing version changes.
- Describe how you verified the CLI still prints the existing analysis blocks.
