"""
Substack Author Agent — interactive CLI
Usage: python agent.py [--sdk agno|claude|openai]
"""

import asyncio
import importlib.util
import os
import sys
import uuid
import typer

app = typer.Typer(add_completion=False)

_here = os.path.dirname(os.path.abspath(__file__))
_agents_dir = os.path.join(_here, "agents")


def _load(module_name: str, rel_path: str):
    path = os.path.join(_here, rel_path)
    spec = importlib.util.spec_from_file_location(module_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)
    return mod


async def _readline_loop(mod, sdk: str):
    session_id = str(uuid.uuid4())
    print("Ask questions about your Substack. Type 'exit' to quit.\n")

    connected = False
    if sdk == "openai":
        await mod.mcp_server.connect()
        connected = True

    try:
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break
            if user_input.lower() in ("exit", "quit", "q"):
                print("Goodbye!")
                break
            if not user_input:
                continue
            response = await mod.run(user_input, session_id)
            print(f"\nAgent: {response}\n")
    finally:
        if connected:
            await mod.mcp_server.cleanup()


@app.command()
def main(
    sdk: str = typer.Option("agno", help="SDK to use: agno | claude | openai"),
):
    if sdk not in ("agno", "claude", "openai"):
        typer.echo(f"Invalid SDK '{sdk}'. Choose from: agno, claude, openai")
        raise typer.Exit(1)

    print(f"\n{'='*60}")
    print(f"  SUBSTACK AUTHOR AGENT  [{sdk.upper()}]")
    print(f"{'='*60}\n")

    # Pre-cache installed SDKs, then expose agents/ internals via sys.path
    import agno as _agno_pkg          # noqa: F401
    import agents as _openai_agents   # noqa: F401
    import openai as _openai_pkg      # noqa: F401

    if _agents_dir not in sys.path:
        sys.path.insert(1, _agents_dir)

    if sdk == "agno":
        mod = _load("_cli_agno", "agents/agno/agent.py")
        asyncio.run(mod._agent.acli_app(stream=True))
    elif sdk == "claude":
        mod = _load("_cli_claude", "agents/claude/agent.py")
        asyncio.run(_readline_loop(mod, "claude"))
    elif sdk == "openai":
        mod = _load("_cli_openai", "agents/openai/agent.py")
        asyncio.run(_readline_loop(mod, "openai"))


if __name__ == "__main__":
    app()
