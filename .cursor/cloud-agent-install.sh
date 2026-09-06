#!/usr/bin/env bash
set -euo pipefail

export PATH="${HOME}/.local/bin:${PATH}"

python3 -m pip install --user --upgrade pip
python3 -m pip install --user -r requirements.txt
