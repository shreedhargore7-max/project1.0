# ============================================================
# UNIFIED AI AGENT
# ============================================================
#
# Handles:
#
# 1. General AI
# 2. Long-term Memory
# 3. PDF / RAG
# 4. Chat History
# 5. Razorpay MCP
#
# ============================================================

import re

from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.monitoring.logger import create_request_id, log_event


# ============================================================
# AI
# ============================================================

from app.chat.gemini_client import generate_answer


# ============================================================
# LOCAL MEMORY
# ============================================================

from app.memory.memory_tool import (
    memory_tool,
    add_memory,
)


# ============================================================
# PDF / RAG
# ============================================================

from app.rag.rag_tool import (
    search_pdf,
)


# ============================================================
# CHAT HISTORY
# ============================================================

from app.agent.mcp_tools import (
    mcp_chat_history_search,
)


# ============================================================
# RAZORPAY MCP
# ============================================================

from app.agent.mcp_tools import (

    mcp_razorpay_fetch_all_payments,
    mcp_razorpay_fetch_payment,

    mcp_razorpay_fetch_all_orders,
    mcp_razorpay_fetch_order,

    mcp_razorpay_fetch_all_refunds,
    mcp_razorpay_fetch_refund,

    mcp_razorpay_fetch_all_payment_links,

    mcp_razorpay_fetch_settlements,
    mcp_razorpay_fetch_settlement,

    mcp_razorpay_create_order,
    mcp_razorpay_create_payment_link,

    mcp_razorpay_update_order,
    mcp_razorpay_capture_payment,
)

# ============================================================
# REVENUE RECOVERY
# ============================================================

from app.revenue_recovery.agent_node import (
    revenue_recovery_node,
)


# ============================================================
# STATE
# ============================================================

class AgentState(TypedDict, total=False):

    question: str

    request_id: str

    chat_history: str

    memory_context: str

    tool: str

    tool_result: str
    last_tool_result: str

    answer: str

    confirmation_required: bool

    pending_action: str

    pending_args: dict

    previous_tool: str

    recovery_analysis: dict
    recovery_status: str
    recovery_payments: list


# ============================================================
# AMOUNT
# ============================================================

def extract_amount(question):

    patterns = [

        r"₹\s*([\d,]+(?:\.\d+)?)",

        r"([\d,]+(?:\.\d+)?)\s*"
        r"(?:rupees|rs\.?|inr)",

        r"(?:for|amount(?:\s+of)?)\s+"
        r"₹?\s*([\d,]+(?:\.\d+)?)",
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            question.lower()
        )

        if match:

            value = match.group(1)

            value = value.replace(
                ",",
                ""
            )

            try:

                amount = float(value)

                if amount.is_integer():

                    return int(amount)

                return amount

            except ValueError:

                pass


    return None


# ============================================================
# ORDER ID
# ============================================================

def extract_order_id(question):

    match = re.search(
        r"\border_[A-Za-z0-9]+\b",
        question
    )

    if match:

        return match.group(0)

    return None


# ============================================================
# PAYMENT ID
# ============================================================

def extract_payment_id(question):

    match = re.search(
        r"\bpay_[A-Za-z0-9]+\b",
        question
    )

    if match:

        return match.group(0)

    return None


# ============================================================
# REFUND ID
# ============================================================

def extract_refund_id(question):

    match = re.search(
        r"\brfnd_[A-Za-z0-9]+\b",
        question
    )

    if match:

        return match.group(0)

    return None


# ============================================================
# RECEIPT
# ============================================================

def extract_receipt(question):

    match = re.search(
        r"(?:receipt|receipt\s*(?:id|number)?)"
        r"[\s:=_-]*([A-Za-z0-9_-]+)",
        question,
        re.IGNORECASE
    )

    if match:

        return match.group(1)

    return None


# ============================================================
# DESCRIPTION
# ============================================================

def extract_description(question):

    if "for testing" in question.lower():

        return "Testing payment link"


    match = re.search(
        r"(?:description|described as)"
        r"\s*[:=]?\s*(.+)",
        question,
        re.IGNORECASE
    )

    if match:

        description = match.group(1).strip()

        if description:

            return description


    return "Testing payment link"


# ============================================================
# ROUTER
# ============================================================

def infer_previous_tool(state: AgentState):
    """Infer the previous tool from explicit state or recent chat history."""

    previous_tool = state.get("previous_tool", "")

    if previous_tool in {
        "memory",
        "pdf",
        "chat_history",
        "razorpay",
        "revenue_recovery",
        "general",
    }:
        return previous_tool

    history = state.get("chat_history", "") or ""
    h = history.lower()

    # Most specific signals first.
    if any(x in h for x in [
        "razorpay",
        "order",
        "payment",
        "refund",
        "settlement",
        "payment link",
        "pay_",
        "order_",
        "rfnd_",
    ]):
        return "razorpay"

    if any(x in h for x in [
        "pdf",
        "document",
        "according to the document",
        "according to pdf",
    ]):
        return "pdf"

    if any(x in h for x in [
        "my name",
        "what do you know about me",
        "what am i building",
        "remember",
        "memory",
    ]):
        return "memory"

    if any(x in h for x in [
        "previous conversation",
        "previous chat",
        "earlier conversation",
        "chat history",
        "what did we discuss",
    ]):
        return "chat_history"

    return ""


def is_contextual_follow_up(question: str) -> bool:
    q = question.lower().strip()

    follow_up_keywords = [
        "how many",
        "how much",
        "which one",
        "which is",
        "what is its",
        "what's its",
        "its amount",
        "its status",
        "its receipt",
        "the latest",
        "latest one",
        "first one",
        "last one",
        "that order",
        "that payment",
        "that refund",
        "those orders",
        "those payments",
        "those refunds",
        "show it",
        "show that",
        "tell me more",
        "what about it",
    ]

    return any(keyword in q for keyword in follow_up_keywords)


def router_node(state: AgentState):
    request_id = state.get("request_id") or create_request_id()
    state["request_id"] = request_id
    log_event(request_id, "REQUEST_STARTED", "Agent request started")

    question = state.get("question", "").strip()
    q = question.lower()

    print()
    print("========================================")
    print("        INTELLIGENT AGENT")
    print("========================================")
    print("[ROUTER] Question:", question)

    previous_tool = infer_previous_tool(state)
    last_tool_result = state.get("last_tool_result", "")

    # ========================================================
    # CONTEXT-AWARE FOLLOW-UP
    # ========================================================
    # Put this BEFORE normal keyword routing. A question such as
    # "how much?" contains no Razorpay keyword, so we use the
    # previous tool to keep the conversation on the same data source.

    if is_contextual_follow_up(question) and previous_tool:
        selected = previous_tool
        print("[ROUTER] Context follow-up detected.")
        print("[ROUTER] Previous tool:", previous_tool)

    # ========================================================
    # REVENUE RECOVERY
    # ========================================================
    elif any(
        keyword in q
        for keyword in [
            "revenue at risk",
            "revenue risk",
            "at risk revenue",
            "recover revenue",
            "revenue recovery",
            "recover payment",
            "recover payments",
            "failed payments",
            "payment recovery",
            "recover my revenue",
            "lost revenue",
            "revenue loss",
            "which payments are at risk",
            "which payment is at risk",
            "high risk payments",
            "high-risk payments",

            # Highest-priority recovery requests
            "recover the highest-priority payment",
            "recover the highest priority payment",
            "recover the top payment",
            "recover the most risky payment",
            "recover the highest risk payment",
        ]
    ):
        selected = "revenue_recovery"

    # ========================================================
    # RAZORPAY
    # ========================================================
    elif any(
        keyword in q
        for keyword in [
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
            "capture payment",
            "pay_",
            "order_",
            "rfnd_",
        ]
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
            "uploaded document",
            "uploaded pdf",
            "this document",
            "this pdf",
            "according to the document",
            "according to the pdf",
            "according to pdf",
            "what does the document say",
            "what does the pdf say",
            "what is mentioned in the document",
            "what is mentioned in the pdf",
            "what is written in the document",
            "what is written in the pdf",
            "summarize the document",
            "summarise the document",
            "summarize the pdf",
            "summarise the pdf",
            "explain the document",
            "explain the pdf",
            "from the document",
            "from the pdf",
            "in the document",
            "in the pdf",
        ]
    ):
        selected = "pdf"

    # ========================================================
    # MEMORY
    # ========================================================
    elif any(
        keyword in q
        for keyword in [
            "what is my name",
            "what's my name",
            "who am i",
            "what am i building",
            "what am i making",
            "what do you know about me",
            "what do you remember about me",
            "remember",
            "memory",
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

    else:
        selected = "general"

    print("[ROUTER] Selected:", selected)
    log_event(request_id, "ROUTER_SELECTED", selected)

    state["tool"] = selected
    return state


# ============================================================
# MEMORY NODE
# ============================================================

def memory_node(state: AgentState):

    question = state.get(
        "question",
        ""
    )


    request_id = state.get("request_id") or create_request_id()
    state["request_id"] = request_id
    log_event(request_id, "MEMORY_SEARCH_STARTED", "Local memory search")

    print(
        "[AGENT] Local memory search"
    )


    try:

        results = memory_tool(
            question
        )


        if results:

            result = "\n".join(
                str(x)
                for x in results
            )

        else:

            result = (
                "No relevant memories found."
            )


        state["memory_context"] = result

        state["tool_result"] = result
        log_event(request_id, "MEMORY_SEARCH_COMPLETED", "Memory search completed")


    except Exception as e:

        log_event(request_id, "ERROR", f"Memory search failed: {e}")
        print(
            "[MEMORY ERROR]",
            e
        )

        state["memory_context"] = ""

        state["tool_result"] = (
            "No relevant memories found."
        )


    return state


# ============================================================
# PDF NODE
# ============================================================

def pdf_node(state: AgentState):

    question = state.get(
        "question",
        ""
    )


    request_id = state.get("request_id") or create_request_id()
    state["request_id"] = request_id
    log_event(request_id, "PDF_SEARCH_STARTED", "PDF/RAG search")

    print(
        "[AGENT] PDF / RAG search"
    )


    try:

        result = search_pdf(
            question
        )


        state["tool_result"] = str(
            result
        )
        log_event(request_id, "PDF_SEARCH_COMPLETED", "PDF/RAG search completed")


    except Exception as e:

        print(
            "[PDF ERROR]",
            e
        )

        state["tool_result"] = (
            "No relevant PDF information found."
        )


    return state


# ============================================================
# CHAT HISTORY NODE
# ============================================================

def chat_history_node(state: AgentState):

    question = state.get(
        "question",
        ""
    )


    request_id = state.get("request_id") or create_request_id()
    state["request_id"] = request_id
    log_event(request_id, "CHAT_HISTORY_SEARCH_STARTED", "Chat history search")

    print(
        "[AGENT] Chat history search"
    )


    try:

        result = mcp_chat_history_search(
            question
        )


        state["tool_result"] = str(
            result
        )
        log_event(request_id, "CHAT_HISTORY_SEARCH_COMPLETED", "Chat history search completed")


    except Exception as e:

        log_event(request_id, "ERROR", f"Chat history search failed: {e}")
        print(
            "[CHAT HISTORY ERROR]",
            e
        )

        state["tool_result"] = (
            "No previous conversation found."
        )


    return state


# ============================================================
# RAZORPAY NODE
# ============================================================

def razorpay_node(state: AgentState):

    request_id = state.get("request_id") or create_request_id()
    state["request_id"] = request_id
    log_event(request_id, "RAZORPAY_NODE_STARTED", "Razorpay operation requested")

    question = state.get(
        "question",
        ""
    ).strip()

    q = question.lower()


    state["confirmation_required"] = False

    state["pending_action"] = ""

    state["pending_args"] = {}


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

        amount = extract_amount(
            question
        )


        if amount is None:

            state["tool_result"] = (
                "Please provide the payment-link amount."
            )

            return state


        description = extract_description(
            question
        )


        state["confirmation_required"] = True

        state["pending_action"] = (
            "create_payment_link"
        )

        state["pending_args"] = {

            "amount": amount,

            "currency": "INR",

            "description": description,
        }


        state["tool"] = (
            "razorpay.create_payment_link"
        )

        state["tool_result"] = (
            "CONFIRMATION_REQUIRED"
        )
        log_event(request_id, "RAZORPAY_CONFIRMATION_REQUIRED", state["pending_action"])

        return state


    # ========================================================
    # CREATE ORDER
    # ========================================================

    if (
        (
            "create" in q
            or "make" in q
            or "generate" in q
            or "add" in q
        )
        and "order" in q
    ):

        amount = extract_amount(
            question
        )

        receipt = extract_receipt(
            question
        )


        if amount is None:

            state["tool_result"] = (
                "Please provide the order amount."
            )

            return state


        if receipt is None:

            state["tool_result"] = (
                "Please provide the receipt."
            )

            return state


        state["confirmation_required"] = True

        state["pending_action"] = (
            "create_order"
        )

        state["pending_args"] = {

            "amount": amount,

            "currency": "INR",

            "receipt": receipt,
        }


        state["tool"] = (
            "razorpay.create_order"
        )

        state["tool_result"] = (
            "CONFIRMATION_REQUIRED"
        )

        return state


    # ========================================================
    # CAPTURE PAYMENT
    # ========================================================

    if (
        "capture" in q
        and "payment" in q
    ):

        payment_id = extract_payment_id(
            question
        )

        amount = extract_amount(
            question
        )


        if payment_id is None:

            state["tool_result"] = (
                "Please provide the payment ID."
            )

            return state


        if amount is None:

            state["tool_result"] = (
                "Please provide the capture amount."
            )

            return state


        state["confirmation_required"] = True

        state["pending_action"] = (
            "capture_payment"
        )

        state["pending_args"] = {

            "payment_id": payment_id,

            "amount": amount,

            "currency": "INR",
        }


        state["tool"] = (
            "razorpay.capture_payment"
        )

        state["tool_result"] = (
            "CONFIRMATION_REQUIRED"
        )

        return state


    # ========================================================
    # UPDATE ORDER
    # ========================================================

    if (
        "update" in q
        and "order" in q
    ):

        order_id = extract_order_id(
            question
        )


        if order_id is None:

            state["tool_result"] = (
                "Please provide the Razorpay order ID."
            )

            return state


        note = "test completed"


        match = re.search(
            r"note\s+(.+)$",
            question,
            re.IGNORECASE
        )


        if match:

            note = match.group(1).strip()


        state["confirmation_required"] = True

        state["pending_action"] = (
            "update_order"
        )

        state["pending_args"] = {

            "order_id": order_id,

            "notes": {
                "test": note
            },
        }


        state["tool"] = (
            "razorpay.update_order"
        )

        state["tool_result"] = (
            "CONFIRMATION_REQUIRED"
        )

        return state


    # ========================================================
    # SPECIFIC PAYMENT
    # ========================================================

    payment_id = extract_payment_id(
        question
    )


    if (
        payment_id
        and "capture" not in q
    ):

        try:

            result = mcp_razorpay_fetch_payment(
                payment_id
            )

            state["tool_result"] = str(
                result
            )

        except Exception as e:

            state["tool_result"] = (
                f"Razorpay payment fetch failed: {e}"
            )

        return state


    # ========================================================
    # SPECIFIC ORDER
    # ========================================================

    order_id = extract_order_id(
        question
    )


    if (
        order_id
        and "update" not in q
    ):

        try:

            result = mcp_razorpay_fetch_order(
                order_id
            )

            state["tool_result"] = str(
                result
            )

        except Exception as e:

            state["tool_result"] = (
                f"Razorpay order fetch failed: {e}"
            )

        return state


    # ========================================================
    # SPECIFIC REFUND
    # ========================================================

    refund_id = extract_refund_id(
        question
    )


    if refund_id:

        try:

            result = mcp_razorpay_fetch_refund(
                refund_id
            )

            state["tool_result"] = str(
                result
            )

        except Exception as e:

            state["tool_result"] = (
                f"Razorpay refund fetch failed: {e}"
            )

        return state


    # ========================================================
    # PAYMENT LINKS
    # ========================================================

    if "payment link" in q:

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

            state["tool_result"] = (
                f"Razorpay payment links failed: {e}"
            )

        return state


    # ========================================================
    # REFUNDS
    # ========================================================

    if "refund" in q:

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

            state["tool_result"] = (
                f"Razorpay refunds failed: {e}"
            )

        return state


    # ========================================================
    # SETTLEMENTS
    # ========================================================

    if "settlement" in q:

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

            state["tool_result"] = (
                f"Razorpay settlements failed: {e}"
            )

        return state


    # ========================================================
    # ORDERS
    # ========================================================

    if "order" in q:

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

            state["tool_result"] = (
                f"Razorpay orders failed: {e}"
            )

        return state


    # ========================================================
    # PAYMENTS
    # ========================================================

    if "payment" in q:

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

            state["tool_result"] = (
                f"Razorpay payments failed: {e}"
            )

        return state


    state["tool_result"] = (
        "I couldn't determine the Razorpay operation."
    )

    return state


# ============================================================
# GENERAL NODE
# ============================================================

def general_node(state: AgentState):

    print(
        "[AGENT] General AI question"
    )

    state["tool_result"] = ""

    return state


# ============================================================
# ANSWER NODE
# ============================================================

def answer_node(state: AgentState):

    request_id = state.get("request_id") or create_request_id()
    state["request_id"] = request_id
    log_event(request_id, "ANSWER_GENERATION_STARTED", "Generating final answer")

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
    # RAZORPAY CONFIRMATION
    # ========================================================

    if state.get(
        "confirmation_required",
        False
    ):

        action = state.get(
            "pending_action",
            ""
        )

        args = state.get(
            "pending_args",
            {}
        )


        if action == "create_order":

            state["answer"] = (
                "⚠️ **Razorpay confirmation required**\n\n"

                "**Action:** Create Razorpay Order\n\n"

                f"**Amount:** `{args.get('amount')}` "
                f"**Currency:** `{args.get('currency', 'INR')}`\n"

                f"**Receipt:** `{args.get('receipt')}`\n\n"

                "This operation can modify your Razorpay account.\n\n"

                "**Do you want to continue?**\n\n"

                "Type **YES** to execute or **NO** to cancel."
            )


        elif action == "create_payment_link":

            state["answer"] = (
                "⚠️ **Razorpay confirmation required**\n\n"

                "**Action:** Create Razorpay Payment Link\n\n"

                f"**Amount:** `{args.get('amount')}` "
                f"**Currency:** `{args.get('currency', 'INR')}`\n"

                f"**Description:** `{args.get('description')}`\n\n"

                "This operation can modify your Razorpay account.\n\n"

                "**Do you want to continue?**\n\n"

                "Type **YES** to execute or **NO** to cancel."
            )


        elif action == "update_order":

            state["answer"] = (
                "⚠️ **Razorpay confirmation required**\n\n"

                "**Action:** Update Razorpay Order\n\n"

                f"**Order ID:** `{args.get('order_id')}`\n"

                f"**Notes:** `{args.get('notes')}`\n\n"

                "This operation can modify your Razorpay account.\n\n"

                "**Do you want to continue?**\n\n"

                "Type **YES** to execute or **NO** to cancel."
            )


        elif action == "capture_payment":

            state["answer"] = (
                "⚠️ **Razorpay confirmation required**\n\n"

                "**Action:** Capture Razorpay Payment\n\n"

                f"**Payment ID:** `{args.get('payment_id')}`\n"

                f"**Amount:** `{args.get('amount')}` "
                f"**Currency:** `{args.get('currency', 'INR')}`\n\n"

                "This operation can modify your Razorpay account.\n\n"

                "**Do you want to continue?**\n\n"

                "Type **YES** to execute or **NO** to cancel."
            )


        return state


    # ========================================================
    # NORMAL AI
    # ========================================================

    prompt = f"""
You are an intelligent AI assistant.

Answer the user's question clearly and naturally.

USER QUESTION:
{question}

SELECTED TOOL:
{tool}

TOOL RESULT:
{tool_result}

LONG-TERM MEMORY:
{memory_context}

CHAT HISTORY:
{chat_history}

RULES:

1. Answer the user's actual question.

2. Use tool results when they are available.

3. Use memory only when it is relevant.

4. Use chat history only when it is relevant.

5. If there is no useful tool result, answer normally using your
   own knowledge.

6. Do not invent information.

7. Do not claim that a tool was used if it was not used.

8. For Razorpay information, only use the supplied Razorpay result.

9. If a Razorpay result contains zero records, clearly say that
   no records were found.

10. Keep the response natural and useful.

ANSWER:
"""


    try:

        answer = generate_answer(
            prompt
        )

        state["answer"] = str(
            answer
        )
        log_event(request_id, "ANSWER_GENERATED", "Final answer generated")


    except Exception as e:

        log_event(request_id, "ERROR", f"Answer generation failed: {e}")
        print(
            "[AGENT ERROR]",
            e
        )

        state["answer"] = (
            "Sorry, I couldn't generate the answer."
        )


    if tool_result:
        state["last_tool_result"] = tool_result

    return state


# ============================================================
# MEMORY SAVE NODE
# ============================================================

def memory_save_node(state: AgentState):

    request_id = state.get("request_id") or create_request_id()
    state["request_id"] = request_id

    question = state.get(
        "question",
        ""
    )

    answer = state.get(
        "answer",
        ""
    )


    # --------------------------------------------------------
    # NEVER SAVE RAZORPAY OPERATIONS
    # --------------------------------------------------------

    if state.get("tool") == "razorpay":

        print(
            "[MEMORY] Razorpay interaction not saved."
        )

        return state


    # --------------------------------------------------------
    # NEVER SAVE REVENUE-RECOVERY / FINANCIAL ANALYSIS
    # --------------------------------------------------------

    if state.get("tool") == "revenue_recovery":

        print(
            "[MEMORY] Revenue-recovery interaction not saved."
        )

        return state


    # --------------------------------------------------------
    # NEVER SAVE PDF ANSWERS
    # --------------------------------------------------------

    if state.get("tool") == "pdf":

        print(
            "[MEMORY] PDF interaction not saved."
        )

        return state


    # --------------------------------------------------------
    # NEVER SAVE CHAT HISTORY SEARCH
    # --------------------------------------------------------

    if state.get("tool") == "chat_history":

        print(
            "[MEMORY] Chat-history search not saved."
        )

        return state


    # --------------------------------------------------------
    # DON'T SAVE EMPTY ANSWERS
    # --------------------------------------------------------

    if not question or not answer:

        return state


    # --------------------------------------------------------
    # SAVE ONLY IMPORTANT PERSONAL INFORMATION
    # --------------------------------------------------------

    try:

        saved = add_memory(
            question
        )


        if saved:

            log_event(request_id, "MEMORY_SAVE_COMPLETED", "Important user information saved")
            print(
                "[MEMORY] Important user information saved."
            )

        else:

            print(
                "[MEMORY] Nothing important to save."
            )


    except Exception as e:

        log_event(request_id, "ERROR", f"Memory save failed: {e}")
        print(
            "[MEMORY SAVE ERROR]",
            e
        )


    return state


# ============================================================
# ROUTING
# ============================================================

def route_after_router(state):

    return state.get(
        "tool",
        "general"
    )


# ============================================================
# BUILD GRAPH
# ============================================================

builder = StateGraph(
    AgentState
)


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
    "revenue_recovery",
    revenue_recovery_node
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
# ROUTER
# ============================================================

builder.add_conditional_edges(

    "router",

    route_after_router,

    {

        "memory": "memory",

        "pdf": "pdf",

        "chat_history": "chat_history",

        "razorpay": "razorpay",

        "revenue_recovery": "revenue_recovery",

        "general": "general",
    }
)


# ============================================================
# TOOLS → ANSWER
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
    "revenue_recovery",
    "answer"
)

builder.add_edge(
    "general",
    "answer"
)


# ============================================================
# ANSWER → MEMORY
# ============================================================

builder.add_edge(
    "answer",
    "memory_save"
)


# ============================================================
# MEMORY → END
# ============================================================

builder.add_edge(
    "memory_save",
    END
)


# ============================================================
# COMPILE
# ============================================================

graph = builder.compile()


print(
    "[UNIFIED AGENT] Loaded successfully."
)


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "========================================"
    )

    print(
        "       UNIFIED AI AGENT"
    )

    print(
        "========================================"
    )

    print(
        "Type 'exit' to stop."
    )


    while True:

        question = input(
            "\nAsk a question: "
        )


        if question.lower().strip() == "exit":

            print(
                "\nGoodbye!"
            )

            break


        if not question.strip():

            continue


        result = graph.invoke(

            {

                "question": question,

                "chat_history": "",

                "memory_context": "",

                "tool": "",

                "tool_result": "",

                "answer": "",
            }
        )


        print()
        print(
            "ANSWER:"
        )

        print(
            result.get(
                "answer",
                ""
            )
        )