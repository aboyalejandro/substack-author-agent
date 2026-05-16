import os
from dotenv import load_dotenv
import anthropic
import opik
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from opik.integrations.anthropic import track_anthropic
from constants import MCP_URL, CLAUDE_MODEL
from shared.prompt import SYSTEM_PROMPT
from shared.skills import CLAUDE_SKILL_TOOL, get_skill_instructions

load_dotenv()

_client = track_anthropic(
    anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY")),
    project_name="substack-author-agent",
)

sessions: dict[str, list] = {}

_LOCAL_TOOLS = {"get_skill_instructions"}


def _mcp_tool_to_claude(tool) -> dict:
    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": tool.inputSchema if tool.inputSchema else {"type": "object", "properties": {}},
    }


async def _run_agent_loop(history: list[dict], mcp_session: ClientSession) -> str:
    tools_result = await mcp_session.list_tools()
    # skill tool first so the agent sees it before MCP tools
    all_tools = [CLAUDE_SKILL_TOOL] + [_mcp_tool_to_claude(t) for t in tools_result.tools]
    messages = list(history)

    while True:
        response = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=all_tools,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            assistant_content = []
            for block in response.content:
                if block.type == "text":
                    assistant_content.append({"type": "text", "text": block.text})
                elif block.type == "tool_use":
                    assistant_content.append({
                        "type": "tool_use",
                        "id": block.id,
                        "name": block.name,
                        "input": block.input,
                    })
            messages.append({"role": "assistant", "content": assistant_content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    if block.name in _LOCAL_TOOLS:
                        result = _call_local_tool(block.name, block.input)
                    else:
                        result = await _call_mcp_tool(mcp_session, block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""


@opik.track(name="skill_call", type="tool")
def _call_local_tool(tool_name: str, tool_input: dict) -> str:
    opik.update_current_span(name=tool_name)
    if tool_name == "get_skill_instructions":
        return get_skill_instructions(tool_input.get("skill_name", ""))
    return ""


@opik.track(name="tool_call", type="tool")
async def _call_mcp_tool(mcp_session: ClientSession, tool_name: str, tool_input: dict) -> str:
    opik.update_current_span(name=tool_name)
    result = await mcp_session.call_tool(tool_name, tool_input)
    return "".join(part.text for part in result.content if hasattr(part, "text"))


@opik.track(name="claude-agent-run", project_name="substack-author-agent")
async def run(message: str, session_id: str) -> str:
    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append({"role": "user", "content": message})

    async with streamable_http_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()
            response_text = await _run_agent_loop(
                history=list(sessions[session_id]),
                mcp_session=mcp_session,
            )

    sessions[session_id].append({"role": "assistant", "content": response_text})
    return response_text
