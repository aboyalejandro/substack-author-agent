#!/usr/bin/env bash
# Live test: run the eval suite and save screenshots of the result.
# Writes evals/results/live/{report.html,summary.txt,report.png}. Extra flags go to claude plugin eval.
# Usage: scripts/live-eval.sh [--case analyze-notes --runs 1 --ablation none]
# Screenshots need Chrome or Chromium: set CHROME=/path/to/chrome if it is not on PATH.
set -euo pipefail
cd "$(dirname "$0")/.."

out=evals/results/live
mkdir -p "$out"

status=0
claude plugin eval . --trust-plugin --judge-model sonnet --concurrency 4 --no-publish \
  --report "$out/report.html" "$@" 2>&1 | tee "$out/summary.txt" || status=$?

chrome="${CHROME:-$(command -v google-chrome chromium chromium-browser 2>/dev/null | head -1 || true)}"
if [[ -z "$chrome" ]]; then
  chrome=$(ls /opt/pw-browsers/chromium-*/chrome-linux/chrome ~/Library/Caches/ms-playwright/chromium-*/chrome-mac/Chromium.app/Contents/MacOS/Chromium 2>/dev/null | head -1 || true)
fi
if [[ -z "$chrome" && -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]]; then
  chrome="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
fi
if [[ -z "$chrome" ]]; then
  echo "No Chrome or Chromium found: report saved at $out/report.html, set CHROME to get the PNG" >&2
  exit "$status"
fi

"$chrome" --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --window-size=1360,1500 --screenshot="$out/report.png" "file://$PWD/$out/report.html" >/dev/null 2>&1
echo "Screenshot: $out/report.png"
exit "$status"
