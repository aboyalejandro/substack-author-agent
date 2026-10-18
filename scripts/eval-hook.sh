#!/usr/bin/env bash
# PostToolUse hook: when Claude edits skills/<name>/SKILL.md, run that skill's eval case once.
# Exit 2 with the failing graders on stderr so Claude sees the diff and fixes it.
set -uo pipefail
cd "$(dirname "$0")/.."

file=$(python3 -I -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))')
[[ "$file" =~ skills/([a-z-]+)/SKILL\.md$ ]] || exit 0
skill="${BASH_REMATCH[1]}"
[[ -d "evals/$skill" ]] || { echo "No eval case for skill '$skill': add evals/$skill/" >&2; exit 2; }

out=$(claude plugin eval . --trust-plugin --case "$skill" --runs 1 --ablation none \
  --judge-model sonnet --no-publish --max-cost-usd 1 2>&1)
status=$?
if [[ $status -ne 0 ]]; then
  echo "Eval '$skill' failed after editing $file:" >&2
  echo "$out" | grep -E '✗|CASE|^[a-z-]+ +[0-9]' >&2
  exit 2
fi
echo "Eval '$skill' passed." >&2
