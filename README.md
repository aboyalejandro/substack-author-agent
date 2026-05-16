# Substack Author Agent

A Substack content strategy agent with **three parallel implementations** — [Agno](https://docs.agno.com/), [Anthropic Claude SDK](https://docs.anthropic.com/), and [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) — all exposed through a single FastAPI server.

Each implementation connects to the [Substack Author MCP](https://substack-author.fastmcp.app/mcp) server for live data and follows the same five content skills.

## Implementations

| ID | SDK | Model | Folder | Session storage |
|----|-----|-------|--------|----------------|
| `agno` | [Agno](https://docs.agno.com/) | Claude Haiku 4.5 | `agno/` | InMemoryDb (built-in) |
| `claude` | Anthropic SDK | Claude Haiku 4.5 | `claude/` | In-memory dict |
| `openai` | OpenAI Agents SDK | GPT-5 Mini | `openai/` | In-memory dict |

All three share the same system prompt (`shared/prompt.py`) and MCP tool set.

## Skills

The agent loads 5 skills from `skills/` (used natively by Agno; compiled into the system prompt for Claude and OpenAI):

| Skill | Trigger | MCP Tools Used |
|-------|---------|----------------|
| `analyze-notes` | "How are my notes doing?" | `get_substack_notes` |
| `analyze-articles` | "What articles worked?" | `get_substack_articles`, `get_article_performance`, `get_article_content` |
| `analyze-comments` | "What are readers saying?" | `get_article_comments` |
| `content-ideas` | "What should I write next?" | `get_substack_articles`, `get_article_performance`, `get_substack_notes` |
| `brand-voice` | "What's my writing style?" | `get_substack_articles`, `get_article_content` |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

cp .env.example .env
```

Edit `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Optional — Opik observability (agno only)
OTEL_EXPORTER_OTLP_ENDPOINT=https://www.comet.com/opik/api/v1/private/otel
OTEL_EXPORTER_OTLP_HEADERS=Authorization=<your-opik-api-key>,Comet-Workspace=default,projectName=substack-author-agent
```

## Usage

### API Server (all three implementations)

```bash
python server.py
```

Starts on `http://localhost:7777`. See [API.md](API.md) for full endpoint reference.

### Interactive CLI

```bash
python agent.py                  # defaults to agno
python agent.py --sdk claude
python agent.py --sdk openai
```

## Project Structure

```
substack-author-agent/
├── agno/
│   └── agent.py              # Agno SDK implementation
├── claude/
│   └── agent.py              # Anthropic SDK implementation
├── openai/
│   └── agent.py              # OpenAI Agents SDK implementation
├── shared/
│   └── prompt.py             # Shared system prompt + agno instructions
├── skills/
│   ├── analyze-notes/
│   ├── analyze-articles/
│   ├── analyze-comments/
│   ├── content-ideas/
│   └── brand-voice/
├── server.py                 # Unified FastAPI server :7777
├── agent.py                  # Interactive CLI (--sdk picker)
└── pyproject.toml
```

## Demo

### Agent CLI

| User Message | Agent Response |
|---|---|
| ![User message](demo/agno_user_message.png) | ![Agent response](demo/agno_agent_response.png) |

### Opik Observability

| Trace Overview | Tool Calls | Skill Usage |
|---|---|---|
| ![Trace](demo/opik_trace.png) | ![Tool call](demo/opik_tool_call.png) | ![Skill usage](demo/opik_skill_usage.png) |

## Resources

- [Agno - Agent with Skills](https://docs.agno.com/skills/overview)
- [Anthropic - Tool use](https://docs.anthropic.com/en/docs/build-with-claude/tool-use)
- [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [Substack Author MCP](https://github.com/aboyalejandro/substack-author-mcp)
- [Opik - Agno Integration](https://www.comet.com/docs/opik/integrations/agno)
