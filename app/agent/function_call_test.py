import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google import genai


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_DIR / "app"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


# ============================================================
# ENV
# ============================================================

load_dotenv(
    PROJECT_DIR / ".env",
    override=True
)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )


# ============================================================
# GEMINI
# ============================================================

client = genai.Client(
    api_key=API_KEY
)

MODEL_NAME = "gemini-3.6-flash"


# ============================================================
# TEST TOOLS
# ============================================================

def search_pdf(question: str) -> str:
    """
    Search the project PDF for information.
    Use this when the user asks about information
    contained inside the PDF.
    """

    print("\n[FUNCTION CALLED] search_pdf")
    print("Question:", question)

    return "PDF TOOL WAS CALLED SUCCESSFULLY."


def web_search(query: str) -> str:
    """
    Search the web for current or latest information.
    Use this for news, recent information, and live data.
    """

    print("\n[FUNCTION CALLED] web_search")
    print("Query:", query)

    return "WEB TOOL WAS CALLED SUCCESSFULLY."


def memory_search(query: str) -> str:
    """
    Search stored user/project memories.
    Use this when the user asks about previous
    information stored in memory.
    """

    print("\n[FUNCTION CALLED] memory_search")
    print("Query:", query)

    return "MEMORY TOOL WAS CALLED SUCCESSFULLY."


# ============================================================
# TOOLS
# ============================================================

tools = [
    search_pdf,
    web_search,
    memory_search,
]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("====================================")
    print("    GEMINI FUNCTION CALLING TEST")
    print("====================================")

    question = input(
        "\nAsk a question: "
    )

    print("\nSending question to Gemini...")

    from google.genai import types

    response = client.models.generate_content(
    model=MODEL_NAME,
    contents=question,
    config=types.GenerateContentConfig(
        tools=tools,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
          maximum_remote_calls=2
        )
    )
)

    print("\n====================================")
    print("              ANSWER")
    print("====================================")

    print(response.text)