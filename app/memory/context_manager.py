# app/memory/context_manager.py

from app.memory.memory_tool import search_memory
from app.chat_history.chat_history_tool import search_chats


# ============================================================
# BUILD CONTEXT
# ============================================================

def build_context(question: str) -> str:

    print("\n[CONTEXT] Building context...")

    # --------------------------------------------------------
    # LONG TERM MEMORY
    # --------------------------------------------------------

    try:

        memories = search_memory(question)

    except Exception as e:

        print("[CONTEXT] Memory error:", e)

        memories = []

    print("[CONTEXT] Long-term memory loaded.")

    # --------------------------------------------------------
    # PREVIOUS CHATS
    # --------------------------------------------------------

    try:

        chats = search_chats(question)

    except Exception as e:

        print("[CONTEXT] Chat history error:", e)

        chats = []

    print("[CONTEXT] Previous chats loaded.")

    # --------------------------------------------------------
    # FORMAT MEMORY
    # --------------------------------------------------------

    memory_text = ""

    if memories:

        memory_text = "\n".join(
            f"- {item}"
            for item in memories
        )

    else:

        memory_text = "No relevant long-term memories found."

    # --------------------------------------------------------
    # FORMAT CHATS
    # --------------------------------------------------------

    chat_text = ""

    if chats:

        chat_parts = []

        for chat in chats:

            title = chat.get(
                "title",
                "Untitled Chat"
            )

            chat_parts.append(
                f"CHAT: {title}"
            )

            for message in chat.get(
                "messages",
                []
            ):

                role = message.get(
                    "role",
                    ""
                )

                content = message.get(
                    "content",
                    ""
                )

                # Ignore previous Gemini quota errors
                if "429 RESOURCE_EXHAUSTED" in content:
                    continue

                chat_parts.append(
                    f"{role}: {content}"
                )

        chat_text = "\n".join(
            chat_parts
        )

    else:

        chat_text = "No relevant previous chats found."

    # --------------------------------------------------------
    # FINAL CONTEXT
    # --------------------------------------------------------

    context = (
        "LONG-TERM MEMORY:\n\n"
        f"{memory_text}\n\n"
        "====================\n\n"
        "RELEVANT PREVIOUS CHATS:\n\n"
        f"{chat_text}"
    )

    return context