"""Stdio MCP server exposing the agent's local `get_skill_instructions` tool.

The Claude agent defines this tool in Python (agents/shared/skills.py). `run.py` mounts it
here so the Claude Code CLI can call the same function the SDK loop calls.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "agents"))

from fastmcp import FastMCP
from shared.skills import get_skill_instructions as _get_skill_instructions

mcp = FastMCP("skills")


@mcp.tool()
def get_skill_instructions(skill_name: str) -> str:
    """Load detailed instructions for a skill. Call this FIRST when the user's request matches a skill before using any other tools."""
    return _get_skill_instructions(skill_name)


if __name__ == "__main__":
    mcp.run()
