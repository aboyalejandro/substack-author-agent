import os
from dotenv import load_dotenv
import asyncio
from agno.agent import Agent                                                                                                                                  
from agno.models.anthropic import Claude                                                                                                                      
from agno.tools.mcp import MCPTools                                                                                                                           
from agno.skills import Skills, LocalSkills                                                                                                                   
from openinference.instrumentation.agno import AgnoInstrumentor  
from agno.db.in_memory import InMemoryDb                                                                                            
from opentelemetry import trace as trace_api                                                                                                                  
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter                                                                            
from opentelemetry.sdk.trace import TracerProvider                                                                                                            
from opentelemetry.sdk.trace.export import SimpleSpanProcessor  

load_dotenv()
claude_api_key = os.getenv("ANTHROPIC_API_KEY")

# Configure the tracer provider
tracer_provider = TracerProvider()
tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
trace_api.set_tracer_provider(tracer_provider=tracer_provider)

# Start instrumenting agno
AgnoInstrumentor().instrument()

substack_author_mcp = MCPTools(transport="streamable-http", url="https://substack-author.fastmcp.app/mcp")

# Initialize in-memory database for session storage
db = InMemoryDb()

# Create and configure the agent
substack_author_agent = Agent(
    name="Substack Author Agent",
    id="substack-author-agent",
    model=Claude(id="claude-haiku-4-5-20251001", api_key=claude_api_key),
    tools=[substack_author_mcp],
    db=db,
    num_history_runs=10,
    add_history_to_context=True,
    read_chat_history=True,
    read_tool_call_history=True,
    skills=Skills(loaders=[LocalSkills("./skills")]),
    instructions="You are a Substack author agent. Use your skills to help with content strategy.",
    markdown=True,
)

def run_agent():
    return asyncio.run(substack_author_agent.acli_app(stream=True,))

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("SUBSTACK AUTHOR AGENT")
    print("=" * 70)
    print("\nAsk questions about Substack content strategy, get helpful answers!")
    print("=" * 70 + "\n")
    run_agent()

