from dotenv import load_dotenv
from agents import Agent, Runner, add_trace_processor, tracing as agents_tracing
from agents.mcp import MCPServerStreamableHttp
from opik.integrations.openai.agents import OpikTracingProcessor
from constants import MCP_URL, OPENAI_MODEL
from shared.prompt import SYSTEM_PROMPT

load_dotenv()


class _CleanOpikProcessor(OpikTracingProcessor):
    """Drops MCPListToolsSpan — tool-discovery noise that shows as 'Unknown' at 0s."""

    def _is_mcp_list(self, span) -> bool:
        return isinstance(span.span_data, agents_tracing.MCPListToolsSpanData)

    def on_span_start(self, span) -> None:
        if not self._is_mcp_list(span):
            super().on_span_start(span)

    def on_span_end(self, span) -> None:
        if not self._is_mcp_list(span):
            super().on_span_end(span)


add_trace_processor(_CleanOpikProcessor(project_name="substack-author-agent"))

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
