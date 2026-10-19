#!/usr/bin/env bash
# Full plugin eval suite on your Claude Code subscription (no API key).
# Usage: scripts/run-evals.sh [extra claude plugin eval flags, e.g. --case analyze-notes]
set -euo pipefail
cd "$(dirname "$0")/.."

exec claude plugin eval . \
  --trust-plugin \
  --threshold 0.8 \
  --judge-model sonnet \
  --concurrency 4 \
  --no-publish \
  "$@"
