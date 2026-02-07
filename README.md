# 📰 Substack Author Agent

An Agent that leverages MCP & SKILLs to help you with your Substack Content Strategy.

It also tracks its behavior with [Opik (by Comet)](https://www.comet.com/site/products/opik/) and is exposed as MCP Server for faster integration to the outside.

## Key Features

[PLACEHOLDER FOR STACK]
- Interactive CLI for Agent with SKILLs & MCP Tools
- Agent exposed as MCP Server to pack all functionality into a simple tool `run_agent`

## Setup

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure .env
cp .env.example .env
```

Edit `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-...
OTEL_EXPORTER_OTLP_ENDPOINT=https://www.comet.com/opik/api/v1/private/otel
OTEL_EXPORTER_OTLP_HEADERS=Authorization=<your-opik-api-key>,Comet-Workspace=default,projectName=substack-author-agent
```

## Usage

#### Talk to the Substack Author Agent directly

```bash
# Run the interactive CLI to talk to the agent
python agent.py
```

#### Expose Agent as MCP and use it as a wrapper

```bash
# Activate the MCP Server and connect it to Claude Code, Cursor using stdio transport and http://localhost:7777/mcp
python server.py
```

[PLACEHOLDER FOR DEMO]

### Resources
- [Agno - Agent with Skills](https://docs.agno.com/skills/overview)
- [Agno - Agent as MCP Server](https://docs.agno.com/agent-os/mcp/mcp#agentos-as-mcp-server)