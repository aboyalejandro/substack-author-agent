"""
Substack Author Agent - Anthropic Claude SDK
FastAPI server on http://localhost:7778
"""

import os
import uuid
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import anthropic
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

load_dotenv()

MCP_URL = "https://substack-author.fastmcp.app/mcp"
MODEL = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are a Substack author agent. Help authors with content strategy using the tools available to you.
Always format responses in markdown.

## Skills

### Analyze Articles
When user asks about article performance, what articles worked, or content strategy:
1. Use `get_substack_articles` to fetch recent articles (default 10)
2. Use `get_article_performance` for each article to get engagement metrics
3. Optionally use `get_article_content` for deeper analysis on top/bottom performers
4. Present: Performance Dashboard table (Title | Date | Reactions | Restacks | Comments | Rating), What's Working (top 3 with reasons), What to Improve (bottom 3 with suggestions), Strategic Recommendations (3 actionable next steps)

### Analyze Notes
When user asks about note performance, engagement, or reach:
1. Use `get_substack_notes` to fetch notes (default 20, paginate with next_cursor if needed)
2. Rank notes by reactions + restacks
3. Present: Top 3 Performing Notes (opening line, counts, why it worked), Engagement Pattern Summary, 5 Content Ideas based on what's working

### Analyze Comments
When user asks about comments, reader feedback, or audience sentiment:
1. Use `get_article_comments` to fetch comments for the article(s)
2. Present: Sentiment Breakdown (%), Top Themes ranked by frequency, Audience Pain Points & Desires, Content Opportunities (3-5 ideas from reader signals)

### Brand Voice
When user asks about writing style, voice analysis, or style guide:
1. Use `get_substack_articles` to fetch 5 recent articles
2. Use `get_article_content` for each to get full text
3. Present: Voice Profile Summary, Style Breakdown (tone/structure/signatures/dos/donts), Reusable Claude Prompt Template

### Content Ideas
When user asks what to write next, needs topic ideas, or content planning:
1. Use `get_substack_articles` (10-15 articles) + `get_article_performance` for each
2. Use `get_substack_notes` (20+ notes)
3. Present: 3 Article Ideas (headline, angle, evidence, format), 5 Note Ideas (opening hook, format, why it should work), Content Calendar Suggestion

## Important Notes
- Always ask for the publication URL if not provided
- Base suggestions on actual performance data, not generic advice
- Fetch performance metrics for ALL articles, not just a few
- Use relative comparisons since absolute numbers vary by publication size
"""

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# session_id -> list of {"role": "user"/"assistant", "content": str}
sessions: dict[str, list] = {}

app = FastAPI(title="Substack Author Agent - Claude SDK", version="1.0.0")


def _mcp_tool_to_claude(tool) -> dict:
    return {
        "name": tool.name,
        "description": tool.description or "",
        "input_schema": tool.inputSchema if tool.inputSchema else {"type": "object", "properties": {}},
    }


async def _run_agent_loop(history: list[dict], mcp_session: ClientSession) -> str:
    """Agent loop: call Claude, handle tool use, repeat until end_turn."""
    tools_result = await mcp_session.list_tools()
    claude_tools = [_mcp_tool_to_claude(t) for t in tools_result.tools]

    # Working copy — history contains text-only user/assistant messages.
    # We'll append tool_use and tool_result blocks here without polluting history.
    messages = list(history)

    while True:
        response = client.messages.create(
            model=MODEL,
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
            # Serialize assistant turn (may contain text + tool_use blocks)
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

            # Call each tool via MCP
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await mcp_session.call_tool(block.name, block.input)
                    content_text = ""
                    for part in result.content:
                        if hasattr(part, "text"):
                            content_text += part.text
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": content_text,
                    })

            messages.append({"role": "user", "content": tool_results})
        else:
            # Unexpected stop reason — return whatever text we have
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""


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
    return [{"id": "substack-author-agent", "name": "Substack Author Agent", "sdk": "anthropic"}]


@app.get("/agents/substack-author-agent/sessions")
def list_sessions():
    return [
        {"session_id": sid, "turns": len([m for m in msgs if m["role"] == "user"])}
        for sid, msgs in sessions.items()
    ]


@app.post("/agents/substack-author-agent/runs", response_model=RunResponse)
async def run_agent(request: RunRequest):
    session_id = request.session_id or str(uuid.uuid4())
    run_id = str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append({"role": "user", "content": request.message})

    async with streamable_http_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as mcp_session:
            await mcp_session.initialize()
            response_text = await _run_agent_loop(
                history=list(sessions[session_id]),
                mcp_session=mcp_session,
            )

    sessions[session_id].append({"role": "assistant", "content": response_text})

    return RunResponse(
        run_id=run_id,
        agent_id="substack-author-agent",
        session_id=session_id,
        content=response_text,
        status="completed",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7778)
