import asyncio

from app.mcp_client.client import MCPClient


async def main():

    client = MCPClient()

    try:

        await client.connect()

        print("\n[MCP TEST] Calling memory_search...")

        result = await client.call_tool(
            "memory_search",
            {
                "query": "favorite programming language"
            }
        )

        print("\n[MCP TEST RESULT]")
        print(result)

    finally:

        await client.close()


if __name__ == "__main__":
    asyncio.run(main())