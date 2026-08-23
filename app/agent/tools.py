"""
Tools for the LangGraph AI Agent.

This file connects:
1. PDF RAG
2. Web Search
3. Memory
"""




import sys
from pathlib import Path


# ==========================================
# ADD APP DIRECTORY TO PYTHON PATH
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parents[2]
APP_DIR = PROJECT_DIR / "app"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


# ==========================================
# IMPORT PROJECT TOOLS
# ==========================================

from rag.rag_tool import search_pdf
from live_data.live_tool import web_search
from memory.memory_tool import add_memory, search_memory


# ==========================================
# PDF RAG TOOL
# ==========================================

def pdf_search_tool(question: str) -> str:
    """
    Search the PDF and return relevant information.
    """

    print("\n[TOOL] PDF RAG")

    documents = search_pdf(
        question,
        top_k=3
    )

    if not documents:
        return "No relevant information was found in the PDF."

    context = "\n\n".join(documents)

    return context


# ==========================================
# WEB SEARCH TOOL
# ==========================================

def web_search_tool(query: str) -> str:
    """
    Search the internet using DuckDuckGo.
    """

    print("\n[TOOL] WEB SEARCH")

    results = web_search(
        query,
        max_results=5
    )

    if not results:
        return "No web search results were found."

    output = []

    for i, result in enumerate(results, start=1):

        output.append(
            f"""
Result {i}

Title: {result.get("title")}

URL: {result.get("url")}

Snippet: {result.get("snippet")}
"""
        )

    return "\n".join(output)


# ==========================================
# MEMORY SEARCH TOOL
# ==========================================

def memory_search_tool(query: str) -> str:
    """
    Search stored user memories.
    """

    print("\n[TOOL] MEMORY SEARCH")

    results = search_memory(query)

    if not results:
        return "No relevant memories were found."

    return "\n".join(
        f"- {memory}"
        for memory in results
    )


# ==========================================
# SAVE MEMORY TOOL
# ==========================================

def memory_save_tool(text: str) -> str:
    """
    Save information to memory.
    """

    print("\n[TOOL] SAVE MEMORY")

    add_memory(text)

    return "Memory saved successfully."


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("====================================")
    print("          AGENT TOOLS TEST")
    print("====================================")

    print("\nTesting PDF tool...")

    try:
        result = pdf_search_tool(
            "What company is mentioned in the PDF?"
        )

        print("\nPDF TOOL RESULT:")
        print(result[:500])

    except Exception as e:
        print("PDF tool error:", e)

    print("\nTesting memory tool...")

    try:
        result = memory_search_tool(
            "Sri Lotus Developers"
        )

        print("\nMEMORY TOOL RESULT:")
        print(result)

    except Exception as e:
        print("Memory tool error:", e)

    print("\nTesting web tool...")

    try:
        result = web_search_tool(
            "Sri Lotus Developers latest news"
        )

        print("\nWEB TOOL RESULT:")
        print(result[:1000])

    except Exception as e:
        print("Web tool error:", e)

    print("\n====================================")
    print("             TEST COMPLETE")
    print("====================================")