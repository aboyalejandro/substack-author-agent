import os
from dotenv import load_dotenv
import anthropic
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from constants import MCP_URL, CLAUDE_MODEL
from shared.prompt import SYSTEM_PROMPT

load_dotenv()

_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

sessions: dict[str, list] = {}


def _mcp_tool_to_claude(tool) -> dict:
    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": tool.inputSchema if tool.inputSchema else {"type": "object", "properties": {}},
    }


async def _run_agent_loop(history: list[dict], mcp_session: ClientSession) -> str:
    tools_result = await mcp_session.list_tools()
    claude_tools = [_mcp_tool_to_claude(t) for t in tools_result.tools]
    messages = list(history)

    while True:
        response = _client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=messages,
            tools=claude_tools,
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
                    result = await mcp_session.call_tool(block.name, block.input)
                    content_text = "".join(part.text for part in result.content if hasattr(part, "text"))
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": content_text,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""


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
