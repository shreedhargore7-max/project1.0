# ============================================================
# LOCAL MCP CLIENT
# ============================================================
#
# Used for:
#   - memory_search
#   - memory_save
#   - chat_history_search
#
# This client connects to:
#
#   app.mcp_server.server
#
# IMPORTANT:
# This is NOT the Razorpay MCP client.
# Razorpay uses:
#   app/mcp_client/razorpay_client.py
#
# ============================================================

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# ============================================================
# MCP CLIENT
# ============================================================

class MCPClient:

    def __init__(
        self,
        command=None,
        args=None
    ):

        # ----------------------------------------------------
        # Local MCP server
        # ----------------------------------------------------

        self.server_params = StdioServerParameters(

            command=(
                command
                if command
                else sys.executable
            ),

            args=(
                args
                if args
                else [
                    "-m",
                    "app.mcp_server.server"
                ]
            )
        )


    # ========================================================
    # ASYNC TOOL CALL
    # ========================================================

    async def _call_tool(
        self,
        name: str,
        arguments: dict
    ):

        print(
            f"[MCP CLIENT] Starting server..."
        )

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Keep stdio_client and ClientSession inside the SAME
        # async context.
        #
        # Do not manually call __aenter__ / __aexit__.
        # ----------------------------------------------------

        async with stdio_client(
            self.server_params
        ) as (
            read_stream,
            write_stream
        ):

            print(
                "[MCP CLIENT] Initializing..."
            )

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                await session.initialize()

                print(
                    f"[MCP CLIENT] Calling tool: {name}"
                )

                result = await session.call_tool(
                    name,
                    arguments=arguments
                )

                return result


    # ========================================================
    # SYNCHRONOUS TOOL CALL
    # ========================================================

    def call_tool(
        self,
        name: str,
        arguments: dict | None = None
    ):

        if arguments is None:
            arguments = {}

        print(
            f"[MCP CLIENT] Calling: {name}"
        )

        return asyncio.run(
            self._call_tool(
                name,
                arguments
            )
        )


    # ========================================================
    # CLOSE
    # ========================================================
    #
    # Nothing to close manually.
    #
    # stdio_client and ClientSession are automatically closed
    # by their async context managers inside _call_tool().
    #
    # This method is kept so existing mcp_tools.py code that
    # calls client.close() does not break.
    # ========================================================

    def close(self):

        # ----------------------------------------------------
        # No manual asyncio.run() here.
        # ----------------------------------------------------

        pass


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("        LOCAL MCP CLIENT TEST")
    print("=" * 60)

    client = MCPClient()

    try:

        result = client.call_tool(
            "memory_search",
            {
                "query": "What am I building?"
            }
        )

        print("\n[MCP TEST RESULT]")
        print(result)

    except Exception as e:

        print("\n[MCP TEST ERROR]")
        print(type(e).__name__)
        print(str(e))

    finally:

        client.close()