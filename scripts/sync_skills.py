"""Snapshot the skills the MCP server exposes (skill://<name>/SKILL.md) into skills/.

The agents fetch them live at startup. The plugin evals need them on disk, so run
this whenever the server's skills change and commit the diff.
"""

import asyncio
from pathlib import Path

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

MCP_URL = "https://substack-author.fastmcp.app/mcp"
SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"


async def main() -> None:
    async with streamable_http_client(MCP_URL) as streams:
        # mcp<2 yields (read, write, get_session_id); newer versions yield (read, write)
        read, write = streams[:2]
        async with ClientSession(read, write) as session:
            await session.initialize()
            listing = await session.list_resources()
            for resource in listing.resources:
                uri = str(resource.uri)
                if not uri.endswith("/SKILL.md"):
                    continue
                name = uri.removeprefix("skill://").removesuffix("/SKILL.md")
                result = await session.read_resource(resource.uri)
                text = "".join(p.text for p in result.contents if hasattr(p, "text"))
                target = SKILLS_DIR / name / "SKILL.md"
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text)
                print(f"synced {name}")


asyncio.run(main())
