# Contributing to StockShield AI

Thanks for helping improve StockShield. This document is the shortest path to a clean pull request.

## Development setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the test suite (plain Python functions, no pytest required):

```bash
PYTHONPATH=. python3 -c "import importlib, pkgutil, tests
for _, name, _ in pkgutil.iter_modules(tests.__path__):
    if name.startswith('test_'):
        mod = importlib.import_module(f'tests.{name}')
        for attr in dir(mod):
            if attr.startswith('test_'):
                getattr(mod, attr)()
                print('PASS', name, attr)
print('ok')"
```

## Guidelines

1. Do not remove existing CLI sections or change analysis formulas unless a bug is proven.
2. New behavior belongs in a dedicated module under `utils/` or `analysis/` with tests in `tests/`.
3. Tune windows and folders in `config.py` instead of hard-coding magic numbers.
4. Yahoo data must go through `utils.market_data.get_ticker_bundle` so the cache stays coherent.
5. Keep functions typed and documented (PEP 257). Follow PEP 8 (79–100 character lines are fine).
6. Never commit `logs/`, `reports/`, or `__pycache__/`.

## Pull requests

- Open against `main`.
- Include tests for every new module.
- Update `CHANGELOG.md` with a user-facing note.
- Describe how you verified the CLI still prints the existing analysis blocks.
