from app.mcp_client.client import MCPClient


def mcp_memory_search(query: str) -> str:
    print("\n[MCP] memory_search")

    client = MCPClient()

    try:
        result = client.call_tool(
            "memory_search",
            {"query": query}
        )

        return extract_result(result)

    finally:
        client.close()


def mcp_memory_save(text: str) -> str:
    print("\n[MCP] memory_save")

    client = MCPClient()

    try:
        result = client.call_tool(
            "memory_save",
            {"text": text}
        )

        return extract_result(result)

    finally:
        client.close()


def mcp_pdf_search(query: str) -> str:
    print("\n[MCP] pdf_search")

    client = MCPClient()

    try:
        result = client.call_tool(
            "pdf_search",
            {"query": query}
        )

        return extract_result(result)

    finally:
        client.close()


def mcp_chat_history_search(query: str) -> str:
    print("\n[MCP] chat_history_search")

    client = MCPClient()

    try:
        result = client.call_tool(
            "chat_history_search",
            {"query": query}
        )

        return extract_result(result)

    finally:
        client.close()


def extract_result(result) -> str:
    """
    Convert MCP CallToolResult into plain text.
    """

    if result is None:
        return ""

    # Structured MCP response
    if hasattr(result, "structured_content"):
        structured = result.structured_content

        if isinstance(structured, dict):
            value = structured.get("result")

            if value is not None:
                return str(value)

    # Text content fallback
    if hasattr(result, "content"):
        texts = []

        for item in result.content:
            if hasattr(item, "text"):
                texts.append(item.text)

        if texts:
            return "\n".join(texts)

    return str(result)