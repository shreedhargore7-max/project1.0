import pytest

from app.agent.unified_agent import (
    graph,
)


# ============================================================
# HELPER
# ============================================================

def run_agent(question, previous_tool="", last_tool_result=""):
    state = {
        "question": question,
        "chat_history": "",
        "memory_context": "",
        "tool": "",
        "tool_result": "",
        "last_tool_result": last_tool_result,
        "answer": "",
        "confirmation_required": False,
        "pending_action": "",
        "pending_args": {},
    }

    if previous_tool:
        state["previous_tool"] = previous_tool

    return graph.invoke(state)


# ============================================================
# GENERAL AI TEST
# ============================================================

def test_general_question():

    result = run_agent(
        "What is machine learning?"
    )

    assert result is not None

    assert result.get("tool") == "general"

    assert result.get("answer")


# ============================================================
# PDF ROUTING TEST
# ============================================================

def test_pdf_question():

    result = run_agent(
        "What does the PDF say about RAG?"
    )

    assert result is not None

    assert result.get("tool") == "pdf"


# ============================================================
# RAZORPAY READ TEST
# ============================================================

def test_razorpay_orders():

    result = run_agent(
        "Show my Razorpay orders"
    )

    assert result is not None

    assert result.get("tool") == "razorpay"

    assert (
        result.get("tool_result")
        or result.get("last_tool_result")
    )


# ============================================================
# CONTEXT FOLLOW-UP TEST
# ============================================================

def test_razorpay_follow_up():

    previous_result = (
        "6 Razorpay orders were found."
    )

    result = run_agent(
        "How many are there?",
        previous_tool="razorpay",
        last_tool_result=previous_result,
    )

    assert result is not None

    assert result.get("tool") == "razorpay"


# ============================================================
# HIGHEST AMOUNT FOLLOW-UP
# ============================================================

def test_highest_amount_follow_up():

    previous_result = """
    Razorpay orders:

    TEST_008 - ₹200
    TEST_007 - ₹200
    TEST_006 - ₹200
    TEST_005 - ₹150
    TEST_004 - ₹100
    TEST_ORDER_001 - ₹100
    """

    result = run_agent(
        "Which one has the highest amount?",
        previous_tool="razorpay",
        last_tool_result=previous_result,
    )

    assert result is not None

    assert result.get("tool") == "razorpay"


# ============================================================
# RAZORPAY CREATE ORDER TEST
# ============================================================

def test_create_razorpay_order_requires_confirmation():

    result = run_agent(
        "Create a Razorpay order for 200 rupees "
        "with receipt TEST_AUTOMATED"
    )

    assert result is not None

    assert result.get("tool") == "razorpay.create_order"

    assert (
        result.get("confirmation_required")
        is True
    )

    assert (
        result.get("pending_action")
        == "create_order"
    )

    pending_args = result.get(
        "pending_args",
        {}
    )

    assert pending_args.get(
        "amount"
    ) == 200

    assert pending_args.get(
        "currency"
    ) == "INR"

    assert pending_args.get(
        "receipt"
    ) == "TEST_AUTOMATED"


# ============================================================
# MEMORY ROUTING TEST
# ============================================================

def test_memory_question():

    result = run_agent(
        "What do you remember about me?"
    )

    assert result is not None

    assert result.get("tool") == "memory"


# ============================================================
# CHAT HISTORY ROUTING TEST
# ============================================================

def test_chat_history_question():

    result = run_agent(
        "What did we discuss earlier?"
    )

    assert result is not None

    assert result.get(
        "tool"
    ) == "chat_history"


# ============================================================
# UNKNOWN / GENERAL QUESTION
# ============================================================

def test_unknown_question_goes_general():

    result = run_agent(
        "Explain neural networks"
    )

    assert result is not None

    assert result.get("tool") == "general"


# ============================================================
# ANSWER GENERATION TEST
# ============================================================

def test_answer_is_generated():

    result = run_agent(
        "What is artificial intelligence?"
    )

    assert result is not None

    assert result.get("answer")

    assert len(
        result.get("answer", "")
    ) > 0


# ============================================================
# BASIC STATE TEST
# ============================================================

def test_agent_returns_state():

    result = run_agent(
        "Hello"
    )

    assert isinstance(
        result,
        dict
    )

    assert "tool" in result

    assert "answer" in result