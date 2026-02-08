"""
Tool Discovery Script

Queries the meanerbeaver/pdf-parse MCP server to discover
available tools and their exact input parameter schemas.

Usage: cd server && python discover_tools.py
"""

import asyncio
from dedalus_labs import AsyncDedalus, DedalusRunner
from dotenv import load_dotenv

load_dotenv()


async def main():
    client = AsyncDedalus()
    runner = DedalusRunner(client)
    result = await runner.run(
        input=(
            "List all available tools from the pdf-parse MCP server. "
            "For each tool, show its name, description, and full input "
            "parameter schema including parameter names, types, and "
            "which are required."
        ),
        model="openai/gpt-4o",
        max_steps=2,
        mcp_servers=["meanerbeaver/pdf-parse"],
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
