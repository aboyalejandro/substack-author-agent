"""
Substack Author Agent — unified server on http://localhost:7777
Three implementations: agno | claude | openai
"""

import importlib.util
import sys
import os
import uuid
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

_here = os.path.dirname(os.path.abspath(__file__))
_agents_dir = os.path.join(_here, "agents")

# Pre-cache installed SDK packages before local subfolders can shadow them.
# agents/ has no __init__.py so the installed openai-agents regular package wins;
# same for agno/ and openai/ subfolders inside agents/.
import agno as _agno_pkg          # noqa: F401
import agents as _openai_agents   # noqa: F401
import openai as _openai_pkg      # noqa: F401

# Add agents/ to sys.path so agent files can import constants and shared.prompt
if _agents_dir not in sys.path:
    sys.path.insert(1, _agents_dir)


def _load(module_name: str, rel_path: str):
    path = os.path.join(_here, rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


agno_mod   = _load("_impl_agno",   "agents/agno/agent.py")
claude_mod = _load("_impl_claude", "agents/claude/agent.py")
openai_mod = _load("_impl_openai", "agents/openai/agent.py")

AGENTS = {
    "agno":   agno_mod,
    "claude": claude_mod,
    "openai": openai_mod,
}

AGENT_META = [
    {"id": "agno",   "name": "Substack Author Agent", "sdk": "agno",          "model": "claude-haiku-4-5"},
    {"id": "claude", "name": "Substack Author Agent", "sdk": "anthropic",     "model": "claude-haiku-4-5"},
    {"id": "openai", "name": "Substack Author Agent", "sdk": "openai-agents", "model": "gpt-5-mini"},
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    await openai_mod.mcp_server.connect()
    yield
    await openai_mod.mcp_server.cleanup()


app = FastAPI(title="Substack Author Agent", version="1.0.0", lifespan=lifespan)


class RunRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class RunResponse(BaseModel):
    run_id: str
    agent_id: str
    session_id: str
    content: str
    status: str


@app.get("/agents")
def list_agents():
    return AGENT_META


@app.get("/agents/{agent_id}/sessions")
def list_sessions(agent_id: str):
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return [
        {"session_id": sid, "turns": len(v) if isinstance(v, list) else 0}
        for sid, v in AGENTS[agent_id].sessions.items()
    ]


@app.post("/agents/{agent_id}/runs", response_model=RunResponse)
async def run_agent(agent_id: str, request: RunRequest):
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")

    session_id = request.session_id or str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    content = await AGENTS[agent_id].run(request.message, session_id)

    return RunResponse(
        run_id=run_id,
        agent_id=agent_id,
        session_id=session_id,
        content=content,
        status="completed",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7777)
