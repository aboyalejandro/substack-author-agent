# API Reference

The agent runs as a REST API via [AgentOS](https://docs.agno.com/agent-os/introduction) on `http://localhost:7777`.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your keys
```

## Start the server

```bash
python server.py
```

## Endpoints

### List agents

```bash
curl http://localhost:7777/agents
```

### Run the agent

```bash
curl -X POST http://localhost:7777/agents/substack-author-agent/runs \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Analyze my latest articles"
```

### Run with streaming

```bash
curl -X POST http://localhost:7777/agents/substack-author-agent/runs \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Analyze my latest articles" \
  -d "stream=true"
```

### Maintain session context

Pass a consistent `session_id` to keep conversation history across requests:

```bash
curl -X POST http://localhost:7777/agents/substack-author-agent/runs \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=What were my top articles last month?" \
  -d "session_id=my-session-123"

curl -X POST http://localhost:7777/agents/substack-author-agent/runs \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Now generate 3 content ideas based on those." \
  -d "session_id=my-session-123"
```

### List sessions

```bash
curl http://localhost:7777/agents/substack-author-agent/sessions
```

## Response format

```json
{
  "run_id": "...",
  "agent_id": "substack-author-agent",
  "session_id": "...",
  "content": "Agent response here...",
  "status": "COMPLETED",
  "metrics": {
    "input_tokens": 2787,
    "output_tokens": 443,
    "total_tokens": 3230
  }
}
```

## Authentication

Disabled by default. To enable, set `OS_SECURITY_KEY` in `.env` and pass it as a Bearer token:

```bash
curl -X POST http://localhost:7777/agents/substack-author-agent/runs \
  -H "Authorization: Bearer <your-key>" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Analyze my latest articles"
```
