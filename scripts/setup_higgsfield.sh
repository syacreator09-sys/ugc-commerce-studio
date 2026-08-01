#!/usr/bin/env bash
set -euo pipefail

if ! command -v higgsfield >/dev/null 2>&1; then
  curl -fsSL https://raw.githubusercontent.com/higgsfield-ai/cli/main/install.sh | sh
fi

if command -v npx >/dev/null 2>&1; then
  npx skills add higgsfield-ai/skills || true
fi

echo "Higgsfield CLI installed. Authenticate with: higgsfield auth login"
echo "Then verify: higgsfield account status --json"
