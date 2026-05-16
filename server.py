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

# Pre-import openai-agents as 'agents' into sys.modules before loading local agents/ files.
# Without agents/__init__.py the namespace package yields to the real installed package,
# but caching it here guarantees agents/openai.py's `from agents import ...` resolves correctly.
import agents as _openai_agents_pkg  # noqa: F401 — side-effect: caches real package in sys.modules

_here = os.path.dirname(os.path.abspath(__file__))


def _load_agent(module_name: str, rel_path: str):
    path = os.path.join(_here, rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


agno_mod   = _load_agent("_impl_agno",   "agents/agno.py")
claude_mod = _load_agent("_impl_claude", "agents/claude.py")
openai_mod = _load_agent("_impl_openai", "agents/openai.py")

AGENTS = {
    "agno":   agno_mod,
    "claude": claude_mod,
    "openai": openai_mod,
}

AGENT_META = [
    {"id": "agno",   "name": "Substack Author Agent", "sdk": "agno"},
    {"id": "claude", "name": "Substack Author Agent", "sdk": "anthropic"},
    {"id": "openai", "name": "Substack Author Agent", "sdk": "openai"},
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
