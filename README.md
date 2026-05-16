# Substack Author Agent

A Substack content strategy agent built **three ways** — using [Agno](https://docs.agno.com/), the [Anthropic SDK](https://docs.anthropic.com/), and the [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — all served from a single FastAPI endpoint and traced with [Opik](https://www.comet.com/docs/opik/).

Data comes from the [Substack Author MCP](https://substack-author.fastmcp.app/mcp) server. Logic comes from five content skills.

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

Five skills loaded from `skills/` — used natively by Agno, compiled into the system prompt for Claude and OpenAI:

| Skill | When it activates |
|-------|-------------------|
| `analyze-articles` | "How are my articles doing?" |
| `analyze-notes` | "How are my notes performing?" |
| `analyze-comments` | "What are readers saying?" |
| `content-ideas` | "What should I write next?" |
| `brand-voice` | "What's my writing style?" |

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
├── agno/agent.py
├── claude/agent.py
└── openai/agent.py
skills/                   # 5 SKILL.md files
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
