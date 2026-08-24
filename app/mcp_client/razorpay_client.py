import os
import asyncio
import base64

import httpx

from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# RAZORPAY CONFIGURATION
# ============================================================

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

RAZORPAY_MCP_URL = "https://mcp.razorpay.com/mcp"


# ============================================================
# VALIDATE CREDENTIALS
# ============================================================

if not RAZORPAY_KEY_ID:
    raise ValueError(
        "RAZORPAY_KEY_ID is missing from .env"
    )

if not RAZORPAY_KEY_SECRET:
    raise ValueError(
        "RAZORPAY_KEY_SECRET is missing from .env"
    )


# ============================================================
# AUTH HEADER
# ============================================================

def get_auth_header():
    """
    Create HTTP Basic Authentication header
    for Razorpay MCP.
    """

    credentials = (
        f"{RAZORPAY_KEY_ID}:{RAZORPAY_KEY_SECRET}"
    )

    encoded = base64.b64encode(
        credentials.encode("utf-8")
    ).decode("utf-8")

    return {
        "Authorization": f"Basic {encoded}"
    }


# ============================================================
# CONNECT TO RAZORPAY MCP
# ============================================================

async def _create_session():

    headers = get_auth_header()

    http_client = httpx.AsyncClient(
        headers=headers,
        timeout=60.0
    )

    transport = streamable_http_client(
        RAZORPAY_MCP_URL,
        http_client=http_client
    )

    return http_client, transport


# ============================================================
# CALL RAZORPAY MCP TOOL
# ============================================================

async def _call_razorpay_tool(
    tool_name: str,
    arguments: dict | None = None
):

    if arguments is None:
        arguments = {}

    headers = get_auth_header()

    print(
        f"[RAZORPAY MCP] Calling tool: {tool_name}"
    )

    print(
        f"[RAZORPAY MCP] Arguments: {arguments}"
    )

    import httpx

    async with httpx.AsyncClient(
        headers=headers,
        timeout=60.0
    ) as http_client:

        async with streamable_http_client(
            RAZORPAY_MCP_URL,
            http_client=http_client
        ) as transport:

            read_stream, write_stream = transport

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                print(
                    "[RAZORPAY MCP] Initializing..."
                )

                await session.initialize()

                print(
                    f"[RAZORPAY MCP] Calling: {tool_name}"
                )

                result = await session.call_tool(
                    tool_name,
                    arguments
                )

                return result


# ============================================================
# PUBLIC TOOL CALL
# ============================================================

def call_razorpay_tool(
    tool_name: str,
    arguments: dict | None = None
):

    if arguments is None:
        arguments = {}

    print(
        f"[RAZORPAY MCP] Calling tool: {tool_name}"
    )

    return asyncio.run(
        _call_razorpay_tool(
            tool_name,
            arguments
        )
    )


# ============================================================
# LIST AVAILABLE RAZORPAY MCP TOOLS
# ============================================================

async def _list_razorpay_tools():

    headers = get_auth_header()

    print(
        "[RAZORPAY MCP] Connecting to list tools..."
    )

    import httpx

    async with httpx.AsyncClient(
        headers=headers,
        timeout=60.0
    ) as http_client:

        async with streamable_http_client(
            RAZORPAY_MCP_URL,
            http_client=http_client
        ) as transport:

            read_stream, write_stream = transport

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                print(
                    "[RAZORPAY MCP] Initializing..."
                )

                await session.initialize()

                print(
                    "[RAZORPAY MCP] Requesting available tools..."
                )

                result = await session.list_tools()

                return result


# ============================================================
# PUBLIC LIST TOOLS FUNCTION
# ============================================================

def list_razorpay_tools():

    return asyncio.run(
        _list_razorpay_tools()
    )


# ============================================================
# PRINT AVAILABLE TOOLS
# ============================================================

def show_razorpay_tools():

    result = list_razorpay_tools()

    print()
    print("=" * 60)
    print("AVAILABLE RAZORPAY MCP TOOLS")
    print("=" * 60)

    if not result or not hasattr(result, "tools"):

        print("No tools returned.")

        return

    tools = result.tools

    print(
        f"Total tools: {len(tools)}"
    )

    print()

    for index, tool in enumerate(
        tools,
        start=1
    ):

        print(
            f"{index}. {tool.name}"
        )

        if getattr(
            tool,
            "description",
            None
        ):

            print(
                f"   {tool.description}"
            )

        print()

    print("=" * 60)


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("       RAZORPAY MCP CLIENT")
    print("=" * 60)

    print()
    print(
        "Razorpay MCP URL:"
    )

    print(
        RAZORPAY_MCP_URL
    )

    print()

    try:

        show_razorpay_tools()

    except Exception as e:

        print()
        print(
            "[RAZORPAY MCP ERROR]"
        )

        print(
            type(e).__name__,
            ":",
            e
        )