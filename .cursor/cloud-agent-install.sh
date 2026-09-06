#!/usr/bin/env bash
# Idempotent Cloud Agent bootstrap for StockShield AI.
set -euo pipefail

cd "$(dirname "$0")/.."

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
