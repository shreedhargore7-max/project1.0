import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPClient:

    def __init__(self):
        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "app.mcp_server.server"],
        )

        self.session = None
        self._stdio_context = None
        self._session_context = None

    async def _connect(self):
        self._stdio_context = stdio_client(
            self.server_params
        )

        read, write = await self._stdio_context.__aenter__()

        self._session_context = ClientSession(
            read,
            write
        )

        self.session = await self._session_context.__aenter__()

        await self.session.initialize()

    async def _call_tool(self, name, arguments):
        await self._connect()

        result = await self.session.call_tool(
            name,
            arguments=arguments
        )

        return result

    def call_tool(self, name, arguments):
        print(
            f"[MCP CLIENT] Calling tool: {name}",
            file=sys.stderr
        )

        return asyncio.run(
            self._call_tool(name, arguments)
        )

    async def _close(self):
        if self._session_context is not None:
            await self._session_context.__aexit__(
                None,
                None,
                None
            )

        if self._stdio_context is not None:
            await self._stdio_context.__aexit__(
                None,
                None,
                None
            )

    def close(self):
        try:
            asyncio.run(self._close())
        except Exception:
            pass