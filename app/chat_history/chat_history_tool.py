import json
from pathlib import Path


# ============================================================
# CHAT HISTORY STORAGE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data"

HISTORY_FILE = DATA_DIR / "chat_history.json"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# LOAD CHAT HISTORY
# ============================================================

def load_chat_history():

    if not HISTORY_FILE.exists():
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if isinstance(data, list):
            return data

        return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


# ============================================================
# SAVE CHAT
# ============================================================

def save_chat(
    user_message,
    assistant_message
):

    history = load_chat_history()

    conversation = {

        "user": str(
            user_message
        ),

        "assistant": str(
            assistant_message
        )
    }

    history.append(
        conversation
    )

    try:

        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                history,
                f,
                indent=2,
                ensure_ascii=False
            )

        print(
            "[CHAT HISTORY] Saved."
        )

        return True

    except OSError as e:

        print(
            f"[CHAT HISTORY ERROR] {e}"
        )

        return False


# ============================================================
# SEARCH CHAT HISTORY
# ============================================================

def search_chat_history(
    query,
    top_k=5
):

    history = load_chat_history()

    if not history:

        return []

    query_text = str(
        query
    ).lower().strip()

    if not query_text:
        return []

    stop_words = {

        "what",
        "is",
        "the",
        "a",
        "an",
        "we",
        "did",
        "do",
        "before",
        "about",
        "me",
        "our",
        "previous",
        "conversation",
        "conversations",
        "discuss",
        "discussed",
        "talk",
        "talked"
    }

    query_words = [

        word.strip(
            ".,?!"
        )

        for word in query_text.split()

        if word.strip(
            ".,?!"
        ) not in stop_words
    ]

    results = []

    for chat in history:

        user_text = str(
            chat.get(
                "user",
                ""
            )
        )

        assistant_text = str(
            chat.get(
                "assistant",
                ""
            )
        )

        combined = (
            user_text
            + " "
            + assistant_text
        )

        combined_lower = combined.lower()

        score = 0

        for word in query_words:

            if word in combined_lower:

                score += 1

        if query_text in combined_lower:

            score += 5

        if score > 0:

            results.append(
                {
                    "score": score,
                    "user": user_text,
                    "assistant": assistant_text
                }
            )

    # If user asks generally about previous conversations,
    # return latest conversations.
    if not results and (
        "before" in query_text
        or
        "previous" in query_text
        or
        "history" in query_text
    ):

        for chat in history[-top_k:]:

            results.append(
                {
                    "score": 1,
                    "user": str(
                        chat.get(
                            "user",
                            ""
                        )
                    ),
                    "assistant": str(
                        chat.get(
                            "assistant",
                            ""
                        )
                    )
                }
            )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    results = results[:top_k]

    formatted = []

    for item in results:

        formatted.append(

            "user: "
            + item["user"]
            + "\nassistant: "
            + item["assistant"]
        )

    return formatted


# ============================================================
# ALIAS
# ============================================================

save_chat_history = save_chat


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        load_chat_history()
    )