"""
AG-UI server — exposes the Agno agent to the CopilotKit frontend (ui/).
Runs on http://localhost:8000, agent endpoint: POST /agui
"""

import importlib.util
import os
import sys

from dotenv import load_dotenv

load_dotenv()

_here = os.path.dirname(os.path.abspath(__file__))
_agents_dir = os.path.join(_here, "agents")

# Pre-cache the installed agno package before local folders can shadow it.
import agno as _agno_pkg  # noqa: F401, E402

from agno.os import AgentOS  # noqa: E402
from agno.os.interfaces.agui import AGUI  # noqa: E402

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


agno_mod = _load("_impl_agno", "agents/agno/agent.py")
agent = agno_mod._agent


# --- Native thinking bridge -------------------------------------------------
# Agno streams Claude extended-thinking deltas as RunContentEvent.reasoning_content,
# but the AG-UI translator only maps ReasoningContentDeltaEvent. Re-tag those
# chunks so thinking shows up as REASONING_* events in the CopilotKit UI.
from agno.os.interfaces.agui import router as _agui_router  # noqa: E402
from agno.os.interfaces.agui.utils import (  # noqa: E402
    async_stream_agno_response_as_agui_events as _translate,
)
from agno.run.agent import (  # noqa: E402
    ReasoningCompletedEvent,
    ReasoningContentDeltaEvent,
    RunContentEvent,
)


async def _retag_thinking(response_stream):
    thinking = False
    async for chunk in response_stream:
        if (
            isinstance(chunk, RunContentEvent)
            and chunk.reasoning_content
            and not chunk.content
        ):
            thinking = True
            yield ReasoningContentDeltaEvent(
                agent_id=chunk.agent_id,
                agent_name=chunk.agent_name,
                run_id=chunk.run_id,
                session_id=chunk.session_id,
                reasoning_content=chunk.reasoning_content,
            )
            continue
        if thinking:
            # Close the reasoning session so the UI collapses the thinking bubble
            thinking = False
            yield ReasoningCompletedEvent(
                agent_id=chunk.agent_id,
                agent_name=chunk.agent_name,
                run_id=chunk.run_id,
                session_id=chunk.session_id,
            )
        yield chunk


async def _translate_with_thinking(response_stream, *args, **kwargs):
    async for event in _translate(_retag_thinking(response_stream), *args, **kwargs):
        yield event


_agui_router.async_stream_agno_response_as_agui_events = _translate_with_thinking
# ---------------------------------------------------------------------------

agent_os = AgentOS(agents=[agent], interfaces=[AGUI(agent=agent)])
app = agent_os.get_app()


# --- Follow-up suggestions endpoint -----------------------------------------
# CopilotKit's built-in dynamic suggestions rely on the agent calling a frontend
# tool, but Agno's AG-UI router drops run_input.tools (see memory) — so the Agno
# agent can't generate them. Instead the frontend POSTs the conversation here and
# we generate one-click follow-ups with a single forced-tool Claude call.
from anthropic import Anthropic  # noqa: E402
from constants import CLAUDE_MODEL  # noqa: E402
from pydantic import BaseModel  # noqa: E402

_anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

_SUGGEST_TOOL = {
    "name": "suggest_followups",
    "description": "Return the most relevant one-click follow-up actions.",
    "input_schema": {
        "type": "object",
        "properties": {
            "suggestions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "2-3 short, actionable follow-up prompts (max ~8 words each).",
            }
        },
        "required": ["suggestions"],
    },
}


class _SuggestMessage(BaseModel):
    role: str
    content: str


class _SuggestRequest(BaseModel):
    messages: list[_SuggestMessage]


@app.post("/suggestions")
def suggestions(req: _SuggestRequest):
    transcript = "\n".join(f"{m.role}: {m.content}" for m in req.messages if m.content)
    if not transcript.strip():
        return {"suggestions": []}

    message = _anthropic.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=256,
        tool_choice={"type": "tool", "name": "suggest_followups"},
        tools=[_SUGGEST_TOOL],
        messages=[
            {
                "role": "user",
                "content": (
                    "You are a Substack content-strategy copilot. Based on the "
                    "conversation so far, propose the most relevant next actions "
                    "the user might take (drill into an article's performance, "
                    "compare notes vs articles, extract brand voice, generate "
                    "content ideas, review cover images). Keep each short and "
                    f"actionable.\n\nConversation:\n{transcript}"
                ),
            }
        ],
    )
    for block in message.content:
        if block.type == "tool_use":
            return {"suggestions": block.input.get("suggestions", [])[:3]}
    return {"suggestions": []}


# ---------------------------------------------------------------------------


if __name__ == "__main__":
    agent_os.serve(app="agui_server:app", host="0.0.0.0", port=8000)
