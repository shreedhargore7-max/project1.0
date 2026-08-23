# ============================================================
# AGENT TOOLS
# ============================================================

# ------------------------------------------------------------
# MEMORY
# ------------------------------------------------------------

def memory_search_tool(query):
    """
    Search long-term memory for information relevant to the query.
    """

    print("\n[TOOL] MEMORY SEARCH")

    try:
        from app.memory.memory_tool import search_memory

        results = search_memory(query)

        if results is None:
            print("[MEMORY] No relevant memories found.")
            return []

        # Make sure the result is always a list
        if isinstance(results, str):
            results = [results]

        results = list(results)

        if not results:
            print("[MEMORY] No relevant memories found.")
            return []

        for item in results:
            print(f"- {item}")

        return results

    except Exception as e:

        print(f"[MEMORY ERROR] {e}")

        return []


# ------------------------------------------------------------
# SAVE MEMORY
# ------------------------------------------------------------

def memory_save_tool(text):
    """
    Save useful user information into long-term memory.
    """

    print("\n[TOOL] MEMORY SAVE")

    if not text or not str(text).strip():
        print("[MEMORY] Nothing to save.")
        return None

    try:
        from app.memory.memory_tool import save_memory

        result = save_memory(str(text).strip())

        print("[MEMORY] Saved successfully.")

        return result

    except ImportError as e:

        print(
            "[MEMORY SAVE ERROR] "
            "save_memory() was not found in app.memory.memory_tool"
        )

        print(f"[MEMORY SAVE ERROR] {e}")

        return None

    except Exception as e:

        print(f"[MEMORY SAVE ERROR] {e}")

        return None


# ------------------------------------------------------------
# PDF SEARCH
# ------------------------------------------------------------

def pdf_search_tool(query):
    """
    Search the indexed PDF/vector database for relevant chunks.
    """

    print("\n[TOOL] PDF SEARCH")

    try:

        # Your existing RAG search function
        from app.rag.rag_tool import search_pdf

        results = search_pdf(query)

        if results is None:
            print("[PDF] No relevant results found.")
            return []

        # ----------------------------------------------------
        # Handle different possible return formats
        # ----------------------------------------------------

        if isinstance(results, str):
            results = [results]

        elif isinstance(results, dict):

            # Chroma-style result
            if "documents" in results:

                documents = results["documents"]

                if documents and isinstance(documents[0], list):
                    documents = documents[0]

                results = documents

            else:
                results = [str(results)]

        else:

            results = list(results)

        if not results:

            print("[PDF] No relevant results found.")

            return []

        print(
            f"[PDF] Retrieved {len(results)} relevant chunks."
        )

        for i, item in enumerate(results, start=1):

            print(f"\n[PDF RESULT {i}]")
            print(item)

        return results

    except Exception as e:

        print(f"[PDF ERROR] {e}")

        return []


# ------------------------------------------------------------
# CHAT HISTORY SEARCH
# ------------------------------------------------------------

def chat_history_search_tool(query):
    """
    Search previous conversations for information relevant
    to the current question.
    """

    print("\n[TOOL] CHAT HISTORY SEARCH")

    try:

        from app.chat_history.chat_history_tool import (
            search_chat_history
        )

        results = search_chat_history(query)

        if results is None:

            print(
                "[CHAT HISTORY] "
                "No relevant previous chats found."
            )

            return []

        if isinstance(results, str):
            results = [results]

        results = list(results)

        if not results:

            print(
                "[CHAT HISTORY] "
                "No relevant previous chats found."
            )

            return []

        print(
            f"[CHAT HISTORY] "
            f"Found {len(results)} relevant conversations."
        )

        for item in results:

            print(item)

        return results

    except Exception as e:

        print(f"[CHAT HISTORY ERROR] {e}")

        return []


# ============================================================
# OPTIONAL: TOOL TESTS
# ============================================================

if __name__ == "__main__":

    print("========================================")
    print("           AGENT TOOLS TEST")
    print("========================================")

    print("\n1. Testing memory search...")

    memory_result = memory_search_tool(
        "what is my name"
    )

    print("\nMEMORY RESULT:")
    print(memory_result)

    print("\n2. Testing PDF search...")

    pdf_result = pdf_search_tool(
        "What does the PDF say about RAG?"
    )

    print("\nPDF RESULT:")
    print(pdf_result)

    print("\n3. Testing chat history search...")

    history_result = chat_history_search_tool(
        "what is my name"
    )

    print("\nCHAT HISTORY RESULT:")
    print(history_result)

    print("\n========================================")
    print("           TEST COMPLETED")
    print("========================================")