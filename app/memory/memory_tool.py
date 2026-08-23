import json
from pathlib import Path


# ==========================================
# MEMORY FILE
# ==========================================

MEMORY_DIR = Path(__file__).resolve().parent
MEMORY_FILE = MEMORY_DIR / "memory.json"


# ==========================================
# LOAD MEMORY
# ==========================================

def load_memory():

    if not MEMORY_FILE.exists():
        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):

        return []


# ==========================================
# SAVE MEMORY
# ==========================================

def save_memory(memory):

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            memory,
            file,
            indent=4,
            ensure_ascii=False
        )


# ==========================================
# ADD MEMORY
# ==========================================

def add_memory(text):

    text = text.strip()

    if not text:
        return False

    memory = load_memory()

    # Prevent duplicate memories
    for item in memory:

        if item.get("text", "").lower() == text.lower():
            return False

    memory.append({
        "text": text
    })

    save_memory(memory)

    print("[MEMORY] Saved:", text)

    return True


# ==========================================
# GET ALL MEMORY
# ==========================================

def get_memory():

    return load_memory()


# ==========================================
# SEARCH MEMORY
# ==========================================

def search_memory(query):

    memory = load_memory()

    if not memory:
        return []

    query_words = [
        word.lower()
        for word in query.split()
        if len(word) > 2
    ]

    results = []

    for item in memory:

        text = item.get("text", "")
        text_lower = text.lower()

        score = 0

        for word in query_words:

            if word in text_lower:
                score += 1

        if score > 0:

            results.append({
                "text": text,
                "score": score
            })

    # Highest matching memories first
    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return [
        item["text"]
        for item in results
    ]


# ==========================================
# CLEAR MEMORY
# ==========================================

def clear_memory():

    save_memory([])

    print("[MEMORY] Cleared.")


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("================================")
    print("       MEMORY TOOL TEST")
    print("================================")

    print("\nMemory file:")
    print(MEMORY_FILE)

    print("\nSaving test memories...")

    add_memory(
        "User's name is Shreedhar."
    )

    add_memory(
        "User is building a RAG application."
    )

    print("\nStored memories:")

    for memory in get_memory():

        print("-", memory["text"])

    print("\nSearching memory:")

    results = search_memory("what is my name")

    for result in results:

        print("-", result)