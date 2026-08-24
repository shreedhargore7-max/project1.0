# app/mcp_client/test_razorpay.py

import asyncio
import traceback

from app.mcp_client.razorpay_client import (
    get_razorpay_tools
)


async def main():

    print()
    print("=" * 60)
    print("             RAZORPAY MCP TEST")
    print("=" * 60)
    print()

    try:

        tools = await get_razorpay_tools()

        print()
        print("=" * 60)
        print(
            f"SUCCESS: {len(tools)} RAZORPAY TOOLS FOUND"
        )
        print("=" * 60)
        print()

        for tool in tools:

            print(
                f"TOOL: {tool.name}"
            )

            if tool.description:

                print(
                    f"DESCRIPTION: {tool.description}"
                )

            print("-" * 60)

    except Exception as e:

        print()
        print("=" * 60)
        print("             RAZORPAY MCP ERROR")
        print("=" * 60)
        print()

        print(
            "TYPE:",
            type(e).__name__
        )

        print(
            "ERROR:",
            repr(e)
        )

        print()
        print("TRACEBACK:")
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())