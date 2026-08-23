import json
from pathlib import Path


# ============================================================
# MEMORY FILE
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]
MEMORY_FILE = BASE_DIR / "memory.json"


# ============================================================
# LOAD MEMORY
# ============================================================

def load_memory():
    """
    Load all long-term memories from memory.json.
    """

    if not MEMORY_FILE.exists():
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        return []

    except (json.JSONDecodeError, OSError):
        return []


# ============================================================
# SAVE MEMORY
# ============================================================

def save_memory(memory):
    """
    Save a memory to memory.json.

    Avoids saving duplicate memories.
    """

    memory = str(memory).strip()

    if not memory:
        return False

    memories = load_memory()

    if memory not in memories:
        memories.append(memory)

    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(
                memories,
                f,
                indent=2,
                ensure_ascii=False
            )

        return True

    except OSError as e:
        print(f"[MEMORY ERROR] {e}")
        return False


# ============================================================
# SEARCH MEMORY
# ============================================================

def search_memory(query, top_k=5):
    """
    Search long-term memory using simple keyword matching.

    This intentionally does NOT require Gemini.
    """

    memories = load_memory()

    if not memories:
        return []

    query = str(query).lower().strip()

    if not query:
        return []

    # --------------------------------------------------------
    # Extract useful words
    # --------------------------------------------------------

    stop_words = {
        "what",
        "is",
        "my",
        "the",
        "a",
        "an",
        "who",
        "are",
        "was",
        "were",
        "do",
        "does",
        "did",
        "tell",
        "me",
        "about",
        "name",
        "please",
        "you",
        "your",
        "i",
        "am",
        "in",
        "of",
        "to",
        "and",
        "just"
    }

    words = [
        word.strip(".,?!")
        for word in query.split()
        if word.strip(".,?!") not in stop_words
    ]

    # --------------------------------------------------------
    # Special handling for name questions
    # --------------------------------------------------------

    if "brother" in query:
        words.append("brother")

    if "favorite" in query:
        words.append("favorite")

    if "programming" in query:
        words.append("programming")

    if "language" in query:
        words.append("language")

    # --------------------------------------------------------
    # Score memories
    # --------------------------------------------------------

    scored = []

    for memory in memories:

        memory_text = str(memory)
        memory_lower = memory_text.lower()

        score = 0

        for word in words:
            if word and word in memory_lower:
                score += 1

        # Direct phrase matching
        if query in memory_lower:
            score += 5

        # Important semantic keywords
        if "brother" in query and "brother" in memory_lower:
            score += 5

        if "name" in query and "name" in memory_lower:
            score += 3

        if "programming language" in query:
            if "programming" in memory_lower or "language" in memory_lower:
                score += 5

        if score > 0:
            scored.append((score, memory_text))

    # --------------------------------------------------------
    # Sort by relevance
    # --------------------------------------------------------

    scored.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        memory
        for score, memory in scored[:top_k]
    ]


# ============================================================
# DEBUG
# ============================================================

if __name__ == "__main__":

    print("Memory file:")
    print(MEMORY_FILE)

    print("\nCurrent memories:")

    memories = load_memory()

    for memory in memories:
        print("-", memory)

    print("\nSearch test:")

    print(
        search_memory(
            "What is my brother name?"
        )
    )