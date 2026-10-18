# Substack Author Agent

A Substack content strategy agent built **three ways** — using [Agno](https://docs.agno.com/), the [Anthropic SDK](https://docs.anthropic.com/), and the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — all served from a single FastAPI endpoint and traced with [Opik](https://www.comet.com/docs/opik/).

Data comes from the [Substack Author MCP](https://substack-author.fastmcp.app/mcp) server. Logic comes from the content skills the same server exposes as MCP resources.

## What's possible

| Capability | Details |
|---|---|
| **3 agent implementations** | Same behaviour, different SDKs — compare outputs and traces side by side |
| **Single API entry point** | `POST /agents/{agno\|claude\|openai}/runs` — pick the SDK per request |
| **Interactive CLI** | `python agent.py --sdk agno\|claude\|openai` |
| **Session continuity** | Pass `session_id` to maintain conversation history across calls |
| **Opik observability** | Every run traced — LLM calls, tool calls, token counts, costs |
| **Shared prompt + constants** | One source of truth for model names, MCP URL, and system prompt |

## Implementations

| ID | SDK | Model | Folder |
|----|-----|-------|--------|
| `agno` | [Agno](https://docs.agno.com/) | Claude Haiku 4.5 | `agents/agno/` |
| `claude` | [Anthropic SDK](https://docs.anthropic.com/) | Claude Haiku 4.5 | `agents/claude/` |
| `openai` | [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) | GPT-5 Mini | `agents/openai/` |

## Skills

Six skills fetched from the MCP server's resources (`skill://<name>/SKILL.md`) at startup — loaded natively by Agno via a custom `MCPSkills` loader, exposed as a `get_skill_instructions` tool for Claude and OpenAI:

| Skill | When it activates |
|-------|-------------------|
| `analyze-articles` | "How are my articles doing?" |
| `analyze-notes` | "How are my notes performing?" |
| `analyze-comments` | "What are readers saying?" |
| `content-ideas` | "What should I write next?" |
| `brand-voice` | "What's my writing style?" |
| `visual-brand` | "Generate a cover image prompt" |

## Observability

All three agents send traces to [Opik](https://www.comet.com/docs/opik/):

| Agent | Integration |
|-------|------------|
| `agno` | `AgnoInstrumentor` via OpenTelemetry / OTLP |
| `claude` | `track_anthropic()` wraps the client + `@opik.track` parent span per run |
| `openai` | Custom `_CleanOpikProcessor` (filters `MCPListToolsSpan` noise) |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
# fill in ANTHROPIC_API_KEY, OPENAI_API_KEY, and Opik keys
```

## Usage

### API server

```bash
python server.py   # http://localhost:7777
```

```bash
curl -X POST http://localhost:7777/agents/claude/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze my latest articles", "session_id": "my-session"}'
```

See [CLAUDE.md](CLAUDE.md) for the full endpoint reference and project internals.

### CLI

```bash
python agent.py                  # agno (default)
python agent.py --sdk claude
python agent.py --sdk openai
```

## Project structure

```
agents/
├── constants.py          # MCP_URL + model names
├── shared/prompt.py      # shared system prompt
├── shared/skills.py      # fetches skills from MCP resources
├── agno/agent.py
├── claude/agent.py
└── openai/agent.py
server.py                 # unified FastAPI :7777
agent.py                  # CLI picker
CLAUDE.md                 # Claude Code guide + run instructions
```

## Resources

- [Agno Docs](https://docs.agno.com/)
- [Anthropic Tool Use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Substack Author MCP](https://github.com/aboyalejandro/substack-author-mcp)
- [Opik Observability](https://www.comet.com/docs/opik/)

## Agent evals

`agent-evals/` tests the agent itself (system prompt, skill routing, tool use), following Anthropic's guide to [developing tests](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests). Every model call, the agent's and the grader's, goes through `claude -p`, so it runs on your Claude Code subscription and needs no API key.

```bash
python3 agent-evals/run.py                         # every case, 1 run each
python3 agent-evals/run.py --only analyze-notes --runs 3
python3 agent-evals/run.py --code-only             # skip the LLM grader
python3 agent-evals/run.py --runs 3 --update-baseline   # accept current scores
```

- `agent-evals/<skill>/evals.json` has one file per skill. Each case has a `prompt`, its `success_criteria`, `code` checks (first tool called, which skill was loaded, minimum calls per tool, call order, regexes on the answer) and an LLM `rubric`.
- `agent-evals/rubrics/*.md` are rubrics shared across cases and mirror rules in `agents/shared/prompt.py` (anchor every metric, ground answers in fetched data, don't ask for a URL you already have).
- The agent under test is the Claude agent's recipe: `SYSTEM_PROMPT`, the local `get_skill_instructions` tool (served by `agent-evals/skills_server.py`) and the live Substack Author MCP. Claude Code's own tools are off. The grader is Sonnet, a different model than the Haiku agent.
- `baseline.json` stores the pass rate per case. The run prints `REGRESSION` and exits 1 when a case drops below it. Some cases start below 1.00 because the agent really misses those rules today, so fixing them raises the baseline.

### Run it while developing with Claude Code

`.claude/settings.json` registers a `PostToolUse` hook. When Claude edits `agents/shared/prompt.py`, `agents/shared/skills.py` or `agents/constants.py`, `agent-evals/hook.sh` runs every case once and exits 2 with the regressions, so Claude sees what changed and fixes it. A full pass takes a few minutes. Needs `fastmcp` installed (already in `requirements.txt`).
