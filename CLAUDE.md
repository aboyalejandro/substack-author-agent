# Substack Author Agent — Claude Code Guide

## What this project is

Three implementations of the same Substack content strategy agent (agno / anthropic SDK / openai-agents SDK), unified behind a single FastAPI server. Originally built by Alejandro Aboy for [The Pipe and the Line](https://thepipeandtheline.substack.com) — replace the publication URL in examples with your own.

## Run the server

```bash
source .venv/bin/activate
python server.py          # starts on http://localhost:7777
```

## Run an agent via API

```bash
# Pick any agent_id: agno | claude | openai
curl -X POST http://localhost:7777/agents/agno/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "...", "session_id": "optional-session-id"}'
```

### All three agents

```bash
# Agno (Claude Haiku 4.5 via Agno framework + Skills)
curl -X POST http://localhost:7777/agents/agno/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze my latest articles from https://yourpublication.substack.com"}'

# Claude (Claude Haiku 4.5 via Anthropic SDK manual loop)
curl -X POST http://localhost:7777/agents/claude/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze my latest articles from https://yourpublication.substack.com"}'

# OpenAI (GPT-5 Mini via OpenAI Agents SDK)
curl -X POST http://localhost:7777/agents/openai/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze my latest articles from https://yourpublication.substack.com"}'
```

### Session continuity

```bash
curl -X POST http://localhost:7777/agents/claude/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "What were my top articles?", "session_id": "my-session"}'

curl -X POST http://localhost:7777/agents/claude/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate 3 ideas based on those.", "session_id": "my-session"}'
```

### Response shape

```json
{
  "run_id": "...",
  "agent_id": "claude",
  "session_id": "my-session",
  "content": "## Article Performance\n...",
  "status": "completed"
}
```

## Run the interactive CLI

```bash
python agent.py                  # defaults to agno SDK
python agent.py --sdk claude
python agent.py --sdk openai
```

## Agent IDs and SDKs

| agent_id | SDK | Model | Observability |
|---|---|---|---|
| `agno` | Agno framework | claude-haiku-4-5 | AgnoInstrumentor → OTLP → Opik |
| `claude` | Anthropic SDK (manual loop) | claude-haiku-4-5 | track_anthropic + @opik.track |
| `openai` | OpenAI Agents SDK | gpt-5-mini | _CleanOpikProcessor (filters MCPListToolsSpan) |

## Key files

| File | Purpose |
|---|---|
| `server.py` | Unified FastAPI wrapper — loads all 3 agents, pre-caches SDK packages |
| `agent.py` | CLI picker (`--sdk agno\|claude\|openai`) |
| `agents/constants.py` | MCP_URL + model names |
| `agents/shared/prompt.py` | SYSTEM_PROMPT (claude + openai) + AGNO_INSTRUCTIONS |
| `agents/agno/agent.py` | Agno implementation |
| `agents/claude/agent.py` | Anthropic SDK implementation |
| `agents/openai/agent.py` | OpenAI Agents SDK implementation |
| `skills/` | 5 SKILL.md files loaded natively by agno, compiled into prompt for others |

## Import trick (important)

`agents/`, `agno/`, `openai/` local folders would shadow installed packages of the same name. `server.py` and `agent.py` pre-cache the real installed packages in `sys.modules` before loading local files via `importlib`. Also adds `agents/` to `sys.path` so agent files can `from constants import ...` and `from shared.prompt import ...`.

## Environment

```
ANTHROPIC_API_KEY     — required for agno + claude
OPENAI_API_KEY        — required for openai
OTEL_EXPORTER_OTLP_*  — Opik OTLP for agno
OPIK_API_KEY          — Opik native client for claude + openai
OPIK_WORKSPACE        — Opik workspace (default: default)
```
