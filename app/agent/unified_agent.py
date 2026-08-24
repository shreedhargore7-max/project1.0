# ============================================================
# UNIFIED AI AGENT
# ============================================================
#
# Handles:
#   1. Memory
#   2. PDF / RAG
#   3. Chat History
#   4. Razorpay MCP
#   5. General conversation
#
# Architecture:
#
# User
#   ↓
# Router
#   ↓
# Selected tool
#   ↓
# Tool execution
#   ↓
# Gemini / OpenRouter
#   ↓
# Final answer
#
# ============================================================


from typing import TypedDict

from langgraph.graph import StateGraph, END


# ============================================================
# GEMINI / OPENROUTER
# ============================================================

from app.chat.gemini_client import generate_answer


# ============================================================
# MCP TOOLS
# ============================================================

from app.agent.mcp_tools import (

    # --------------------------------------------------------
    # Memory
    # --------------------------------------------------------

    mcp_memory_search,
    mcp_memory_save,

    # --------------------------------------------------------
    # Chat history
    # --------------------------------------------------------

    mcp_chat_history_search,

    # --------------------------------------------------------
    # PDF / RAG
    # --------------------------------------------------------

    mcp_pdf_search,

    # --------------------------------------------------------
    # Razorpay
    # --------------------------------------------------------

    mcp_razorpay_fetch_all_payments,
    mcp_razorpay_fetch_payment,

    mcp_razorpay_fetch_all_orders,
    mcp_razorpay_fetch_order,

    mcp_razorpay_fetch_all_refunds,
    mcp_razorpay_fetch_refund,

    mcp_razorpay_create_payment_link,
    mcp_razorpay_fetch_all_payment_links,

    mcp_razorpay_fetch_settlements,
    mcp_razorpay_fetch_settlement,
)


# ============================================================
# AGENT STATE
# ============================================================

class AgentState(TypedDict, total=False):

    question: str

    chat_history: str

    memory_context: str

    tool: str

    tool_result: str

    answer: str


# ============================================================
# ROUTER
# ============================================================

def router_node(state: AgentState):

    question = state.get(
        "question",
        ""
    ).strip()

    q = question.lower()

    print("\n========================================")
    print("        INTELLIGENT AGENT")
    print("========================================")

    print("\n[ROUTER] Question:")
    print(question)

    # ========================================================
    # RAZORPAY
    # ========================================================

    razorpay_keywords = [

        "razorpay",

        "payment",
        "payments",

        "order",
        "orders",

        "refund",
        "refunds",

        "settlement",
        "settlements",

        "payment link",
        "payment links",

        "qr code",
        "qr codes",

        "payout",
        "payouts",
    ]

    if any(
        keyword in q
        for keyword in razorpay_keywords
    ):

        selected = "razorpay"

    # ========================================================
    # PDF / RAG
    # ========================================================

    elif any(
        keyword in q
        for keyword in [
            "pdf",
            "document",
            "file",
            "according to the document",
            "according to pdf",
            "what does the document say",
        ]
    ):

        selected = "pdf"

    # ========================================================
    # MEMORY
    # ========================================================

    elif any(
        keyword in q
        for keyword in [
            "remember",
            "memory",
            "what am i building",
            "what do you know about me",
            "what did i tell you",
        ]
    ):

        selected = "memory"

    # ========================================================
    # CHAT HISTORY
    # ========================================================

    elif any(
        keyword in q
        for keyword in [
            "previous conversation",
            "previous chat",
            "earlier conversation",
            "earlier chat",
            "chat history",
            "what did we discuss",
            "what we discussed",
        ]
    ):

        selected = "chat_history"

    # ========================================================
    # GENERAL
    # ========================================================

    else:

        selected = "general"

    print(
        f"[ROUTER] Selected tool: {selected}"
    )

    state["tool"] = selected

    return state


# ============================================================
# MEMORY NODE
# ============================================================

def memory_node(state: AgentState):

    print("\n[AGENT] Memory search")

    question = state.get(
        "question",
        ""
    )

    try:

        result = mcp_memory_search(
            question
        )

        state["memory_context"] = str(
            result
        )

        state["tool_result"] = str(
            result
        )

    except Exception as e:

        print(
            f"[MEMORY ERROR] {e}"
        )

        state["memory_context"] = ""

        state["tool_result"] = (
            f"Memory search failed: {e}"
        )

    return state


# ============================================================
# PDF NODE
# ============================================================

def pdf_node(state: AgentState):

    print("\n[AGENT] PDF / RAG search")

    question = state.get(
        "question",
        ""
    )

    try:

        result = mcp_pdf_search(
            question
        )

        state["tool_result"] = str(
            result
        )

    except Exception as e:

        print(
            f"[PDF ERROR] {e}"
        )

        state["tool_result"] = (
            f"PDF search failed: {e}"
        )

    return state


# ============================================================
# CHAT HISTORY NODE
# ============================================================

def chat_history_node(state: AgentState):

    print(
        "\n[AGENT] Chat history search"
    )

    question = state.get(
        "question",
        ""
    )

    try:

        result = mcp_chat_history_search(
            question
        )

        state["tool_result"] = str(
            result
        )

    except Exception as e:

        print(
            f"[CHAT HISTORY ERROR] {e}"
        )

        state["tool_result"] = (
            f"Chat history search failed: {e}"
        )

    return state


# ============================================================
# RAZORPAY NODE
# ============================================================

def razorpay_node(state: AgentState):

    print("\n[AGENT] Razorpay MCP")

    question = state.get(
        "question",
        ""
    ).strip()

    q = question.lower()

    # ========================================================
    # CREATE PAYMENT LINK
    # ========================================================

    if (
        (
            "create" in q
            or "make" in q
            or "generate" in q
        )
        and "payment link" in q
    ):

        print(
            "[RAZORPAY] Action: create_payment_link"
        )

        # ----------------------------------------------------
        # IMPORTANT
        # ----------------------------------------------------
        # We currently do not guess the amount.
        # The agent should only create a payment link when
        # an amount is explicitly supplied.
        #
        # For now, return a clear instruction.
        # ----------------------------------------------------

        state["tool_result"] = (
            "To create a Razorpay payment link, "
            "please provide the amount and description. "
            "Example: Create a payment link for ₹500 "
            "for a laptop."
        )

        return state

    # ========================================================
    # FETCH SPECIFIC PAYMENT
    # ========================================================

    if (
        "payment" in q
        and "link" not in q
        and any(
            x in q
            for x in [
                "payment id",
                "payment_id",
                "paymentid",
            ]
        )
    ):

        print(
            "[RAZORPAY] Action: fetch_payment"
        )

        state["tool_result"] = (
            "Please provide the Razorpay payment ID. "
            "Example: Show payment pay_XXXXXXXXXXXXXX"
        )

        return state

    # ========================================================
    # FETCH SPECIFIC ORDER
    # ========================================================

    if (
        "order" in q
        and any(
            x in q
            for x in [
                "order id",
                "order_id",
                "orderid",
            ]
        )
    ):

        print(
            "[RAZORPAY] Action: fetch_order"
        )

        state["tool_result"] = (
            "Please provide the Razorpay order ID. "
            "Example: Show order order_XXXXXXXXXXXXXX"
        )

        return state

    # ========================================================
    # FETCH SPECIFIC REFUND
    # ========================================================

    if (
        "refund" in q
        and any(
            x in q
            for x in [
                "refund id",
                "refund_id",
                "refundid",
            ]
        )
    ):

        print(
            "[RAZORPAY] Action: fetch_refund"
        )

        state["tool_result"] = (
            "Please provide the Razorpay refund ID. "
            "Example: Show refund rfnd_XXXXXXXXXXXXXX"
        )

        return state

    # ========================================================
    # PAYMENT LINKS
    # ========================================================

    if (
        "payment link" in q
        or "payment links" in q
    ):

        print(
            "[RAZORPAY] Action: fetch_all_payment_links"
        )

        try:

            result = (
                mcp_razorpay_fetch_all_payment_links(
                    count=10,
                    skip=0
                )
            )

            state["tool_result"] = str(
                result
            )

        except Exception as e:

            print(
                f"[RAZORPAY ERROR] {e}"
            )

            state["tool_result"] = (
                f"Razorpay payment links failed: {e}"
            )

        return state

    # ========================================================
    # REFUNDS
    # ========================================================

    if "refund" in q:

        print(
            "[RAZORPAY] Action: fetch_all_refunds"
        )

        try:

            result = (
                mcp_razorpay_fetch_all_refunds(
                    count=10,
                    skip=0
                )
            )

            state["tool_result"] = str(
                result
            )

        except Exception as e:

            print(
                f"[RAZORPAY ERROR] {e}"
            )

            state["tool_result"] = (
                f"Razorpay refunds failed: {e}"
            )

        return state

    # ========================================================
    # SETTLEMENTS
    # ========================================================

    if "settlement" in q:

        print(
            "[RAZORPAY] Action: fetch_settlements"
        )

        try:

            result = (
                mcp_razorpay_fetch_settlements(
                    count=10,
                    skip=0
                )
            )

            state["tool_result"] = str(
                result
            )

        except Exception as e:

            print(
                f"[RAZORPAY ERROR] {e}"
            )

            state["tool_result"] = (
                f"Razorpay settlements failed: {e}"
            )

        return state

    # ========================================================
    # ORDERS
    # ========================================================

    if "order" in q:

        print(
            "[RAZORPAY] Action: fetch_all_orders"
        )

        try:

            result = (
                mcp_razorpay_fetch_all_orders(
                    count=10,
                    skip=0
                )
            )

            state["tool_result"] = str(
                result
            )

        except Exception as e:

            print(
                f"[RAZORPAY ERROR] {e}"
            )

            state["tool_result"] = (
                f"Razorpay orders failed: {e}"
            )

        return state

    # ========================================================
    # PAYMENTS
    # ========================================================

    if "payment" in q:

        print(
            "[RAZORPAY] Action: fetch_all_payments"
        )

        try:

            result = (
                mcp_razorpay_fetch_all_payments(
                    count=10,
                    skip=0
                )
            )

            state["tool_result"] = str(
                result
            )

        except Exception as e:

            print(
                f"[RAZORPAY ERROR] {e}"
            )

            state["tool_result"] = (
                f"Razorpay payments failed: {e}"
            )

        return state

    # ========================================================
    # DEFAULT RAZORPAY ACTION
    # ========================================================

    print(
        "[RAZORPAY] Action: fetch_all_payments"
    )

    try:

        result = (
            mcp_razorpay_fetch_all_payments(
                count=10,
                skip=0
            )
        )

        state["tool_result"] = str(
            result
        )

    except Exception as e:

        print(
            f"[RAZORPAY ERROR] {e}"
        )

        state["tool_result"] = (
            f"Razorpay request failed: {e}"
        )

    return state


# ============================================================
# GENERAL NODE
# ============================================================

def general_node(state: AgentState):

    print(
        "\n[AGENT] General question"
    )

    state["tool_result"] = ""

    return state


# ============================================================
# ANSWER NODE
# ============================================================

def answer_node(state: AgentState):

    print(
        "\n[AGENT] Sending request to Gemini..."
    )

    question = state.get(
        "question",
        ""
    )

    tool = state.get(
        "tool",
        ""
    )

    tool_result = state.get(
        "tool_result",
        ""
    )

    memory_context = state.get(
        "memory_context",
        ""
    )

    chat_history = state.get(
        "chat_history",
        ""
    )

    # ========================================================
    # BUILD PROMPT
    # ========================================================

    prompt = f"""
You are an intelligent AI assistant.

Answer the user's question using the available information.

USER QUESTION:
{question}

SELECTED TOOL:
{tool}

TOOL RESULT:
{tool_result}

MEMORY:
{memory_context}

CHAT HISTORY:
{chat_history}

Instructions:

1. Answer clearly and naturally.
2. Do not invent information.
3. If the tool returned no records, clearly say that no records were found.
4. For Razorpay data, explain the result in a simple way.
5. Do not expose internal implementation details unless the user asks.
6. Keep the answer concise but useful.
"""

    try:

        answer = generate_answer(
            prompt
        )

        state["answer"] = str(
            answer
        )

        print(
            "[AGENT] Answer generated."
        )

    except Exception as e:

        print(
            f"[AGENT ERROR] {e}"
        )

        state["answer"] = (
            f"Sorry, I couldn't generate the answer: {e}"
        )

    return state


# ============================================================
# MEMORY SAVE NODE
# ============================================================

def memory_save_node(state: AgentState):

    print(
        "\n[AGENT] Saving useful information to memory..."
    )

    question = state.get(
        "question",
        ""
    )

    answer = state.get(
        "answer",
        ""
    )

    # --------------------------------------------------------
    # Save the conversation as memory
    # --------------------------------------------------------

    try:

        memory_text = (
            f"User: {question}\n"
            f"Assistant: {answer}"
        )

        mcp_memory_save(
            memory_text
        )

        print(
            "[AGENT] Memory saved."
        )

    except Exception as e:

        print(
            f"[MEMORY SAVE ERROR] {e}"
        )

    return state


# ============================================================
# ROUTING FUNCTION
# ============================================================

def route_after_router(
    state: AgentState
):

    tool = state.get(
        "tool",
        "general"
    )

    return tool


# ============================================================
# BUILD LANGGRAPH
# ============================================================

builder = StateGraph(
    AgentState
)


# ============================================================
# ADD NODES
# ============================================================

builder.add_node(
    "router",
    router_node
)

builder.add_node(
    "memory",
    memory_node
)

builder.add_node(
    "pdf",
    pdf_node
)

builder.add_node(
    "chat_history",
    chat_history_node
)

builder.add_node(
    "razorpay",
    razorpay_node
)

builder.add_node(
    "general",
    general_node
)

builder.add_node(
    "answer",
    answer_node
)

builder.add_node(
    "memory_save",
    memory_save_node
)


# ============================================================
# ENTRY
# ============================================================

builder.set_entry_point(
    "router"
)


# ============================================================
# ROUTER → TOOL
# ============================================================

builder.add_conditional_edges(

    "router",

    route_after_router,

    {

        "memory": "memory",

        "pdf": "pdf",

        "chat_history": "chat_history",

        "razorpay": "razorpay",

        "general": "general",

    }
)


# ============================================================
# TOOL → ANSWER
# ============================================================

builder.add_edge(
    "memory",
    "answer"
)

builder.add_edge(
    "pdf",
    "answer"
)

builder.add_edge(
    "chat_history",
    "answer"
)

builder.add_edge(
    "razorpay",
    "answer"
)

builder.add_edge(
    "general",
    "answer"
)


# ============================================================
# ANSWER → MEMORY SAVE
# ============================================================

builder.add_edge(
    "answer",
    "memory_save"
)


# ============================================================
# MEMORY SAVE → END
# ============================================================

builder.add_edge(
    "memory_save",
    END
)


# ============================================================
# COMPILE GRAPH
# ============================================================

graph = builder.compile()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "========================================"
    )

    print(
        "        UNIFIED AGENT TEST"
    )

    print(
        "========================================"
    )

    result = graph.invoke(
        {
            "question": "Show my Razorpay payments",
            "chat_history": "",
            "memory_context": "",
            "tool": "",
            "tool_result": "",
            "answer": "",
        }
    )

    print(
        "\nFINAL ANSWER:"
    )

    print(
        result.get(
            "answer",
            ""
        )
    )