# EDD Framework Learnings

> Running log of friction, surprises, and gotchas from executing DEMO.md (3 branches × multi-evaluator experiments). Reconciled and grouped by topic. **The "Port Plan" section at the bottom is the actionable handoff to the `eval-driven-development` repo.**

## Run summary

- **Date:** 2026-05-21
- **Agent repo:** `substack-author-agent`
- **EDD repo:** `/Users/alejandroaboygatto/Desktop/eval-driven-development`
- **Agent SDKs exercised:** `claude` (anthropic SDK via `track_anthropic`)
- **Branches shipped:** [PR #4](https://github.com/aboyalejandro/substack-author-agent/pull/4) (`temporal-scoping`), [PR #5](https://github.com/aboyalejandro/substack-author-agent/pull/5) (`cross-article-comparison`), [PR #6](https://github.com/aboyalejandro/substack-author-agent/pull/6) (`search-intent-specificity`)
- **Branch 3 result was catastrophic** (every evaluator avg 0.00–0.15) — surfaced that one of the test scenarios was out-of-tool-scope, not a prompt bug

---

# Findings by topic

## A. Install + runtime bootstrap

### L1 — EDD infra lives in a separate repo; agent repo only holds artifacts

The `edd:edd` skill and CLI binaries (`edd`, `edd-build`, `edd-run`, `edd-inspect`) live in `eval-driven-development/scripts/`. The agent repo only needs the artifacts: `.edd/session.json`, `scenarios.txt`, `regressions.txt`. **DEMO.md L264–269** referenced `_local/`, `scripts/simulation/`, `shared/opik_client.py` as if they were in the agent repo. They aren't — that table needs rewriting.

### L3 — Install path is fragile; PATH and pyenv leak through

Symptom chain on first try:
1. `which edd` → not found (CLI never installed)
2. `pip install -e .../scripts` → `/opt/homebrew/bin/python3` is broken (`platform.mac_ver()` returns empty)
3. `python3 -m pip` via Python.framework path on `$PATH` → file doesn't exist (stale symlink to a deleted Python 3.12)
4. `~/.pyenv/shims/python3.13` works (Python 3.13.7) — install succeeds there
5. CLI shims land in `~/.pyenv/versions/3.13.7/bin/` but `pyenv rehash` fails: `cannot overwrite existing file ~/.pyenv/shims/.pyenv-shim` (stale lock, 325B, not held open). Shims never get linked.
6. Workaround: `rm ~/.pyenv/shims/.pyenv-shim && pyenv rehash` (one-time, safe).

User-machine specifics aside, the EDD skill never tells the operator to `pip install -e .../scripts` before Phase A. Cryptic failures cascade until someone reads `pyproject.toml`.

### L10 — `edd-build` requires Python 3.14+ for `uuid.uuid7()` (or a code patch)

`scripts/shared/opik_client.py:255` calls `str(uuid.uuid7())`. `uuid.uuid7()` only exists in **Python 3.14 stdlib**. We ran 3.13.7. Patched: `from fastuuid import uuid7` (already a transitive dep). Also affects `scripts/simulation/run_experiment.py:178,190`. `pyproject.toml` declares `requires-python = ">=3.11"` — too loose.

### L4 — `edd check` already does the right preflight (we missed it)

Once `edd` is on PATH, `edd check` verifies env vars + Opik reachable + agent reachable in seconds. DEMO.md Phase A still describes a Python one-liner. The skill docs should point at `edd check` first, then fall back to `OpikClient` only if the CLI is broken.

---

## B. Schema, tags, and convention drift

### L8 — Skill docs vs. runtime drift on tag convention

Commit `faae8f7` (`docs: remove sim- prefix and run-id from all tag references`) changed `scripts/setup/cli.py` so traces are tagged `[branch, *session_tags()]` (was `[f"run-{run_id}", f"sim-{branch}", *session_tags()]`). But the commit only touched `scripts/`. These skill docs still document the old pattern:

- `skills/scope-agent/SKILL.md:61` — `"branch_tag": "sim-<git-branch>"`
- `skills/experiment/SKILL.md:51` — `--branch-tag sim-$(git rev-parse --abbrev-ref HEAD)`
- `skills/run/SKILL.md:22` — "prevents `sim-main` taint"
- `skills/CLAUDE.md:59,62` — tag pattern `sim-<topic>`

I followed stale docs → wrote `"branch_tag": "sim-temporal-scoping"`. Runtime took it literally (no stripping). Caught + fixed before Phase D, but it's a silent foot-gun.

### L2 — Phase A evaluator-existence check has no MCP-level escape hatch

DEMO.md Phase A asks to "Confirm evaluators exist in Opik (`edd check` or `get_evaluators`)". `edd check` needs the CLI on PATH (see L3). `OpikClient.get_evaluators()` needs the Python package installed. **The Opik MCP server exposes traces/projects/stats but no `list-evaluators` / `list-automation-rules` tool.** Without the CLI, you can't inspect online evaluator state from MCP alone. Either the Opik MCP needs that endpoint, or the skill needs to write evaluator state to `.edd/evaluators.json` after `scope-evals` so the router can read it without a live Opik call.

---

## C. Data extraction + enrichment

### L11 — `edd-build` extraction non-idempotent across runs

First `edd-build --dry-run` after enrichment: 15/15 extracted. Second invocation ~10s later (same traces, no re-enrich): 4/15 extracted. The `--from` window default of "now − 6h" slides forward between calls; dry-run printed `2026-05-21T02:34:01` while the real run printed `2026-05-21T02:36:00`. The earliest 11 traces fell out of the window. Branch 2 saw the same shape (13/15 — 2 traces dropped silently on real build). **Mitigation:** pass `--from "<explicit-anchor>"`. **Real fix:** `--from` default should be derived from session start or first-tagged-trace start, not wall-clock.

### L13 — `--from` anchor is also fragile *forward* — Branch 3 lost everything

Branch 3 attempt #1: I anchored `--from "2026-05-21T10:05:00Z"`. Actual trace `start_time` was `2026-05-21T10:01:32Z` (3 min earlier). Result: `0 traces match — no tags found on any trace in this window`. The CLI error message (`hint: cli.py run may not have tagged traces — check batch_update_traces`) actively misled — it pointed at the tagging code, when the bug was on the user side. **Port-back:** when `extra_filters` includes a tag and the `start_time` window returns 0 traces, the CLI should differentiate "tag exists but outside window" vs "tag doesn't exist at all".

### L14 — Enrich script tool-span filter (`type=="tool"`) misses OpenInference traces

`_local/enrich_traces_claude.py` filters tool spans with `s.get("type") == "tool"`. `references/trace-enrichment.md:118` explicitly warns this: *"Opik computes `span.type` from instrumentor signals; many instrumentors set `span.type = 'general'` while emitting `kind=TOOL` in attributes."* On Branch 3 (semantic search scenarios), **every single trace recorded 0 tool spans** with the naive filter. Branch 1+2 caught most because article-fetch tools are typed correctly, but the warning is real. **Port-back:** the canonical enrich skeleton in `references/trace-enrichment.md:55-58` should be updated to walk spans by attribute (`kind=TOOL`), not by `span.type`, and the doc anti-pattern should be promoted to a runnable example.

### L5 — `_default_extractor` doesn't say *why* it dropped a trace

When extraction shrinks (L11, Branch 2's 13/15), the CLI just prints `extracted N items, dropped M`. No per-trace reason. `_default_extractor` returns `None` when `metadata.user_message` or `metadata.assistant_response` is missing — but the CLI swallows that signal. Should emit `dropped trace=<id> reason=missing_user_message|missing_assistant_response|other` at WARN level.

---

## D. Opik backend, transactional behavior

### L9 — Opik backend split via `~/.opik.config` (agent vs edd disagreed)

`edd run` reported `no traces found` after 15 successful HTTP 200s from the agent. Agent emitted to `http://localhost:5173/` (self-hosted Opik); edd queried `https://www.comet.com/opik/api/...` (cloud). Two backends, no overlap.

Root cause: user-global `~/.opik.config` (Sept 2025) pinned `url_override = http://localhost:5173/api/`. Opik SDK reads this file by default. Agent picked it up; edd ignored it because edd's `.env` set `OPIK_URL` explicitly.

Per-process override (verified: env vars beat config file):
```
OPIK_URL_OVERRIDE=https://www.comet.com/opik/api/ \
OPIK_WORKSPACE=aboyalejandro \
python server.py
```

`edd check` should grow a step: emit one cheap test trace via the agent, then immediately query the configured Opik for that trace ID. If 0 hits within 5s → fail loudly: `URL mismatch — agent OPIK_URL=<X>, edd OPIK_URL=<Y>`. Today `edd check` verifies both URLs reachable in isolation but not that they're the *same* URL.

### L15 — Opik `PUT /experiments/items/bulk` is transient-500 prone; retry safe but expensive

Branch 3 first `edd-run` attempt: judges scored 13/13, then `client.create_experiment_items()` failed with `500 Server Error on PUT /v1/private/experiments/items/bulk` (Opik error id `d2dfaeb555ab0ff2`). The experiment row got created via `create_experiment` (the prior call) but had no item links. Retrying the full `edd-run` worked on attempt #2 — but the second run re-fired all 5 judges × 13 traces = 65 calls, doubling the cost for that branch.

**Port-back actions:**
- `edd-run` should split into two phases internally: `score-only` (fire judges) and `commit-items` (write to Opik). On a 5xx during commit, retry the commit alone — never re-score.
- If commit fails 3 times, leave the experiment row + score data and surface: `experiment <id> created, items not linked — rerun edd-run --resume-experiment <id>`.
- Worth a learning entry in `references/opik-endpoints.md`: which endpoints are idempotent, which are observed-flaky.

---

## E. Scenario design

### L19 — Per-SDK prompt divergence is a silent regression vector

**Symptom:** Codex P2 on PR #7 flagged that `agents/agno/agent.py:37` passes `AGNO_INSTRUCTIONS` (a one-sentence constant) to the Agno runtime, while `agents/claude/agent.py` and `agents/openai/agent.py` both use `SYSTEM_PROMPT` (derived from `_BASE`). All four prior PRs (#4 temporal-scoping, #5 cross-article-comparison, #6 search-intent-specificity, #7 multi-turn-coherence) added rules to `_BASE` only. So Claude + OpenAI got every fix; Agno got none. Switching the eval endpoint to `/agents/agno/runs` would have silently reintroduced every regression we just fixed.

**Why the framework didn't catch it:** EDD runs against a single `AGENT_ENDPOINT` per session — by design, since the integration contract is HTTP-level. There's no awareness that this endpoint is one of three SDK implementations sharing a project, prompt module, and tool surface.

**Implication for the EDD skill:**
- `edd:scope-agent` walks the agent source to extract promises (per [`scope-agent/SKILL.md`](../eval-driven-development/skills/scope-agent/SKILL.md)). It should also enumerate the **prompt-injection paths** — every place a system prompt or instruction string is fed into the runtime — and warn when those paths diverge. A pattern like *"agno reads AGNO_INSTRUCTIONS, claude reads SYSTEM_PROMPT, openai reads SYSTEM_PROMPT — these are different constants"* should land in `.edd/promises.md` as a structural warning.
- When the operator picks an `AGENT_ENDPOINT`, `edd check` could grep the repo for sibling endpoints and warn: *"3 endpoints found, only 1 selected — your fix may not propagate to the others. See agents/{agno,claude,openai}/agent.py for divergence."*
- Long-term: `regressions.txt` should be fired against every SDK in turn, not just the chosen one. The cost is 3× but catches exactly this class of bug.

### L20 — Self-referential baseline trap when writing prompt rules

**Symptom:** My initial fix on PR #7 said *"anchor the answer to the publication baseline computed over the same set the user is asking about"*. Codex P1 caught it immediately: when the user asks to compare a subset (or single item) against the publication average, computing the "baseline" over the same set is self-comparison, which always yields parity and systematically breaks Relative Grounding and Metric Accuracy. A correct rule has to specify a *distinct, broader* reference set than the subject of comparison.

**Why this matters for the EDD skill:** Codex is doing the work an evaluator-of-evaluators would do — sanity-checking the *judge prompt*, not just the agent prompt. The framework currently has `references/evaluator-selection.md` and `validate-evaluator` (from the evals-skills plugin), but neither catches a rule that scores trivially well (because every result is parity = "anchored", judge gives full credit). A judge that always scores 1.0 on a class of inputs is just as broken as one that always scores 0.0.

**Port-back action:** add a "sanity question" to `scope-evals` Step 4: *"For each judge prompt, name one query where this judge would trivially return parity / full credit / zero credit. If you can name one, harden the rubric to disambiguate."*

### L21 — Per-SDK enrichers should be shipped templates, not docstring comments

**Symptom:** When Branch 4 had to pivot to the OpenAI Agents SDK (Anthropic key capped per L17), I had to hand-write `_local/enrich_traces_openai.py` from scratch — adapting the OpenInference-style enricher in `references/trace-enrichment.md` for OpenAI's specific trace shape: `input.input = [{role, content}, {type: 'function_call', ...}]`, `output.output = [{content: [{text}]}]`, and the `created_from == 'openai-agents'` discriminator.

The reference doc has the right knowledge encoded as Python-comment hints:
```python
# OpenAI Agents SDK:
# user_message = (trace_input.get("input") or [{}])[0].get("content", "")
# assistant_response = extract_openai_response(trace.get("output") or {})
```

But the operator has to translate those hints into a runnable script that handles edge cases (content as string vs list, multi-turn history accumulation, function-call entries in the input array, tool argument extraction). That's 80 lines of code, ~30 min of reading the actual trace shape, and an opportunity to misread the contract.

**Port-back action:** ship `_local/enrich_traces_anthropic.py`, `_local/enrich_traces_openai_agents.py`, `_local/enrich_traces_agno.py` as starter templates under `references/enrichers/` (or `examples/enrichers/`). Operators copy + modify. Reduces enrichment-time bugs and shortens the time-to-first-trace.

### L22 — Multi-turn OpenAI Agents SDK accumulates history in `input.input`

**Symptom:** Each turn POST to `/agents/openai/runs` produces one Opik trace, but the trace's `input.input` field is a **list containing the full conversation up to that turn** (prior user messages, assistant responses, tool calls — all interleaved). Turn 2 of a 2-turn scenario shows BOTH turn-1's user message AND turn-2's, with function calls between them.

For enrichment this means **the trigger message is always the *last* `role=user` entry, not the first**. Getting this wrong:
- `users[0]` → enriches every turn-N trace with turn-1's user message → judges score the same scenario over and over.
- `users[-1]` → correct: each trace gets the message that actually triggered it.

This contrasts with the Anthropic SDK (`track_anthropic`), where each trace's `input` is just the current turn's message — no history accumulation in the trace itself.

**Implication:** `references/trace-enrichment.md` should make this explicit. The current SDK-pattern table covers shape but not multi-turn semantics — "OpenAI Agents SDK accumulates conversation history in input.input; use the last role=user entry per trace" is the missing line.

### L18 — `OpikClient.search_traces` returns inconsistent counts across calls

**Symptom:** Repeatedly calling `search_traces(project, from_time=<X>)` with the same arguments seconds apart returned wildly different results. One trace within minutes:
- `since=10min` → 3 traces
- `since=1h` → 0 traces
- `since=24h` → 500 traces
- `since=6h` → 46 traces
- `since=1h` (again) → 2 traces
- `since=30min` → 0 traces

Not a clock-skew issue — the windows overlap. Not pagination — `size=500` was the cap on all calls. The Opik backend returns different content for the same `GET /v1/private/traces?filters=...&size=500` request. Could be eventual-consistency, view-cache invalidation, or a rate-limit-tied empty body, but the helper doesn't see any signal — `data.get("content", [])` returns `[]` and the caller can't tell flake from genuinely empty.

**Impact in this run:** none — `edd run` and the enrichers worked because they call `search_traces` once at the right moment. But for any code that *retries* a search to confirm a result (which `edd-build` doesn't do, but operators do manually), the flake would mislead. Branch 3's "0 traces match" diagnostic on the wrong `--from` (L13) compounds with this — operators can't trust "0 traces" as ground truth.

**Port-back actions:**
- `OpikClient.search_traces` should retry on suspiciously-empty responses (200 OK + empty content within a window known to have traces) before returning to the caller.
- Or: log every call's `total` field (most paginated APIs return it) so operators can detect the inconsistency themselves.
- Or at minimum: log a WARN when `content=[]` returns within 10s of a previous call that returned non-empty against the same project.

### L17 — `edd run` doesn't surface upstream 4xx; bails opaquely on scenario 1

**Symptom:** Branch 4 (`multi-turn-coherence`) emit died on scenario 1 with `HTTPStatusError: Server error '500 Internal Server Error' for url 'http://localhost:7777/agents/claude/runs'`. The CLI exited, never tagged anything. Surface-level diagnosis would be "agent server is broken".

**Actual cause:** the *agent* hit Anthropic's monthly API usage cap. Anthropic SDK raised `anthropic.BadRequestError: 400 — You have reached your specified API usage limits. You will regain access on 2026-06-01 at 00:00 UTC.`. FastAPI didn't translate the 400 — it surfaced as an unhandled `ExceptionGroup` in the request task, which Starlette wrapped into a generic 500. So `edd` saw 500 from the agent endpoint while the real signal was a 400 from upstream.

**Two implications for the EDD skill:**
1. **`edd check` should emit one real trace, not just `httpx.get` the base URL.** The current preflight does `_httpx.get(base, timeout=5.0)` against the host root (which 404s on this agent — counted as "reachable"). A `POST` against `AGENT_ENDPOINT` with a one-token message would have surfaced the upstream 400 *before* the first scenario fired, saving 13 minutes of wakeup time. Even better: surface the upstream error body in the CLI output rather than masking it under `HTTPStatusError`.
2. **`edd run` on first-scenario failure should stop and dump the agent server log tail.** Today it tracebacks `HTTPStatusError` and exits — operator has to know to look at server stderr. A `--show-server-log <path>` flag, or auto-tail of `AGENT_LOG_PATH` env var when set, would close that loop.

**Branch 4 is parked** until the Anthropic key recovers (2026-06-01). The scenarios + session.json + plan are committed on this branch and ready to fire when budget returns.

### L7 — Simulations need a domain-agnostic blast-radius cap

First-pass scenarios in DEMO.md ("Show me my top articles", "Rank all my articles by engagement", "Compare articles against my average") were unbounded. Agent obediently called `get_article_performance` 20–50× per trace and stitched 50+ items. Capping to `top 5` / `last 10` brought it to ~27s/scenario and well inside the 300s adapter timeout.

The framework needs a *generic* "simulation hygiene" section. Domain-agnostic table:

| Anti-pattern (unbounded ask)                                          | Bounded shape                                                          |
| --------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Support agent: *"Show me all open tickets for this account."*         | *"Show me the 10 most recent open tickets for this account."*          |
| Shop assistant: *"List the products we sell in the kitchen category."* | *"List the top 5 best-selling kitchen products this month."*           |
| Analytics agent: *"Compare every campaign's CTR against the baseline."* | *"Compare the top 5 campaigns by spend against the baseline CTR."*     |
| Knowledge-base search: *"Find articles about onboarding."*            | *"Find the 5 most relevant articles about onboarding for new admins."* |
| CRM agent: *"Pull all deals in stage X."*                              | *"Pull the 10 most recent deals in stage X, ranked by close date."*    |

Rules of thumb:
1. **Cap every list-returning query.** Default cap = 5 or 10; broader coverage = more scenarios, not wider ones.
2. **Anchor every range with a count or window.** `top N`, `last N`, `most recent N`, or `last N days` — pick one.
3. **One unbounded plural per scenario is one too many.** "All", "every", "across the board" → rewrite during `edd:scope-agent`.
4. **Aggregations are bounded by definition; rankings are not.** `"average open rate across last 10"` is fine; `"rank articles by open rate"` needs an explicit `top N`.
5. **Search scenarios need a result-count cap too.** Default cap = 5.

### L16 — Scenarios must respect the agent's tool surface, or the experiment measures missing capability

Branch 3 scored 0.00–0.15 across every evaluator. Root cause was *not* a prompt gap. The agent has no cross-publication search tool — only `get_substack_articles` / `get_substack_notes` scoped to a single publication URL. The Branch 3 scenarios ("Find Substack articles about Python tutorials", "Search for posts about AI safety") asked for the impossible. The agent's best honest response was "I can't do that"; instead it asked for a URL and stalled.

This is a deeper failure mode than blast radius. The scenarios *can't* be answered by any reasonable prompt change — the tool simply isn't there. The experiment then "measures" missing capability and scores 0 across the board.

**Port-back action:** `edd:scope-agent` produces `.edd/promises.md` — a list of skills/tools the agent exposes. Scenarios should be cross-checked against that file. If a scenario references a tool the agent doesn't have, flag it before `edd run` ever fires. Phase B in `experiment/SKILL.md` already says "every promise represented" but doesn't say *conversely*: "every scenario must hit a promise". The reverse-direction check would have caught Branch 3 in 30 seconds.

---

## F. Agent-repo specific (port these to `substack-author-agent`, not EDD)

### L5 (agent-repo) — `server.py` is all-or-nothing across 3 SDKs

`python server.py` exits with `ImportError: cannot import name 'Agent' from 'agents'` if `openai-agents` isn't installed. The eval loop only ever hits one endpoint per session — but server.py refuses to boot until all 3 SDK packages are installable. Either lazy-load each SDK + warn-on-missing, or list all 3 in `requirements.txt`.

### L6 (agent-repo) — `openai-agents` pulls a starlette that breaks fastapi

`pip install openai-agents` v0.17.3 yanks `starlette 1.0.0`. `fastapi 0.117.1` requires `starlette<0.49`. Server boots with `TypeError: Router.__init__() got an unexpected keyword argument 'on_startup'`. Pinned `starlette<0.49` in this repo's PR #4.

### L12 — Auto-mode classifier blocks cross-repo edits inconsistently

When patching `eval-driven-development/scripts/` from inside the agent repo working-dir, three of four Edit calls succeeded but one was denied. The denied edit was an `import` line; the corresponding `replace_all` on the same file in the same turn went through. End state: file half-patched. Either `cd` into the EDD repo before editing it, or grant explicit `Edit` allow for `eval-driven-development/scripts/**` in settings.

---

# Port Plan — handoff to `eval-driven-development`

Concrete tasks, file paths in the EDD repo, prioritized.

## P0 — runtime fixes that block ≥3.13 users

| # | Change                                                                                                             | File(s)                                                                                                                | From learning |
| - | ------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- | ------------- |
| 1 | Swap `uuid.uuid7()` → `fastuuid.uuid7()` everywhere; drop `import uuid` where uuid7 is the only use                | `scripts/shared/opik_client.py:255,273` · `scripts/simulation/run_experiment.py:7,178,190` (already patched this branch — port commits) | L10           |
| 2 | Bump `requires-python` floor in `scripts/pyproject.toml` to whatever the lowest tested floor is (3.13 if fastuuid, 3.14 if stdlib uuid7) | `scripts/pyproject.toml`                                                                                               | L10           |
| 3 | `edd-run` post-score-commit retry: catch 5xx on `create_experiment_items`, retry the bulk call up to 3× with backoff, never re-score | `scripts/simulation/run_experiment.py:206`                                                                             | L15           |
| 4 | `edd-run --resume-experiment <id>` flag to write items to an existing experiment row when commit failed mid-flow   | `scripts/simulation/run_experiment.py` (new flag)                                                                      | L15           |

## P1 — preflight + observability

| # | Change                                                                                                                              | File(s)                                                                  | From learning |
| - | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | ------------- |
| 5 | `edd check` emits one cheap test trace via the agent + queries Opik for it; fail on URL/workspace mismatch                          | `scripts/setup/cli.py` (the `check` subcommand)                          | L9            |
| 6 | `edd check` asserts Python ≥ floor + warns if `~/.opik.config` is present + warns if env vars are overriding it                      | `scripts/setup/cli.py`                                                   | L3, L9        |
| 7 | `_default_extractor` returns a structured drop reason; `edd-build` logs `dropped trace=<id> reason=<…>` per drop                    | `scripts/simulation/build_dataset.py:22` (extractor) + the consumer loop | L5, L11       |
| 8 | `edd-build` differentiates "tag exists but outside `--from` window" from "tag doesn't exist" in the error message                   | `scripts/simulation/build_dataset.py`                                    | L13           |
| 9 | `edd-build` default `--from` anchors to `min(start_time WHERE tag=<branch_tag>)` instead of `now-6h`                                | `scripts/simulation/build_dataset.py`                                    | L11           |

## P2 — scope-agent + scenario hygiene

| #  | Change                                                                                                                                     | File(s)                                                                | From learning |
| -- | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------- | ------------- |
| 10 | New `references/scenario-design.md` section "Blast-radius hygiene" with the domain-agnostic anti-pattern table from L7                     | `references/scenario-design.md` (new section, ~40 lines)                | L7            |
| 11 | `edd:scope-agent` skill prompt explicitly tells the operator: every scenario must reference a tool/skill named in `.edd/promises.md`       | `skills/scope-agent/SKILL.md`                                          | L16           |
| 12 | `edd:scope-agent` skill emits a `scenarios-lint` step that warns on unbounded plurals ("all", "every", missing `top N` on rankings)        | `skills/scope-agent/SKILL.md` + optional helper in `scripts/setup/`     | L7            |
| 13 | `references/trace-enrichment.md` tool-span skeleton walks spans by `attributes.kind` (TOOL), not `span.type`. Update L55-58 of that doc.   | `references/trace-enrichment.md`                                       | L14           |

## P3 — docs + skill drift cleanup

| #  | Change                                                                                                                     | File(s)                                                                                                                 | From learning |
| -- | -------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ------------- |
| 14 | Scrub `sim-` prefix from skill docs (commit `faae8f7` missed these)                                                        | `skills/scope-agent/SKILL.md:61` · `skills/experiment/SKILL.md:51` · `skills/run/SKILL.md:22` · `skills/CLAUDE.md:59,62` | L8            |
| 15 | `PREREQUISITES.md` adds explicit "Step 0: `pip install -e scripts/` then `edd check`" before integration contract          | `PREREQUISITES.md`                                                                                                      | L1, L3        |
| 16 | `PREREQUISITES.md` documents `~/.opik.config` precedence: env vars win; how to inspect via `python -c …OpikConfig()…`     | `PREREQUISITES.md`                                                                                                      | L9            |
| 17 | `DEMO.md` template (the one in this repo) should be rewritten to not reference files that live in the EDD repo as if local | `DEMO.md` in agent repos using EDD                                                                                      | L1            |

## P4 — Opik MCP capability gap (optional, not framework-blocking)

| #  | Change                                                                                              | Where                              | From learning |
| -- | --------------------------------------------------------------------------------------------------- | ---------------------------------- | ------------- |
| 18 | Request `list-evaluators` / `list-automation-rules` tool in the Opik MCP server                     | Opik project (not EDD)             | L2            |
| 19 | Until 18 lands: `edd:scope-evals` writes `.edd/evaluators.json` after running, so router can read   | `skills/scope-evals/SKILL.md` + helper | L2            |

---

# Self-verify

- [x] Every learning L1–L16 has at least one row in the Port Plan tables
- [x] File paths in the Port Plan are real (verified against `eval-driven-development/scripts/`, `skills/`, `references/`)
- [x] Agent-repo concerns (L5-agent, L6-agent, L12) are quarantined in section F and not mixed into the EDD port plan
- [x] Priority columns reflect blocking impact: P0 stops new users, P1 prevents silent data loss, P2 improves scope quality, P3 is docs hygiene
