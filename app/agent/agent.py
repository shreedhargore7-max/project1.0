from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.agent.mcp_tools import (
    mcp_memory_search,
    mcp_memory_save,
    mcp_pdf_search,
    mcp_chat_history_search,
)

from app.chat.gemini_client import generate_answer
from app.chat_history.chat_history_tool import save_chat


# ============================================================
# STATE
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

    question = state.get("question", "").strip()

    print("\n========================================")
    print("        INTELLIGENT AGENT")
    print("========================================")

    print("\n[ROUTER] Question:")
    print(question)

    q = question.lower()

    # --------------------------------------------------------
    # MEMORY QUESTIONS
    # --------------------------------------------------------

    memory_keywords = [
        "my name",
        "my brother",
        "my favorite",
        "my favourite",
        "what do i like",
        "what is my",
        "what's my",
        "do you remember",
        "remember that",
        "i told you",
        "i said",
    ]

    # --------------------------------------------------------
    # PDF QUESTIONS
    # --------------------------------------------------------

    pdf_keywords = [
        "pdf",
        "document",
        "according to the document",
        "according to the pdf",
        "in the document",
        "in the pdf",
        "what does the pdf",
        "what does the document",
    ]

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    history_keywords = [
        "previous conversation",
        "previous chat",
        "earlier conversation",
        "earlier chat",
        "what did we discuss",
        "what did i tell you",
        "last conversation",
        "last chat",
    ]

    if any(keyword in q for keyword in memory_keywords):

        tool = "memory"

    elif any(keyword in q for keyword in pdf_keywords):

        tool = "pdf"

    elif any(keyword in q for keyword in history_keywords):

        tool = "chat_history"

    else:

        tool = "general"

    print(f"[ROUTER] Selected tool: {tool}")

    return {
        "tool": tool
    }


# ============================================================
# MEMORY NODE
# ============================================================

def memory_node(state: AgentState):

    question = state["question"]

    print("\n[AGENT] Executing MEMORY tool")

    result = mcp_memory_search(question)

    if result:

        print("\n[MEMORY RESULT]")
        print(result)

    else:

        result = "No relevant memories found."

        print("[MEMORY] No relevant memories found.")

    return {
        "tool_result": result,
        "memory_context": result,
    }


# ============================================================
# PDF NODE
# ============================================================

def pdf_node(state: AgentState):

    question = state["question"]

    print("\n[AGENT] Executing PDF tool")

    result = mcp_pdf_search(question)

    if not result:

        result = "No relevant information was found in the PDF."

    print("\n[PDF RESULT]")
    print(result)

    return {
        "tool_result": result
    }


# ============================================================
# CHAT HISTORY NODE
# ============================================================

def chat_history_node(state: AgentState):

    question = state["question"]

    print("\n[AGENT] Executing CHAT HISTORY tool")

    result = mcp_chat_history_search(question)

    if not result:

        result = "No relevant previous conversation was found."

    print("\n[CHAT HISTORY RESULT]")
    print(result)

    return {
        "tool_result": result
    }


# ============================================================
# GENERAL GEMINI NODE
# ============================================================

def general_node(state: AgentState):

    question = state["question"]

    chat_history = state.get("chat_history", "")

    print("\n[AGENT] General question")
    print("[AGENT] Sending request to Gemini...")

    prompt = f"""
You are a helpful AI assistant.

Answer the user's question naturally and conversationally.

User question:
{question}

Previous conversation:
{chat_history}

Do not mention internal tools, memory systems, RAG, MCP, routing,
or implementation details unless the user explicitly asks about them.

Give a useful answer even if the question is simple.
"""

    try:

        answer = generate_answer(prompt)

    except Exception as e:

        print(f"[AGENT] Gemini error: {e}")

        answer = "I couldn't generate an answer right now."

    return {
        "answer": answer
    }


# ============================================================
# TOOL RESULT → ANSWER
# ============================================================

def tool_answer_node(state: AgentState):

    question = state["question"]

    tool = state.get("tool", "")

    result = state.get("tool_result", "")

    print("\n[AGENT] Processing tool result")

    if not result:

        return {
            "answer": "I couldn't find relevant information."
        }

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    if tool == "memory":

        answer = result.strip()

        # Don't expose internal formatting.
        if answer.startswith("[") and answer.endswith("]"):
            answer = answer.strip("[]")

        return {
            "answer": answer
        }

    # --------------------------------------------------------
    # PDF
    # --------------------------------------------------------

    if tool == "pdf":

        prompt = f"""
Answer the user's question using ONLY the information retrieved
from the PDF.

User question:
{question}

Retrieved PDF information:
{result}

Give a concise, natural answer.

Do not mention MCP.
Do not mention the routing system.
Do not say "the tool returned".
"""

        try:

            answer = generate_answer(prompt)

        except Exception:

            answer = result

        return {
            "answer": answer
        }

    # --------------------------------------------------------
    # CHAT HISTORY
    # --------------------------------------------------------

    if tool == "chat_history":

        prompt = f"""
Answer the user's question using the previous conversation below.

User question:
{question}

Previous conversation:
{result}

Answer naturally.

Do not mention MCP or internal tools.
"""

        try:

            answer = generate_answer(prompt)

        except Exception:

            answer = result

        return {
            "answer": answer
        }

    return {
        "answer": result
    }


# ============================================================
# MEMORY SAVE
# ============================================================

def memory_save_node(state: AgentState):

    question = state.get("question", "")
    answer = state.get("answer", "")

    if not answer:

        return {}

    # Don't save obvious temporary/general questions.
    if len(answer.strip()) < 3:

        return {}

    print("\n[AGENT] Saving useful information to memory...")

    try:

        mcp_memory_save(answer)

        print("[AGENT] Memory saved.")

    except Exception as e:

        print(f"[AGENT] Memory save skipped: {e}")

    return {}


# ============================================================
# CHAT HISTORY SAVE
# ============================================================

def save_conversation_node(state: AgentState):

    question = state.get("question", "")
    answer = state.get("answer", "")

    print("\n[AGENT] Saving conversation...")

    try:

        save_chat(
            question,
            answer
        )

        print("[AGENT] Conversation saved.")

    except Exception as e:

        print(f"[AGENT] Conversation save failed: {e}")

    return {}


# ============================================================
# ROUTING FUNCTION
# ============================================================

def route_after_router(state: AgentState):

    tool = state.get("tool", "general")

    if tool == "memory":

        return "memory"

    if tool == "pdf":

        return "pdf"

    if tool == "chat_history":

        return "chat_history"

    return "general"


# ============================================================
# BUILD GRAPH
# ============================================================

builder = StateGraph(AgentState)


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
    "general",
    general_node
)

builder.add_node(
    "tool_answer",
    tool_answer_node
)

builder.add_node(
    "memory_save",
    memory_save_node
)

builder.add_node(
    "save_conversation",
    save_conversation_node
)


# ============================================================
# EDGES
# ============================================================

builder.set_entry_point("router")


builder.add_conditional_edges(
    "router",
    route_after_router,
    {
        "memory": "memory",
        "pdf": "pdf",
        "chat_history": "chat_history",
        "general": "general",
    }
)


builder.add_edge(
    "memory",
    "tool_answer"
)

builder.add_edge(
    "pdf",
    "tool_answer"
)

builder.add_edge(
    "chat_history",
    "tool_answer"
)


builder.add_edge(
    "general",
    "memory_save"
)

builder.add_edge(
    "tool_answer",
    "memory_save"
)

builder.add_edge(
    "memory_save",
    "save_conversation"
)

builder.add_edge(
    "save_conversation",
    END
)


# ============================================================
# COMPILE
# ============================================================

graph = builder.compile()