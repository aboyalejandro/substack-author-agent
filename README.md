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

## Plugin evals (skills)

The six skills are also packaged as a Claude Code plugin (`.claude-plugin/plugin.json`, `skills/`, `.mcp.json`) so [`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals) can test them. It runs on your Claude Code subscription, no API key needed.

```bash
scripts/run-evals.sh                           # whole suite, 3 runs per case, with and without the plugin
scripts/run-evals.sh --case analyze-notes --runs 1 --ablation none   # one skill, fast
```

- `evals/<skill>/` holds one case per skill: `prompt.md` (how a user would ask), and `graders/` (`skill-fired`, `used-data`, and an LLM `rubric`). `evals/unrelated-request/` checks that no skill fires on an off-topic question.
- `evals/mocks/substack-author/` replaces the MCP server with fixtures, so runs are repeatable and never hit Substack. The `.replay/` folder keeps recorded answers of the agent mocks.
- The table prints `WITH`, `W/OUT` and `Δ`. A skill whose `Δ` drops to ~0 or whose `skill-fired` grader fails no longer triggers.
- `skills/` is a snapshot of the skills the MCP server serves. Refresh it with `python3 scripts/sync_skills.py` and review the diff.

### Live test with screenshots

```bash
scripts/live-eval.sh                                   # whole suite
scripts/live-eval.sh --case analyze-notes --runs 1 --ablation none   # one skill, fast
```

It runs the suite and saves `evals/results/live/summary.txt` (the table), `report.html` and a `report.png` screenshot of the report, taken with headless Chrome or Chromium (set `CHROME=/path/to/chrome` if it is not on your PATH). The folder is git-ignored.

### Run it while developing with Claude Code

`.claude/settings.json` registers a `PostToolUse` hook. When Claude edits `skills/<name>/SKILL.md`, `scripts/eval-hook.sh` runs that skill's case once. If a grader fails, the hook exits 2 and Claude sees the failing graders and fixes the skill. Needs Claude Code 2.1.269+ and git 2.31+.

Adding a skill means adding `evals/<skill-name>/` (same name as the skill), otherwise the hook asks for it.
