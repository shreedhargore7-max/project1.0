import os
import sys
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from google import genai


# ==========================================
# PROJECT / APP PATH
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_DIR / "app"

# Add PROJECT directory to Python path
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# Add APP directory to Python path
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


# ==========================================
# IMPORT RAG
# ==========================================

from rag.rag_tool import search_pdf


# ==========================================
# LOAD .ENV
# ==========================================

ENV_FILE = PROJECT_DIR / ".env"

print("Loading .env from:")
print(ENV_FILE)

load_dotenv(
    dotenv_path=ENV_FILE,
    override=True
)


# ==========================================
# GEMINI API KEY
# ==========================================

API_KEY = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(API_KEY))

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY was not found in .env"
    )

print("API key length:", len(API_KEY))


# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=API_KEY
)

MODEL_NAME = "gemini-3.6-flash"


# ==========================================
# LANGGRAPH STATE
# ==========================================

class AgentState(TypedDict):
    question: str
    context: str
    answer: str


# ==========================================
# RAG NODE
# ==========================================

def rag_node(state: AgentState):

    question = state["question"]

    print("\nSearching PDF using RAG...")

    results = search_pdf(question, top_k=3)

    print(
        f"Retrieved {len(results)} relevant PDF chunks."
    )

    context = "\n\n".join(results)

    return {
        "context": context
    }


# ==========================================
# GEMINI NODE
# ==========================================

def llm_node(state: AgentState):

    question = state["question"]
    context = state["context"]

    print("\nSending PDF context to Gemini...")

    prompt = f"""
You are a helpful assistant answering questions about a PDF.

Answer the user's question using ONLY the information
provided in the PDF context.

If the answer cannot be found in the PDF context, say:

"I could not find this information in the PDF."

Do not invent information.

---------------- PDF CONTEXT ----------------

{context}

-------------- END PDF CONTEXT --------------

USER QUESTION:
{question}

ANSWER:
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return {
        "answer": response.text
    }


# ==========================================
# CREATE LANGGRAPH
# ==========================================

builder = StateGraph(AgentState)


builder.add_node(
    "rag",
    rag_node
)

builder.add_node(
    "llm",
    llm_node
)


# ==========================================
# GRAPH FLOW
# ==========================================

builder.add_edge(
    START,
    "rag"
)

builder.add_edge(
    "rag",
    "llm"
)

builder.add_edge(
    "llm",
    END
)


graph = builder.compile()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    print("\n====================================")
    print("       LANGGRAPH RAG AGENT")
    print("====================================")

    question = input(
        "\nAsk a question about the PDF: "
    )

    if not question.strip():
        print("Please enter a question.")
        sys.exit()

    try:

        result = graph.invoke({
            "question": question,
            "context": "",
            "answer": ""
        })

        print("\n====================================")
        print("              ANSWER")
        print("====================================")

        print(result["answer"])

    except Exception as e:

        print("\n====================================")
        print("               ERROR")
        print("====================================")

        print(e)