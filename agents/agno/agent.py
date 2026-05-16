import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.mcp import MCPTools
from agno.skills import Skills, LocalSkills
from agno.db.in_memory import InMemoryDb
from constants import MCP_URL, AGNO_MODEL
from shared.prompt import AGNO_INSTRUCTIONS

load_dotenv()

_mcp = MCPTools(transport="streamable-http", url=MCP_URL)
_db = InMemoryDb()

_agent = Agent(
    name="Substack Author Agent",
    id="substack-author-agent-agno",
    model=Claude(id=AGNO_MODEL, api_key=os.getenv("ANTHROPIC_API_KEY")),
    tools=[_mcp],
    db=_db,
    num_history_runs=10,
    add_history_to_context=True,
    read_chat_history=True,
    read_tool_call_history=True,
    skills=Skills(loaders=[LocalSkills("./skills")]),
    instructions=AGNO_INSTRUCTIONS,
    markdown=True,
)

sessions: dict = {}


async def run(message: str, session_id: str) -> str:
    response = await _agent.arun(message, session_id=session_id)
    return response.content or ""
