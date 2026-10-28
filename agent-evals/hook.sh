#!/usr/bin/env bash
# PostToolUse hook: when Claude edits the agent's prompt, skill loading or constants,
# re-run the agent evals once per case and compare with agent-evals/baseline.json.
# Exit 2 with the regressions on stderr so Claude sees them and fixes the change.
set -uo pipefail
cd "$(dirname "$0")/.."

file=$(python3 -I -c 'import json,sys; print(json.load(sys.stdin).get("tool_input",{}).get("file_path",""))')
[[ "$file" =~ agents/(shared/(prompt|skills)|constants)\.py$ ]] || exit 0

out=$(python3 agent-evals/run.py --runs 1 --concurrency 6 --tolerance 0.67 2>&1)
if [[ $? -ne 0 ]]; then
  echo "Agent evals regressed after editing $file:" >&2
  echo "$out" | grep -E 'REGRESSION|✗|CASE' >&2
  exit 2
fi
echo "Agent evals match the baseline." >&2
