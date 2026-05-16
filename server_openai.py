"""
Substack Author Agent - OpenAI Agents SDK
FastAPI server on http://localhost:7779
"""

import uuid
from contextlib import asynccontextmanager
from typing import Optional
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

load_dotenv()

MCP_URL = "https://substack-author.fastmcp.app/mcp"
MODEL = "gpt-4o-mini"

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

# MCP server instance — connected once at startup
mcp_server = MCPServerStreamableHttp(
    params={"url": MCP_URL},
    cache_tools_list=True,
    name="substack-author-mcp",
)

# Agent — defined once; MCP server is connected via lifespan
substack_agent = Agent(
    name="Substack Author Agent",
    instructions=SYSTEM_PROMPT,
    model=MODEL,
    mcp_servers=[mcp_server],
)

# session_id -> full conversation history as input list
sessions: dict[str, list] = {}


@asynccontextmanager
async def lifespan(_: FastAPI):
    await mcp_server.connect()
    yield
    await mcp_server.cleanup()


app = FastAPI(
    title="Substack Author Agent - OpenAI Agents SDK",
    version="1.0.0",
    lifespan=lifespan,
)


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
    return [{"id": "substack-author-agent", "name": "Substack Author Agent", "sdk": "openai"}]


@app.get("/agents/substack-author-agent/sessions")
def list_sessions():
    return [
        {"session_id": sid, "turns": sum(1 for m in history if m.get("role") == "user")}
        for sid, history in sessions.items()
    ]


@app.post("/agents/substack-author-agent/runs", response_model=RunResponse)
async def run_agent(request: RunRequest):
    session_id = request.session_id or str(uuid.uuid4())
    run_id = str(uuid.uuid4())

    history = sessions.get(session_id, [])

    if history:
        agent_input = history + [{"role": "user", "content": request.message}]
    else:
        agent_input = request.message

    result = await Runner.run(substack_agent, input=agent_input)

    sessions[session_id] = result.to_input_list()

    return RunResponse(
        run_id=run_id,
        agent_id="substack-author-agent",
        session_id=session_id,
        content=str(result.final_output),
        status="completed",
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7779)
