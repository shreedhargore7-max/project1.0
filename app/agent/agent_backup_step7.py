import os
import sys
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from google import genai
from google.genai import types


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]

APP_DIR = PROJECT_DIR / "app"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


# ============================================================
# IMPORT TOOLS
# ============================================================

from agent.tools import (
    pdf_search_tool,
    web_search_tool,
    memory_search_tool,
    memory_save_tool,
)

from memory.context_manager import build_context


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

ENV_FILE = PROJECT_DIR / ".env"

print("Loading .env from:")
print(ENV_FILE)

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)


# ============================================================
# GEMINI API KEY
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

print(
    "API key loaded:",
    bool(API_KEY)
)

if not API_KEY:

    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )

print(
    "API key length:",
    len(API_KEY)
)


# ============================================================
# GEMINI CLIENT
# ============================================================

client = genai.Client(
    api_key=API_KEY
)

MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# LANGGRAPH STATE
# ============================================================

class AgentState(TypedDict):

    question: str

    chat_history: str

    memory_context: str

    tool: str

    tool_result: str

    answer: str


# ============================================================
# GEMINI TOOL 1
# ============================================================

def search_pdf(question: str) -> str:
    """
    Search the uploaded PDF.

    Use this when the user asks about information
    contained in their PDF or document.
    """

    print("\n[AI TOOL] PDF SEARCH")

    try:

        result = pdf_search_tool(
            question
        )

        if not result:

            return (
                "No relevant information was "
                "found in the PDF."
            )

        return result

    except Exception as e:

        return (
            f"PDF search failed: {str(e)}"
        )


# ============================================================
# GEMINI TOOL 2
# ============================================================

def search_web(query: str) -> str:
    """
    Search the internet.

    Use this when current, recent, live,
    latest, news, or external information
    is required.
    """

    print("\n[AI TOOL] WEB SEARCH")

    try:

        result = web_search_tool(
            query
        )

        if not result:

            return (
                "No web search results were found."
            )

        return result

    except Exception as e:

        return (
            f"Web search failed: {str(e)}"
        )


# ============================================================
# GEMINI TOOL 3
# ============================================================

def search_long_term_memory(
    query: str
) -> str:
    """
    Search persistent user memory.

    Use this for information the user previously
    asked the assistant to remember or information
    stored for future conversations.
    """

    print(
        "\n[AI TOOL] LONG-TERM MEMORY SEARCH"
    )

    try:

        result = memory_search_tool(
            query
        )

        if not result:

            return (
                "No relevant long-term "
                "memories were found."
            )

        return result

    except Exception as e:

        return (
            f"Memory search failed: {str(e)}"
        )


# ============================================================
# GEMINI TOOL 4
# ============================================================

def save_long_term_memory(
    text: str
) -> str:
    """
    Save important information permanently.

    Use this when the user explicitly asks
    the assistant to remember something.
    """

    print(
        "\n[AI TOOL] SAVE LONG-TERM MEMORY"
    )

    try:

        result = memory_save_tool(
            text
        )

        return result

    except Exception as e:

        return (
            f"Memory save failed: {str(e)}"
        )


# ============================================================
# TOOL LIST
# ============================================================

AI_TOOLS = [

    search_pdf,

    search_web,

    search_long_term_memory,

    save_long_term_memory,

]


# ============================================================
# BUILD CONTEXT
# ============================================================

def context_node(
    state: AgentState
):

    question = state["question"]

    print(
        "\n[CONTEXT] Building context..."
    )

    try:

        context = build_context(
            question
        )

        print(
            "[CONTEXT] Context loaded."
        )

    except Exception as e:

        print(
            "[CONTEXT] Error:",
            e
        )

        context = ""

    return {

        "memory_context": context

    }


# ============================================================
# DIRECT MEMORY ANSWER
# ============================================================

def direct_memory_answer(
    question: str
):
    """
    Answer simple personal-memory questions
    without calling Gemini.

    This is useful when Gemini quota is exhausted.
    """

    question_lower = (
        question
        .lower()
        .strip()
    )

    # --------------------------------------------------------
    # Questions that are clearly memory questions
    # --------------------------------------------------------

    memory_questions = [

        "what is my name",

        "what's my name",

        "who am i",

        "what is my brother's name",

        "what's my brother's name",

        "what do you know about me",

    ]

    if not any(
        phrase in question_lower
        for phrase in memory_questions
    ):

        return None


    # --------------------------------------------------------
    # Search persistent memory
    # --------------------------------------------------------

    print(
        "\n[DIRECT MEMORY] Searching..."
    )

    try:

        result = memory_search_tool(
            question
        )

    except Exception as e:

        print(
            "[DIRECT MEMORY] Error:",
            e
        )

        return None


    # --------------------------------------------------------
    # No memory found
    # --------------------------------------------------------

    if not result:

        return None


    if (
        result
        == "No relevant memories were found."
    ):

        return None


    if (
        result
        == "No relevant long-term "
        "memories were found."
    ):

        return None


    # --------------------------------------------------------
    # Return memory result
    # --------------------------------------------------------

    return result


# ============================================================
# INTELLIGENT AGENT NODE
# ============================================================

def agent_node(
    state: AgentState
):

    question = state["question"]

    print()
    print(
        "========================================"
    )
    print(
        "        INTELLIGENT AGENT"
    )
    print(
        "========================================"
    )


    # ========================================================
    # DIRECT MEMORY
    # ========================================================

    direct_answer = direct_memory_answer(
        question
    )

    if direct_answer:

        print(
            "[AGENT] Answered directly from memory."
        )

        return {

            "answer": direct_answer

        }


    # ========================================================
    # GET CONTEXT
    # ========================================================

    memory_context = state.get(
        "memory_context",
        ""
    )

    chat_history = state.get(
        "chat_history",
        ""
    )


    # ========================================================
    # SYSTEM INSTRUCTION
    # ========================================================

    system_instruction = """

You are an intelligent personal AI assistant.

You are NOT a simple keyword-based chatbot.

You must understand the user's intention and decide
whether external tools are necessary.

You have four tools.

------------------------------------------------------------
TOOL 1: PDF SEARCH
------------------------------------------------------------

Search the user's uploaded PDF/document.

Use it when the answer should come from the user's
PDF or uploaded document.

------------------------------------------------------------
TOOL 2: WEB SEARCH
------------------------------------------------------------

Search the internet.

Use it when the user needs:

- latest information
- current information
- recent information
- news
- live information
- current technology information
- external information
- information that may have changed recently

------------------------------------------------------------
TOOL 3: LONG-TERM MEMORY SEARCH
------------------------------------------------------------

Search persistent information about the user.

Use it for:

- user's name
- user's preferences
- user's projects
- information the user asked you to remember
- personal facts
- information from previous sessions

------------------------------------------------------------
TOOL 4: SAVE LONG-TERM MEMORY
------------------------------------------------------------

Save information permanently.

Use this when the user explicitly says things like:

"remember this"

"save this"

"don't forget this"

"remember that..."

or gives important information that clearly
should persist between conversations.

------------------------------------------------------------
IMPORTANT
------------------------------------------------------------

Do NOT select tools using simple keyword matching.

Understand the meaning of the question.

You may use multiple tools when necessary.

For example:

"What is the latest Python version?"

Use WEB SEARCH.

"According to my PDF, what company is mentioned?"

Use PDF SEARCH.

"What is my name?"

Use LONG-TERM MEMORY SEARCH.

"Remember that I am building a RAG chatbot."

Use SAVE LONG-TERM MEMORY.

"What did we discuss about Python before?"

Use previous chat context and memory when useful.

"What did we discuss about Python and what is the latest
development in Python?"

This may require previous conversation context AND web search.

For normal questions that do not require external information,
answer directly.

Do not call tools unnecessarily.

When a tool returns information, use that information
to answer the user.

Never invent facts from a tool result.

If the tool cannot provide the requested information,
say that clearly.

Be conversational and intelligent.

Maintain continuity with previous conversations.
"""


    # ========================================================
    # PROMPT
    # ========================================================

    prompt = f"""

{system_instruction}

============================================================
LONG-TERM MEMORY AND PREVIOUS CHAT CONTEXT
============================================================

{memory_context}

============================================================
RECENT CHAT HISTORY
============================================================

{chat_history}

============================================================
CURRENT USER QUESTION
============================================================

{question}

============================================================

Think about what the user actually wants.

Decide whether a tool is required.

If a tool is required, use the appropriate tool.

You may use multiple tools if necessary.

Then provide the final answer naturally.
"""


    # ========================================================
    # GEMINI REQUEST
    # ========================================================

    print(
        "[AGENT] Sending request to Gemini..."
    )

    try:

        response = client.models.generate_content(

            model=MODEL_NAME,

            contents=prompt,

            config=types.GenerateContentConfig(

                tools=AI_TOOLS,

                temperature=0.2,

            ),

        )


        # ----------------------------------------------------
        # Get response
        # ----------------------------------------------------

        answer = response.text


        if not answer:

            answer = (
                "I could not generate an answer."
            )


        print(
            "[AGENT] Final answer generated."
        )


        return {

            "answer": answer

        }


    # ========================================================
    # QUOTA ERROR
    # ========================================================

    except Exception as e:

        error_text = str(e)


        if (
            "429" in error_text
            or
            "RESOURCE_EXHAUSTED"
            in error_text
        ):

            print(
                "[AGENT] Gemini quota exhausted."
            )


            return {

                "answer":
                "Gemini API quota is currently "
                "exhausted. Your memory, PDF, chat "
                "history, and web-search components "
                "are still available. Please retry "
                "after the Gemini quota resets."

            }


        # ----------------------------------------------------
        # Other error
        # ----------------------------------------------------

        print(
            "[AGENT] Gemini error:",
            e
        )


        return {

            "answer":
            f"Error while generating the answer: {e}"

        }


# ============================================================
# CREATE LANGGRAPH
# ============================================================

builder = StateGraph(
    AgentState
)


# ============================================================
# ADD NODES
# ============================================================

builder.add_node(
    "context",
    context_node
)

builder.add_node(
    "agent",
    agent_node
)


# ============================================================
# GRAPH FLOW
# ============================================================

builder.add_edge(
    START,
    "context"
)

builder.add_edge(
    "context",
    "agent"
)

builder.add_edge(
    "agent",
    END
)


# ============================================================
# COMPILE
# ============================================================

graph = builder.compile()


# ============================================================
# COMMAND LINE TEST
# ============================================================

if __name__ == "__main__":

    print()
    print(
        "========================================"
    )
    print(
        "       INTELLIGENT LANGGRAPH AGENT"
    )
    print(
        "========================================"
    )

    while True:

        question = input(
            "\nYou: "
        ).strip()


        # ----------------------------------------------------
        # EXIT
        # ----------------------------------------------------

        if question.lower() == "exit":

            print(
                "\nGoodbye!"
            )

            break


        # ----------------------------------------------------
        # EMPTY INPUT
        # ----------------------------------------------------

        if not question:

            print(
                "Please enter a question."
            )

            continue


        # ----------------------------------------------------
        # RUN GRAPH
        # ----------------------------------------------------

        try:

            result = graph.invoke({

                "question": question,

                "chat_history": "",

                "memory_context": "",

                "tool": "",

                "tool_result": "",

                "answer": "",

            })


            print()
            print(
                "========================================"
            )
            print(
                "                  AI"
            )
            print(
                "========================================"
            )

            print(
                result.get(
                    "answer",
                    "No answer generated."
                )
            )


        except Exception as e:

            print()
            print(
                "Agent error:",
                e
            )