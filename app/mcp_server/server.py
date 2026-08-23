import sys

from mcp.server import MCPServer
from mcp.types import Tool, TextContent

from app.memory.memory_tool import search_memory, save_memory
from app.rag.rag_tool import search_pdf
from app.chat_history.chat_history_tool import search_chat_history


mcp = MCPServer(
    name="Intelligent RAG Assistant",
    version="1.0.0",
)


@mcp.tool(
    name="memory_search",
    description="Search the user's long-term memory."
)
async def memory_search(query: str) -> str:
    result = search_memory(query)

    if not result:
        return "No relevant memories found."

    return "\n".join(result)


@mcp.tool(
    name="memory_save",
    description="Save useful information to the user's long-term memory."
)
async def memory_save(text: str) -> str:
    result = save_memory(text)

    if result:
        return "Memory saved successfully."

    return "Memory could not be saved."


@mcp.tool(
    name="pdf_search",
    description="Search the indexed PDF documents."
)
async def pdf_search(query: str) -> str:
    result = search_pdf(query)

    if not result:
        return "No relevant PDF information found."

    if isinstance(result, list):
        return "\n\n".join(str(x) for x in result)

    return str(result)


@mcp.tool(
    name="chat_history_search",
    description="Search previous conversations."
)
async def chat_history_search(query: str) -> str:
    result = search_chat_history(query)

    if not result:
        return "No relevant conversation history found."

    if isinstance(result, list):
        return "\n".join(str(x) for x in result)

    return str(result)


if __name__ == "__main__":
    print(
        "[MCP SERVER] Starting MCP server...",
        file=sys.stderr
    )

    mcp.run(
        transport="stdio"
    )