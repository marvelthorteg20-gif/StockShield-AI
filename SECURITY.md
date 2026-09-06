# Security Policy

## Supported versions

| Version | Supported |
| --- | --- |
| 1.0.x | Yes |

## Reporting a vulnerability

Please do **not** open a public issue for security problems.

Email the maintainers through GitHub (Security advisory on this repository) with:

- a description of the issue
- steps to reproduce
- the affected version / commit

We will acknowledge the report and ship a patch on the `1.0.x` line when needed.

## Data sources

StockShield AI reads public market data from Yahoo Finance and optional news from Alpha Vantage. No broker credentials are stored. Put API keys in environment variables (see `.env.example`); do not commit `.env` files.
