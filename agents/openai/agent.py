from dotenv import load_dotenv
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp
from constants import MCP_URL, OPENAI_MODEL
from shared.prompt import SYSTEM_PROMPT

load_dotenv()

mcp_server = MCPServerStreamableHttp(
    params={"url": MCP_URL},
    cache_tools_list=True,
    name="substack-author-mcp",
)

_agent = Agent(
    name="Substack Author Agent",
    instructions=SYSTEM_PROMPT,
    model=OPENAI_MODEL,
    mcp_servers=[mcp_server],
)

sessions: dict[str, list] = {}


async def run(message: str, session_id: str) -> str:
    history = sessions.get(session_id, [])
    agent_input = history + [{"role": "user", "content": message}] if history else message
    result = await Runner.run(_agent, input=agent_input)
    sessions[session_id] = result.to_input_list()
    return str(result.final_output)
