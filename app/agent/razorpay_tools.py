from app.mcp_client.razorpay_client import (
    call_razorpay_tool
)


# ============================================================
# EXECUTE RAZORPAY TOOL
# ============================================================

def execute_razorpay_tool(
    tool_name: str,
    arguments: dict | None = None
) -> str:

    if arguments is None:
        arguments = {}

    print(
        "\n[RAZORPAY AGENT TOOL]"
    )

    print(
        f"Tool: {tool_name}"
    )

    print(
        f"Arguments: {arguments}"
    )

    result = call_razorpay_tool(
        tool_name,
        arguments
    )

    text = extract_result(result)

    print(
        "\n[RAZORPAY TOOL RESULT]"
    )

    print(text)

    return text


# ============================================================
# EXTRACT RESULT
# ============================================================

def extract_result(result) -> str:

    if result is None:
        return ""

    # --------------------------------------------------------
    # Text content
    # --------------------------------------------------------

    if hasattr(result, "content"):

        texts = []

        for item in result.content:

            if hasattr(item, "text"):

                texts.append(
                    item.text
                )

        if texts:

            return "\n".join(texts)

    # --------------------------------------------------------
    # Structured content
    # --------------------------------------------------------

    if hasattr(
        result,
        "structured_content"
    ):

        structured = (
            result.structured_content
        )

        if structured:

            if isinstance(
                structured,
                dict
            ):

                if "result" in structured:

                    return str(
                        structured["result"]
                    )

                return str(
                    structured
                )

    return str(result)