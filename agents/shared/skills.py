"""
Skill loading — fetches skills exposed by the MCP server as resources
(skill://<name>/SKILL.md), so all three agents share one skill source.
Fetched once at import time.
"""

import asyncio
import json
import re

import yaml
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from constants import MCP_URL


def _parse_skill_md(content: str) -> tuple[dict, str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not match:
        return {}, content.strip()
    return yaml.safe_load(match.group(1)) or {}, match.group(2).strip()


async def _read_skill(session: ClientSession, resource) -> dict:
    result = await session.read_resource(resource.uri)
    content = "".join(part.text for part in result.contents if hasattr(part, "text"))
    frontmatter, instructions = _parse_skill_md(content)
    uri = str(resource.uri)
    name = frontmatter.get("name") or uri.removeprefix("skill://").removesuffix("/SKILL.md")
    return {
        "name": name,
        "description": frontmatter.get("description") or resource.description or "",
        "instructions": instructions,
        "uri": uri,
    }


async def _fetch_skills() -> dict[str, dict]:
    async with streamable_http_client(MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_resources()
            skill_resources = [r for r in listing.resources if str(r.uri).endswith("/SKILL.md")]
            skills = await asyncio.gather(*(_read_skill(session, r) for r in skill_resources))
            return {skill["name"]: skill for skill in skills}


SKILLS = asyncio.run(_fetch_skills())


def get_skills_prompt_snippet() -> str:
    """System prompt block listing skills — tells the agent to call get_skill_instructions first."""
    if not SKILLS:
        return ""
    names = ", ".join(SKILLS.keys())
    return (
        f"You have skills for content strategy tasks. "
        f"When the user's request is about content analysis or planning, "
        f"call get_skill_instructions(skill_name) FIRST — before any other tool — "
        f"to load step-by-step instructions. Available skills: {names}."
    )


def get_skill_instructions(skill_name: str) -> str:
    """
    Load instructions for a skill by name. Call this when the user's request matches
    one of the available skills before proceeding with other tools.
    """
    skill = SKILLS.get(skill_name)
    if not skill:
        return json.dumps({
            "error": f"Skill '{skill_name}' not found",
            "available": list(SKILLS.keys()),
        })
    return json.dumps({
        "skill_name": skill["name"],
        "description": skill["description"],
        "instructions": skill["instructions"],
    })


# Claude tool schema for get_skill_instructions
CLAUDE_SKILL_TOOL: dict = {
    "name": "get_skill_instructions",
    "description": (
        "Load detailed instructions for a skill. Call this FIRST when the user's request "
        "matches a skill before using any other tools."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "skill_name": {
                "type": "string",
                "description": "The skill name to load.",
                "enum": list(SKILLS.keys()),
            }
        },
        "required": ["skill_name"],
    },
}
