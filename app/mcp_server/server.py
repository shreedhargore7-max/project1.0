import sys

from mcp.server import MCPServer

from app.memory.memory_tool import search_memory, save_memory
from app.chat_history.chat_history_tool import search_chat_history


mcp = MCPServer(
    name="Intelligent Assistant MCP Server",
    version="1.0.0",
)


@mcp.tool(
    name="memory_search",
    description="Search the user's long-term memory."
)
async def memory_search(query: str) -> str:

    try:
        result = search_memory(query)

        if not result:
            return "No relevant memories found."

        return "\n".join(str(item) for item in result)

    except Exception as e:

        print(
            f"[MCP ERROR] memory_search: {e}",
            file=sys.stderr,
            flush=True
        )

        return f"Memory search failed: {e}"


@mcp.tool(
    name="memory_save",
    description="Save information to long-term memory."
)
async def memory_save(text: str) -> str:

    try:
        result = save_memory(text)

        if result:
            return "Memory saved successfully."

        return "Memory could not be saved."

    except Exception as e:

        print(
            f"[MCP ERROR] memory_save: {e}",
            file=sys.stderr,
            flush=True
        )

        return f"Memory save failed: {e}"


@mcp.tool(
    name="chat_history_search",
    description="Search previous conversations."
)
async def chat_history_search(query: str) -> str:

    try:
        result = search_chat_history(query)

        if not result:
            return "No relevant conversation history found."

        return "\n\n".join(
            str(item) for item in result
        )

    except Exception as e:

        print(
            f"[MCP ERROR] chat_history_search: {e}",
            file=sys.stderr,
            flush=True
        )

        return f"Chat history search failed: {e}"


if __name__ == "__main__":

    print(
        "[MCP SERVER] Starting...",
        file=sys.stderr,
        flush=True
    )

    mcp.run(
        transport="stdio"
    )