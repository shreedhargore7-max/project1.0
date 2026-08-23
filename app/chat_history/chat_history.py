import json
from pathlib import Path
from datetime import datetime


# ============================================================
# CHAT HISTORY LOCATION
# ============================================================

CHAT_DIR = Path(__file__).resolve().parent

CHAT_FILE = CHAT_DIR / "chat_history.json"


# ============================================================
# LOAD ALL CHATS
# ============================================================

def load_chats():

    if not CHAT_FILE.exists():
        return []

    try:

        with open(
            CHAT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (
        json.JSONDecodeError,
        OSError
    ):

        return []


# ============================================================
# SAVE ALL CHATS
# ============================================================

def save_chats(chats):

    CHAT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        CHAT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chats,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# CREATE NEW CHAT
# ============================================================

def create_chat(title="New Chat"):

    chats = load_chats()

    now = datetime.now().isoformat()

    chat = {
        "id": datetime.now().strftime(
            "%Y%m%d%H%M%S%f"
        ),
        "title": title,
        "created_at": now,
        "updated_at": now,
        "messages": []
    }

    chats.append(chat)

    save_chats(chats)

    return chat


# ============================================================
# ADD MESSAGE
# ============================================================

def add_message(
    chat_id,
    role,
    content
):

    chats = load_chats()

    for chat in chats:

        if chat["id"] == chat_id:

            chat["messages"].append(
                {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
            )

            chat["updated_at"] = datetime.now().isoformat()

            # First user message becomes title
            if (
                role == "user"
                and chat["title"] == "New Chat"
            ):

                title = content.strip()

                if len(title) > 40:
                    title = title[:40] + "..."

                chat["title"] = title

            save_chats(chats)

            return True

    return False


# ============================================================
# GET CHAT
# ============================================================

def get_chat(chat_id):

    chats = load_chats()

    for chat in chats:

        if chat["id"] == chat_id:
            return chat

    return None


# ============================================================
# GET RECENT CHATS
# ============================================================

def get_recent_chats(limit=20):

    chats = load_chats()

    chats.sort(
        key=lambda x: x.get(
            "updated_at",
            ""
        ),
        reverse=True
    )

    return chats[:limit]


# ============================================================
# SEARCH OLD CHATS
# ============================================================

def search_chats(query, limit=5):

    chats = load_chats()

    query_words = [
        word.lower()
        for word in query.split()
        if len(word) > 2
    ]

    results = []

    for chat in chats:

        score = 0

        for message in chat.get(
            "messages",
            []
        ):

            content = message.get(
                "content",
                ""
            ).lower()

            for word in query_words:

                if word in content:
                    score += 1

        if score > 0:

            results.append(
                {
                    "chat": chat,
                    "score": score
                }
            )

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return [
        item["chat"]
        for item in results[:limit]
    ]


# ============================================================
# DELETE CHAT
# ============================================================

def delete_chat(chat_id):

    chats = load_chats()

    chats = [
        chat
        for chat in chats
        if chat["id"] != chat_id
    ]

    save_chats(chats)


# ============================================================
# CLEAR ALL CHATS
# ============================================================

def clear_all_chats():

    save_chats([])


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    chat = create_chat()

    add_message(
        chat["id"],
        "user",
        "Hello"
    )

    add_message(
        chat["id"],
        "assistant",
        "Hello! How can I help?"
    )

    print(
        json.dumps(
            chat,
            indent=4
        )
    )