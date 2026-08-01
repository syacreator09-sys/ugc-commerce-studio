#!/usr/bin/env bash
set -euo pipefail

python -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
[ -f .env ] || cp .env.example .env
make verify

echo "Bootstrap complete. Higgsfield remains disabled until authenticated."
