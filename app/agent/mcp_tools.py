# ============================================================
# app/agent/mcp_tools.py
# ============================================================
#
# Unified MCP tool layer
#
# Local tools:
#   - Memory
#   - Chat history
#   - PDF / RAG
#
# Razorpay tools:
#   - Payments
#   - Orders
#   - Refunds
#   - Payment Links
#   - Settlements
#   - QR
#   - Capture
#   - Update operations
#   - Payment-link operations
#   - UPI
#   - Initiate payment
#
# ============================================================

from app.mcp_client.client import MCPClient
from app.agent.razorpay_tools import execute_razorpay_tool


# ============================================================
# EXTRACT MCP RESULT
# ============================================================

def extract_result(result) -> str:

    if result is None:
        return ""

    # --------------------------------------------------------
    # Structured MCP response
    # --------------------------------------------------------

    if hasattr(result, "structured_content"):

        structured = result.structured_content

        if structured:

            if isinstance(structured, dict):

                if "result" in structured:
                    return str(structured["result"])

                return str(structured)

    # --------------------------------------------------------
    # Text response
    # --------------------------------------------------------

    if hasattr(result, "content"):

        texts = []

        for item in result.content:

            if hasattr(item, "text"):

                texts.append(item.text)

        if texts:
            return "\n".join(texts)

    return str(result)


# ============================================================
# MEMORY SEARCH
# ============================================================

def mcp_memory_search(query: str) -> str:

    print("\n[MCP] memory_search")

    client = MCPClient()

    try:

        result = client.call_tool(
            "memory_search",
            {
                "query": query
            }
        )

        return extract_result(result)

    except Exception as e:

        print(f"[MEMORY ERROR] {e}")

        return f"Memory search failed: {e}"

    finally:

        client.close()


# ============================================================
# MEMORY SAVE
# ============================================================

def mcp_memory_save(text: str) -> str:

    print("\n[MCP] memory_save")

    client = MCPClient()

    try:

        result = client.call_tool(
            "memory_save",
            {
                "text": text
            }
        )

        return extract_result(result)

    except Exception as e:

        print(f"[MEMORY SAVE ERROR] {e}")

        return f"Memory save failed: {e}"

    finally:

        client.close()


# ============================================================
# CHAT HISTORY SEARCH
# ============================================================

def mcp_chat_history_search(query: str) -> str:

    print("\n[MCP] chat_history_search")

    client = MCPClient()

    try:

        result = client.call_tool(
            "chat_history_search",
            {
                "query": query
            }
        )

        return extract_result(result)

    except Exception as e:

        print(f"[CHAT HISTORY ERROR] {e}")

        return f"Chat history search failed: {e}"

    finally:

        client.close()


# ============================================================
# PDF SEARCH
# ============================================================

def mcp_pdf_search(query: str) -> str:

    print("\n[MCP] pdf_search")

    try:

        from app.rag.rag_tool import search_pdf

        result = search_pdf(
            query,
            top_k=3
        )

        if not result:
            return "No relevant information found in the PDF."

        return "\n\n".join(
            str(item)
            for item in result
        )

    except Exception as e:

        print(f"[PDF ERROR] {e}")

        return f"PDF search failed: {e}"


# ============================================================
# GENERIC RAZORPAY CALL
# ============================================================

def razorpay_call(
    tool_name: str,
    arguments: dict | None = None
) -> str:

    if arguments is None:
        arguments = {}

    print(
        f"\n[MCP] Razorpay {tool_name}"
    )

    print(
        f"[MCP] Arguments: {arguments}"
    )

    try:

        return execute_razorpay_tool(
            tool_name,
            arguments
        )

    except Exception as e:

        print(
            f"[RAZORPAY ERROR] {e}"
        )

        return f"Razorpay operation failed: {e}"


# ============================================================
# PAYMENTS
# ============================================================


# ------------------------------------------------------------
# 1. FETCH ALL PAYMENTS
# ------------------------------------------------------------

def mcp_razorpay_fetch_all_payments(
    count: int = 10,
    skip: int = 0
) -> str:

    return razorpay_call(
        "fetch_all_payments",
        {
            "count": count,
            "skip": skip
        }
    )


# ------------------------------------------------------------
# 2. FETCH PAYMENT
# ------------------------------------------------------------

def mcp_razorpay_fetch_payment(
    payment_id: str
) -> str:

    return razorpay_call(
        "fetch_payment",
        {
            "payment_id": payment_id
        }
    )


# ------------------------------------------------------------
# 3. FETCH PAYMENT CARD DETAILS
# ------------------------------------------------------------

def mcp_razorpay_fetch_payment_card_details(
    payment_id: str
) -> str:

    return razorpay_call(
        "fetch_payment_card_details",
        {
            "payment_id": payment_id
        }
    )


# ------------------------------------------------------------
# 4. CAPTURE PAYMENT
# ------------------------------------------------------------

def mcp_razorpay_capture_payment(
    payment_id: str,
    amount: int | None = None,
    currency: str = "INR"
) -> str:

    arguments = {
        "payment_id": payment_id,
        "currency": currency
    }

    if amount is not None:
        arguments["amount"] = amount

    return razorpay_call(
        "capture_payment",
        arguments
    )


# ============================================================
# ORDERS
# ============================================================


# ------------------------------------------------------------
# 5. FETCH ALL ORDERS
# ------------------------------------------------------------

def mcp_razorpay_fetch_all_orders(
    count: int = 10,
    skip: int = 0
) -> str:

    return razorpay_call(
        "fetch_all_orders",
        {
            "count": count,
            "skip": skip
        }
    )


# ------------------------------------------------------------
# 6. FETCH ORDER
# ------------------------------------------------------------

def mcp_razorpay_fetch_order(
    order_id: str
) -> str:

    return razorpay_call(
        "fetch_order",
        {
            "order_id": order_id
        }
    )


# ------------------------------------------------------------
# 7. CREATE ORDER
# ------------------------------------------------------------

def mcp_razorpay_create_order(
    amount: int,
    currency: str = "INR",
    receipt: str | None = None,
    notes: dict | None = None
) -> str:

    arguments = {
        "amount": amount,
        "currency": currency
    }

    if receipt:
        arguments["receipt"] = receipt

    if notes:
        arguments["notes"] = notes

    return razorpay_call(
        "create_order",
        arguments
    )


# ------------------------------------------------------------
# 8. FETCH ORDER PAYMENTS
# ------------------------------------------------------------

def mcp_razorpay_fetch_order_payments(
    order_id: str
) -> str:

    return razorpay_call(
        "fetch_order_payments",
        {
            "order_id": order_id
        }
    )


# ------------------------------------------------------------
# 9. UPDATE ORDER
# ------------------------------------------------------------

def mcp_razorpay_update_order(
    order_id: str,
    notes: dict | None = None
) -> str:

    arguments = {
        "order_id": order_id
    }

    if notes is not None:
        arguments["notes"] = notes

    return razorpay_call(
        "update_order",
        arguments
    )


# ============================================================
# REFUNDS
# ============================================================


# ------------------------------------------------------------
# 10. FETCH ALL REFUNDS
# ------------------------------------------------------------

def mcp_razorpay_fetch_all_refunds(
    count: int = 10,
    skip: int = 0
) -> str:

    return razorpay_call(
        "fetch_all_refunds",
        {
            "count": count,
            "skip": skip
        }
    )


# ------------------------------------------------------------
# 11. FETCH REFUND
# ------------------------------------------------------------

def mcp_razorpay_fetch_refund(
    refund_id: str
) -> str:

    return razorpay_call(
        "fetch_refund",
        {
            "refund_id": refund_id
        }
    )


# ------------------------------------------------------------
# 12. CREATE REFUND
# ------------------------------------------------------------

def mcp_razorpay_create_refund(
    payment_id: str,
    amount: int | None = None,
    speed: str | None = None,
    notes: dict | None = None,
    receipt: str | None = None
) -> str:

    arguments = {
        "payment_id": payment_id
    }

    if amount is not None:
        arguments["amount"] = amount

    if speed:
        arguments["speed"] = speed

    if notes:
        arguments["notes"] = notes

    if receipt:
        arguments["receipt"] = receipt

    return razorpay_call(
        "create_refund",
        arguments
    )


# ------------------------------------------------------------
# 13. UPDATE REFUND
# ------------------------------------------------------------

def mcp_razorpay_update_refund(
    refund_id: str,
    notes: dict | None = None
) -> str:

    arguments = {
        "refund_id": refund_id
    }

    if notes is not None:
        arguments["notes"] = notes

    return razorpay_call(
        "update_refund",
        arguments
    )


# ============================================================
# PAYMENT LINKS
# ============================================================


# ------------------------------------------------------------
# 14. CREATE PAYMENT LINK
# ------------------------------------------------------------

def mcp_razorpay_create_payment_link(
    amount: int,
    description: str,
    currency: str = "INR",
    customer_name: str | None = None,
    customer_email: str | None = None,
    customer_contact: str | None = None,
    reference_id: str | None = None
) -> str:

    arguments = {
        "amount": amount,
        "currency": currency,
        "description": description
    }

    if customer_name:
        arguments["customer_name"] = customer_name

    if customer_email:
        arguments["customer_email"] = customer_email

    if customer_contact:
        arguments["customer_contact"] = customer_contact

    if reference_id:
        arguments["reference_id"] = reference_id

    return razorpay_call(
        "create_payment_link",
        arguments
    )


# ------------------------------------------------------------
# 15. FETCH ALL PAYMENT LINKS
# ------------------------------------------------------------

def mcp_razorpay_fetch_all_payment_links(
    count: int = 10,
    skip: int = 0
) -> str:

    return razorpay_call(
        "fetch_all_payment_links",
        {
            "count": count,
            "skip": skip
        }
    )


# ------------------------------------------------------------
# 16. FETCH PAYMENT LINK
# ------------------------------------------------------------

def mcp_razorpay_fetch_payment_link(
    payment_link_id: str
) -> str:

    return razorpay_call(
        "fetch_payment_link",
        {
            "payment_link_id": payment_link_id
        }
    )


# ------------------------------------------------------------
# 17. UPDATE PAYMENT LINK
# ------------------------------------------------------------

def mcp_razorpay_update_payment_link(
    payment_link_id: str,
    reference_id: str | None = None,
    description: str | None = None,
    expire_by: int | None = None
) -> str:

    arguments = {
        "payment_link_id": payment_link_id
    }

    if reference_id is not None:
        arguments["reference_id"] = reference_id

    if description is not None:
        arguments["description"] = description

    if expire_by is not None:
        arguments["expire_by"] = expire_by

    return razorpay_call(
        "update_payment_link",
        arguments
    )


# ------------------------------------------------------------
# 18. PAYMENT LINK NOTIFY
# ------------------------------------------------------------

def mcp_razorpay_payment_link_notify(
    payment_link_id: str,
    medium: str = "sms"
) -> str:

    return razorpay_call(
        "payment_link_notify",
        {
            "payment_link_id": payment_link_id,
            "medium": medium
        }
    )


# ------------------------------------------------------------
# 19. PAYMENT LINK UPI CREATE
# ------------------------------------------------------------

def mcp_razorpay_payment_link_upi_create(
    payment_link_id: str
) -> str:

    return razorpay_call(
        "payment_link_upi_create",
        {
            "payment_link_id": payment_link_id
        }
    )


# ============================================================
# SETTLEMENTS
# ============================================================


# ------------------------------------------------------------
# 20. FETCH SETTLEMENTS
# ------------------------------------------------------------

def mcp_razorpay_fetch_settlements(
    count: int = 10,
    skip: int = 0
) -> str:

    return razorpay_call(
        "fetch_settlements",
        {
            "count": count,
            "skip": skip
        }
    )


# ------------------------------------------------------------
# 21. FETCH ALL SETTLEMENTS
#
# Alias kept because different versions of unified_agent.py
# may use either name.
# ------------------------------------------------------------

def mcp_razorpay_fetch_all_settlements(
    count: int = 10,
    skip: int = 0
) -> str:

    return razorpay_call(
        "fetch_settlements",
        {
            "count": count,
            "skip": skip
        }
    )


# ------------------------------------------------------------
# 22. FETCH SINGLE SETTLEMENT
# ------------------------------------------------------------

def mcp_razorpay_fetch_settlement(
    settlement_id: str
) -> str:

    return razorpay_call(
        "fetch_settlement",
        {
            "settlement_id": settlement_id
        }
    )


# ============================================================
# QR CODE
# ============================================================


# ------------------------------------------------------------
# 23. CREATE QR CODE
# ------------------------------------------------------------

def mcp_razorpay_create_qr_code(
    payment_amount: int,
    description: str = "",
    name: str = "Razorpay QR",
    usage: str = "single_use",
    fixed_amount: bool = True
) -> str:

    arguments = {
        "type": "upi_qr",
        "name": name,
        "usage": usage,
        "fixed_amount": fixed_amount,
        "payment_amount": payment_amount
    }

    if description:
        arguments["description"] = description

    return razorpay_call(
        "create_qr_code",
        arguments
    )


# ============================================================
# PAYMENT INITIATION
# ============================================================


# ------------------------------------------------------------
# 24. INITIATE PAYMENT
# ------------------------------------------------------------

def mcp_razorpay_initiate_payment(
    amount: int,
    currency: str = "INR",
    email: str | None = None,
    contact: str | None = None,
    order_id: str | None = None
) -> str:

    arguments = {
        "amount": amount,
        "currency": currency
    }

    if email:
        arguments["email"] = email

    if contact:
        arguments["contact"] = contact

    if order_id:
        arguments["order_id"] = order_id

    return razorpay_call(
        "initiate_payment",
        arguments
    )


# ============================================================
# EXTRA UPDATE OPERATIONS
# ============================================================


# ------------------------------------------------------------
# 25. UPDATE PAYMENT
# ------------------------------------------------------------

def mcp_razorpay_update_payment(
    payment_id: str,
    notes: dict | None = None
) -> str:

    arguments = {
        "payment_id": payment_id
    }

    if notes is not None:
        arguments["notes"] = notes

    return razorpay_call(
        "update_payment",
        arguments
    )


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================
#
# These prevent ImportError when unified_agent.py uses a slightly
# different function name.
#
# ============================================================


def mcp_razorpay_fetch_all_settlement(
    count: int = 10,
    skip: int = 0
) -> str:

    return mcp_razorpay_fetch_settlements(
        count=count,
        skip=skip
    )


# ============================================================
# FINAL STATUS
# ============================================================

print("[MCP TOOLS] Loaded successfully.")