import os
import sys
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from google import genai


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_DIR / "app"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


# ============================================================
# IMPORT OUR TOOLS
# ============================================================

from agent.tools import (
    pdf_search_tool,
    web_search_tool,
    memory_search_tool,
    memory_save_tool,
)


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

print("API key loaded:", bool(API_KEY))

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )

print("API key length:", len(API_KEY))


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
    tool: str
    tool_result: str
    answer: str


# ============================================================
# TOOL SELECTION NODE
# ============================================================

def choose_tool_node(state: AgentState):

    question = state["question"]

    print("\nChoosing appropriate tool...")

    question_lower = question.lower()

    # --------------------------------------------------------
    # PDF QUESTIONS
    # --------------------------------------------------------

    pdf_keywords = [
        "pdf",
        "document",
        "in the file",
        "in the document",
        "mentioned in",
        "according to the document",
        "according to the pdf",
        "company mentioned",
        "what does the pdf say",
    ]

    if any(
        keyword in question_lower
        for keyword in pdf_keywords
    ):

        selected_tool = "pdf"

    # --------------------------------------------------------
    # WEB / CURRENT INFORMATION
    # --------------------------------------------------------

    elif any(
        keyword in question_lower
        for keyword in [
            "latest",
            "today",
            "current",
            "recent",
            "news",
            "live",
            "now",
            "stock price",
            "share price",
        ]
    ):

        selected_tool = "web"

    # --------------------------------------------------------
    # MEMORY
    # --------------------------------------------------------

    elif any(
        keyword in question_lower
        for keyword in [
            "remember",
            "memory",
            "what am i",
            "what am i researching",
            "my project",
            "what do you know about me",
            "what did i tell you",
        ]
    ):

        selected_tool = "memory"

    # --------------------------------------------------------
    # GENERAL GEMINI
    # --------------------------------------------------------

    else:

        selected_tool = "gemini"

    print("Selected tool:", selected_tool)

    return {
        "tool": selected_tool
    }


# ============================================================
# TOOL EXECUTION NODE
# ============================================================

def execute_tool_node(state: AgentState):

    question = state["question"]
    selected_tool = state["tool"]

    print("\nExecuting tool:", selected_tool)

    try:

        # ----------------------------------------------------
        # PDF
        # ----------------------------------------------------

        if selected_tool == "pdf":

            result = pdf_search_tool(question)

        # ----------------------------------------------------
        # WEB
        # ----------------------------------------------------

        elif selected_tool == "web":

            result = web_search_tool(question)

        # ----------------------------------------------------
        # MEMORY
        # ----------------------------------------------------

        elif selected_tool == "memory":

            result = memory_search_tool(question)

        # ----------------------------------------------------
        # GEMINI
        # ----------------------------------------------------

        else:

            result = "No external tool is required."

        return {
            "tool_result": result
        }

    except Exception as e:

        return {
            "tool_result": f"Tool error: {str(e)}"
        }


# ============================================================
# GEMINI NODE
# ============================================================

def llm_node(state: AgentState):

    question = state["question"]
    selected_tool = state["tool"]
    tool_result = state["tool_result"]

    print("\nSending information to Gemini...")

    # ========================================================
    # GENERAL QUESTION
    # ========================================================

    if selected_tool == "gemini":

        prompt = f"""
You are a helpful AI assistant.

Answer the user's question clearly and accurately.

User question:
{question}
"""

    # ========================================================
    # TOOL-BASED QUESTION
    # ========================================================

    else:

        prompt = f"""
You are an AI assistant using external tools.

The user asked:

{question}

The selected tool was:

{selected_tool}

The tool returned:

---------------- TOOL RESULT ----------------

{tool_result}

-------------- END TOOL RESULT --------------

Answer the user's question using the tool result.

Important rules:

1. Do not invent information.
2. If the tool result does not contain the answer, say so.
3. For PDF questions, use only the PDF information.
4. For web questions, summarize the search results.
5. For memory questions, use only the stored memories.
6. Give a clear and concise answer.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return {
        "answer": response.text
    }


# ============================================================
# CREATE LANGGRAPH
# ============================================================

builder = StateGraph(AgentState)


# Add nodes

builder.add_node(
    "choose_tool",
    choose_tool_node
)

builder.add_node(
    "execute_tool",
    execute_tool_node
)

builder.add_node(
    "llm",
    llm_node
)


# ============================================================
# GRAPH FLOW
# ============================================================

builder.add_edge(
    START,
    "choose_tool"
)

builder.add_edge(
    "choose_tool",
    "execute_tool"
)

builder.add_edge(
    "execute_tool",
    "llm"
)

builder.add_edge(
    "llm",
    END
)


# Compile graph

graph = builder.compile()


# ============================================================
# RUN AGENT
# ============================================================

if __name__ == "__main__":

    print("\n====================================")
    print("       LANGGRAPH AI AGENT")
    print("====================================")

    while True:

        question = input(
            "\nAsk a question "
            "(type 'exit' to quit): "
        )

        if question.lower().strip() == "exit":

            print("\nGoodbye!")

            break

        if not question.strip():

            print(
                "Please enter a question."
            )

            continue

        try:

            result = graph.invoke({

                "question": question,

                "tool": "",

                "tool_result": "",

                "answer": ""

            })

            print("\n====================================")
            print("              ANSWER")
            print("====================================")

            print(
                result["answer"]
            )

        except Exception as e:

            print("\nERROR:")
            print(e)