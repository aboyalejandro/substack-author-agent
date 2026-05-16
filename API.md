# API Reference

The agent runs as a unified REST API on `http://localhost:7777` with three implementations selectable via `agent_id`.

## Start the server

```bash
python server.py
```

## Agents

| `agent_id` | SDK | Model |
|---|---|---|
| `agno` | Agno framework | Claude Haiku 4.5 |
| `claude` | Anthropic SDK (manual loop) | Claude Haiku 4.5 |
| `openai` | OpenAI Agents SDK | GPT-5 Mini |

---

## Endpoints

### List agents

```bash
curl http://localhost:7777/agents
```

```json
[
  {"id": "agno",   "name": "Substack Author Agent", "sdk": "agno",         "model": "claude-haiku-4-5"},
  {"id": "claude", "name": "Substack Author Agent", "sdk": "anthropic",    "model": "claude-haiku-4-5"},
  {"id": "openai", "name": "Substack Author Agent", "sdk": "openai-agents","model": "gpt-5-mini"}
]
```

---

### Run an agent

```bash
curl -X POST http://localhost:7777/agents/{agent_id}/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "How are my latest articles doing?"}'
```

**Examples:**

```bash
# Agno
curl -X POST http://localhost:7777/agents/agno/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze my latest articles"}'

# Claude SDK
curl -X POST http://localhost:7777/agents/claude/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze my latest articles"}'

# OpenAI Agents SDK
curl -X POST http://localhost:7777/agents/openai/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "Analyze my latest articles"}'
```

**Response:**

```json
{
  "run_id": "3f2a1b...",
  "agent_id": "claude",
  "session_id": "auto-generated-uuid",
  "content": "## Article Performance\n...",
  "status": "completed"
}
```

---

### Maintain session context

Pass a consistent `session_id` to keep conversation history across requests:

```bash
curl -X POST http://localhost:7777/agents/claude/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "What were my top articles last month?", "session_id": "my-session-123"}'

curl -X POST http://localhost:7777/agents/claude/runs \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate 3 content ideas based on those.", "session_id": "my-session-123"}'
```

**Session storage per agent:**

| Agent | How history is stored |
|---|---|
| `agno` | InMemoryDb (managed by Agno internally) |
| `claude` | In-memory dict — text-only user/assistant pairs |
| `openai` | In-memory dict — full input list (`result.to_input_list()`) |

---

### List sessions

```bash
curl http://localhost:7777/agents/claude/sessions
```

```json
[
  {"session_id": "my-session-123", "turns": 2}
]
```

---

## Request body

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | string | ✅ | User message |
| `session_id` | string | ❌ | Pass same value across requests to maintain context. Auto-generated if omitted. |
