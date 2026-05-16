"""
Skill loading — mirrors Agno's LocalSkills/Skills mechanics for use in
the Anthropic SDK and OpenAI Agents SDK agents.
"""

import json
import os
import re

_SKILLS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "skills"))


def _parse_skill_md(content: str) -> tuple[dict, str]:
    match = re.match(r"^---\n(.*?)\n---\n(.*)", content, re.DOTALL)
    if not match:
        return {}, content
    frontmatter = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            frontmatter[key.strip()] = val.strip().strip('"')
    return frontmatter, match.group(2).strip()


def _load_skills() -> dict[str, dict]:
    skills = {}
    if not os.path.isdir(_SKILLS_DIR):
        return skills
    for entry in sorted(os.listdir(_SKILLS_DIR)):
        path = os.path.join(_SKILLS_DIR, entry, "SKILL.md")
        if not os.path.isfile(path):
            continue
        with open(path) as f:
            frontmatter, instructions = _parse_skill_md(f.read())
        name = frontmatter.get("name", entry)
        skills[name] = {
            "name": name,
            "description": frontmatter.get("description", ""),
            "instructions": instructions,
        }
    return skills


SKILLS = _load_skills()


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
