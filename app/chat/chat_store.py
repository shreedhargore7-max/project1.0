import json
import uuid
from pathlib import Path
from datetime import datetime


# ==========================================
# CHAT STORAGE
# ==========================================

CHAT_DIR = Path(__file__).resolve().parent
CHAT_FILE = CHAT_DIR / "chats.json"


# ==========================================
# LOAD CHATS
# ==========================================

def load_chats():

    if not CHAT_FILE.exists():
        return []

    try:
        with open(CHAT_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


# ==========================================
# SAVE CHATS
# ==========================================

def save_chats(chats):

    CHAT_DIR.mkdir(parents=True, exist_ok=True)

    with open(CHAT_FILE, "w", encoding="utf-8") as file:

        json.dump(
            chats,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================
# CREATE CHAT
# ==========================================

def create_chat(title="New Chat"):

    chats = load_chats()

    chat = {
        "id": str(uuid.uuid4()),
        "title": title,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": []
    }

    chats.append(chat)

    save_chats(chats)

    return chat


# ==========================================
# GET CHAT
# ==========================================

def get_chat(chat_id):

    chats = load_chats()

    for chat in chats:

        if chat["id"] == chat_id:
            return chat

    return None


# ==========================================
# ADD MESSAGE
# ==========================================

def add_message(chat_id, role, content):

    chats = load_chats()

    for chat in chats:

        if chat["id"] == chat_id:

            chat["messages"].append({
                "role": role,
                "content": content
            })

            chat["updated_at"] = datetime.now().isoformat()

            # Use first user message as title
            if (
                chat["title"] == "New Chat"
                and role == "user"
            ):

                title = content.strip()

                if len(title) > 40:
                    title = title[:40] + "..."

                chat["title"] = title

            break

    save_chats(chats)


# ==========================================
# GET ALL CHATS
# ==========================================

def get_all_chats():

    chats = load_chats()

    # Newest first
    chats.sort(
        key=lambda x: x.get("updated_at", ""),
        reverse=True
    )

    return chats


# ==========================================
# DELETE CHAT
# ==========================================

def delete_chat(chat_id):

    chats = load_chats()

    chats = [
        chat
        for chat in chats
        if chat["id"] != chat_id
    ]

    save_chats(chats)


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    chat = create_chat()

    add_message(
        chat["id"],
        "user",
        "My name is Shreedhar."
    )

    add_message(
        chat["id"],
        "assistant",
        "Nice to meet you, Shreedhar!"
    )

    print("\nChats:")

    for item in get_all_chats():

        print(
            item["id"],
            item["title"]
        )

        for message in item["messages"]:

            print(
                message["role"],
                ":",
                message["content"]
            )