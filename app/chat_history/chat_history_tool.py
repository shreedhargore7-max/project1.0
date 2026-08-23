import json
from pathlib import Path


# ============================================================
# CHAT HISTORY STORAGE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
HISTORY_FILE = DATA_DIR / "chat_history.json"


# Make sure data folder exists
DATA_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD CHAT HISTORY
# ============================================================

def load_chat_history():
    """
    Load all saved conversations.
    """

    if not HISTORY_FILE.exists():
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


# ============================================================
# SAVE CHAT
# ============================================================

def save_chat(user_message, assistant_message):
    """
    Save one user/assistant conversation.
    """

    history = load_chat_history()

    conversation = {
        "user": str(user_message),
        "assistant": str(assistant_message)
    }

    history.append(conversation)

    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(
                history,
                f,
                indent=2,
                ensure_ascii=False
            )

        print("[CHAT HISTORY] Saved successfully.")
        return True

    except OSError as e:
        print(f"[CHAT HISTORY ERROR] {e}")
        return False


# ============================================================
# SEARCH CHAT HISTORY
# ============================================================

def search_chat_history(query, top_k=5):
    """
    Search previous conversations using simple keyword matching.

    This does NOT call Gemini.
    """

    history = load_chat_history()

    if not history:
        print("[CHAT HISTORY] No previous chats found.")
        return []

    query_words = set(
        word.lower()
        for word in str(query).split()
        if len(word.strip()) > 1
    )

    results = []

    for chat in history:

        user_text = str(chat.get("user", ""))
        assistant_text = str(chat.get("assistant", ""))

        combined = f"{user_text} {assistant_text}"

        combined_words = set(
            word.lower()
            for word in combined.split()
        )

        score = len(query_words.intersection(combined_words))

        # Also allow substring matching
        query_lower = str(query).lower()

        if query_lower in combined.lower():
            score += 3

        if score > 0:
            results.append(
                {
                    "score": score,
                    "user": user_text,
                    "assistant": assistant_text
                }
            )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    results = results[:top_k]

    if not results:
        print("[CHAT HISTORY] No relevant previous chats found.")
        return []

    formatted = []

    for item in results:
        formatted.append(
            f"user: {item['user']}\n"
            f"assistant: {item['assistant']}"
        )

    print(
        f"[CHAT HISTORY] Found {len(formatted)} relevant conversations."
    )

    return formatted


# ============================================================
# ALIAS
# ============================================================

# Some older agent code may use this name.
save_chat_history = save_chat


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("Chat history file:")
    print(HISTORY_FILE)

    print("\nCurrent history:")
    print(load_chat_history())