#!/usr/bin/env python3
"""Evals for the Substack Author Agent itself, run through the Claude Code CLI.

Every model call (the agent under test and the LLM grader) goes through `claude -p`,
so it uses your Claude Code subscription and needs no API key.

The agent under test is the Claude agent's recipe: SYSTEM_PROMPT from agents/shared/prompt.py,
the local get_skill_instructions tool and the live Substack Author MCP, with Claude Code's own
tools turned off.

    python3 agent-evals/run.py                       # all evals/<skill>/evals.json
    python3 agent-evals/run.py --only analyze-notes  # one skill, or one case id
    python3 agent-evals/run.py --code-only           # skip the LLM grader (no judge calls)
    python3 agent-evals/run.py --update-baseline     # accept the current scores
"""

import argparse
import json
import re
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVALS = Path(__file__).resolve().parent
BASELINE = EVALS / "baseline.json"
sys.path.insert(0, str(ROOT / "agents"))

from constants import MCP_URL  # noqa: E402
from shared.prompt import SYSTEM_PROMPT  # noqa: E402

AGENT_MODEL = "haiku"  # same family as CLAUDE_MODEL in agents/constants.py
GRADER_MODEL = "sonnet"  # a different model grades the agent, as the Anthropic docs recommend

GRADER_PROMPT = """Grade this answer based on the rubric.
<rubric>{rubric}</rubric>
<question>{question}</question>
<answer>{answer}</answer>
Think step by step inside <thinking> tags, then output 'correct' or 'incorrect' in <result> tags."""


def load_cases(only: str | None) -> list[dict]:
    cases = []
    for path in sorted(EVALS.glob("*/evals.json")):
        data = json.loads(path.read_text())
        for case in data["evals"]:
            case["skill"] = data["skill"]
            case["rubrics"] = [(EVALS / "rubrics" / f"{r}.md").read_text() for r in case.get("rubrics", [])]
            if only in (None, data["skill"], case["id"]):
                cases.append(case)
    return cases


def run_claude(args: list[str], prompt: str) -> list[dict]:
    proc = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose", *args],
        capture_output=True, text=True, cwd=tempfile.gettempdir(), timeout=600,
    )
    return [json.loads(line) for line in proc.stdout.splitlines() if line.startswith("{")]


def run_agent(prompt: str, mcp_config: Path) -> dict:
    events = run_claude([
        "--model", AGENT_MODEL,
        "--system-prompt", SYSTEM_PROMPT,
        "--mcp-config", str(mcp_config), "--strict-mcp-config",
        "--tools", "",
        "--allowedTools", "mcp__skills__*", "mcp__substack__*",
        "--setting-sources", "",
        "--no-session-persistence",
        "--max-turns", "30",
    ], prompt)
    tools = [
        (block["name"].split("__", 2)[-1], block["input"])
        for e in events if e.get("type") == "assistant"
        for block in e["message"]["content"] if block.get("type") == "tool_use"
    ]
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    return {"tools": tools, "answer": result.get("result") or "", "cost": result.get("total_cost_usd", 0.0)}


def code_checks(case: dict, run: dict) -> dict[str, bool]:
    spec, tools, answer = case.get("code", {}), run["tools"], run["answer"]
    names = [name for name, _ in tools]
    checks = {}
    if "first_tool" in spec:
        checks["first_tool"] = bool(names) and names[0] == spec["first_tool"]
    if "skill_arg" in spec:
        checks["skill_arg"] = any(
            n == "get_skill_instructions" and a.get("skill_name") == spec["skill_arg"] for n, a in tools
        )
    for tool, minimum in spec.get("tools_min", {}).items():
        checks[f"{tool}>={minimum}"] = names.count(tool) >= minimum
    for tool in spec.get("tools_absent", []):
        checks[f"no {tool}"] = tool not in names
    if spec.get("no_tools"):
        checks["no tool calls"] = not names
    if "order" in spec:
        idx = [names.index(t) if t in names else -1 for t in spec["order"]]
        checks["order " + ">".join(spec["order"])] = -1 not in idx and idx == sorted(idx)
    for pattern in spec.get("regex", []):
        checks[f"/{pattern}/"] = bool(re.search(pattern, answer, re.I | re.S))
    for pattern in spec.get("not_regex", []):
        checks[f"!/{pattern}/"] = not re.search(pattern, answer, re.I | re.S)
    return checks


def judge(case: dict, run: dict) -> tuple[bool, str]:
    rubric = "\n\n".join([case["rubric"], *case["rubrics"]]) if "rubric" in case else "\n\n".join(case["rubrics"])
    prompt = GRADER_PROMPT.format(rubric=rubric, question=case["prompt"], answer=run["answer"])
    events = run_claude(["--model", GRADER_MODEL, "--tools", "", "--setting-sources", "", "--no-session-persistence"], prompt)
    text = next((e.get("result", "") for e in reversed(events) if e.get("type") == "result"), "")
    return "<result>correct</result>" in text.lower().replace(" ", ""), text


def run_case(job: tuple[dict, int], mcp_config: Path, code_only: bool) -> dict:
    case, n = job
    run = run_agent(case["prompt"], mcp_config)
    checks = code_checks(case, run)
    if not code_only and ("rubric" in case or case["rubrics"]):
        checks["rubric"], run["judge"] = judge(case, run)
    return {"id": case["id"], "skill": case["skill"], "run": n, "checks": checks, "passed": all(checks.values()),
            "cost": run["cost"], "judge": run.get("judge", ""), "tools": [t for t, _ in run["tools"]], "answer": run["answer"]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="skill name or case id")
    ap.add_argument("--runs", type=int, default=1, help="runs per case")
    ap.add_argument("-j", "--concurrency", type=int, default=4)
    ap.add_argument("--code-only", action="store_true", help="skip the LLM grader")
    ap.add_argument("--tolerance", type=float, default=0.0, help="allowed drop from baseline before a case counts as a regression")
    ap.add_argument("--update-baseline", action="store_true")
    args = ap.parse_args()

    cases = load_cases(args.only)
    if not cases:
        print("No eval cases found", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        mcp_config = Path(tmp) / "mcp.json"
        mcp_config.write_text(json.dumps({"mcpServers": {
            "substack": {"type": "http", "url": MCP_URL},
            "skills": {"command": sys.executable, "args": [str(EVALS / "skills_server.py")]},
        }}))
        jobs = [(c, n) for c in cases for n in range(args.runs)]
        with ThreadPoolExecutor(args.concurrency) as pool:
            results = list(pool.map(lambda j: run_case(j, mcp_config, args.code_only), jobs))

    passes: dict[str, list[bool]] = {}
    for r in results:
        passes.setdefault(r["id"], []).append(r["passed"])
    scores = {k: sum(v) / len(v) for k, v in passes.items()}
    baseline = json.loads(BASELINE.read_text()) if BASELINE.exists() else {}

    out = EVALS / "results"
    out.mkdir(exist_ok=True)
    (out / "latest.json").write_text(json.dumps(results, indent=1))

    regressions = []
    print(f"{'CASE':34} {'SCORE':>5} {'BASE':>5}")
    for cid, score in scores.items():
        base = baseline.get(cid)
        flag = "  REGRESSION" if base is not None and base - score > args.tolerance else ""
        if flag:
            regressions.append(cid)
        print(f"{cid:34} {score:5.2f} {('-' if base is None else f'{base:5.2f}'):>5}{flag}")
    for r in results:
        failed = [name for name, ok in r["checks"].items() if not ok]
        if failed:
            print(f"  ✗ {r['id']} run {r['run']}: {', '.join(failed)}")
    print(f"\n{len(results)} runs, ${sum(r['cost'] for r in results):.2f} list price")

    if args.update_baseline:
        BASELINE.write_text(json.dumps({**baseline, **scores}, indent=1, sort_keys=True) + "\n")
        print(f"baseline updated: {BASELINE.relative_to(ROOT)}")
        return 0
    return 1 if regressions else 0


if __name__ == "__main__":
    sys.exit(main())
