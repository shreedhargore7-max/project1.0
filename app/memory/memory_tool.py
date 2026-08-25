# ============================================================
# MEMORY TOOL
# ============================================================

import json
import re
from pathlib import Path


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MEMORY_FILE = BASE_DIR / "memory.json"


# ============================================================
# LOAD MEMORY
# ============================================================

def load_memory():

    if not MEMORY_FILE.exists():
        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if isinstance(data, list):
            return data

        return []

    except Exception as e:

        print(
            "[MEMORY] Load error:",
            e
        )

        return []


# ============================================================
# SAVE MEMORY FILE
# ============================================================

def save_memory(memory):

    try:

        with open(
            MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                memory,
                f,
                indent=2,
                ensure_ascii=False
            )

        return True

    except Exception as e:

        print(
            "[MEMORY] Save error:",
            e
        )

        return False


# ============================================================
# CLEAN MEMORY TEXT
# ============================================================

def clean_memory_text(text):

    if not text:
        return ""

    text = str(text).strip()

    # Remove excessive whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SHOULD SAVE?
# ============================================================

def should_save_memory(text):

    if not text:
        return False

    text = clean_memory_text(text)

    lower = text.lower()

    # --------------------------------------------------------
    # NEVER SAVE API / SYSTEM ERRORS
    # --------------------------------------------------------

    blocked = [

        "error code:",
        "rate limit exceeded",
        "api error",
        "traceback",
        "exception",
        "internal server error",
        "something went wrong",
        "couldn't generate the answer",
        "couldn't generate an answer",
        "ai service returned an error",
        "tool error",
        "memory search failed",
        "pdf search failed",
        "razorpay",
        "mcp result",
        "tool used",
        "amount_due",
        "amount_paid",
        "created_at",
        "order_",
        "pay_",
        "rfnd_",
        "plink_",
    ]

    for item in blocked:

        if item in lower:
            return False

    return True


# ============================================================
# EXTRACT IMPORTANT MEMORY
# ============================================================

def extract_memory(text):

    memories = []

    if not text:
        return memories

    text = clean_memory_text(text)

    # --------------------------------------------------------
    # NAME
    # --------------------------------------------------------

    match = re.search(
        r"\bmy name is\s+([A-Za-z][A-Za-z\s'-]{1,40})",
        text,
        re.IGNORECASE
    )

    if match:

        name = match.group(1).strip()

        memories.append(
            f"User's name is {name}."
        )


    # --------------------------------------------------------
    # LEARNING
    # --------------------------------------------------------

    match = re.search(
        r"\b(?:i am|i'm)\s+(?:learning|studying)\s+(.+?)(?:[.!?]|$)",
        text,
        re.IGNORECASE
    )

    if match:

        subject = match.group(1).strip()

        memories.append(
            f"User is learning {subject}."
        )


    # --------------------------------------------------------
    # BUILDING
    # --------------------------------------------------------

    match = re.search(
        r"\b(?:i am|i'm)\s+building\s+(.+?)(?:[.!?]|$)",
        text,
        re.IGNORECASE
    )

    if match:

        project = match.group(1).strip()

        memories.append(
            f"User is building {project}."
        )


    # --------------------------------------------------------
    # WORKING ON
    # --------------------------------------------------------

    match = re.search(
        r"\b(?:i am|i'm)\s+working on\s+(.+?)(?:[.!?]|$)",
        text,
        re.IGNORECASE
    )

    if match:

        project = match.group(1).strip()

        memories.append(
            f"User is working on {project}."
        )


    # --------------------------------------------------------
    # FAVORITE PROGRAMMING LANGUAGE
    # --------------------------------------------------------

    match = re.search(
        r"\bmy (?:favorite|favourite) programming language is\s+(.+?)(?:[.!?]|$)",
        text,
        re.IGNORECASE
    )

    if match:

        language = match.group(1).strip()

        memories.append(
            f"User's favorite programming language is {language}."
        )


    return memories


# ============================================================
# ADD MEMORY
# ============================================================

def add_memory(text):

    if not should_save_memory(text):

        print(
            "[MEMORY] Rejected temporary/system content."
        )

        return False

    memories = extract_memory(text)

    if not memories:

        print(
            "[MEMORY] No important personal information detected."
        )

        return False

    existing = load_memory()

    changed = False

    for memory in memories:

        duplicate = False

        for old in existing:

            if (
                isinstance(old, str)
                and old.strip().lower()
                == memory.strip().lower()
            ):

                duplicate = True
                break

        if not duplicate:

            existing.append(memory)

            changed = True

            print(
                "[MEMORY] Saved:",
                memory
            )

    if changed:

        save_memory(existing)

    return changed


# ============================================================
# SEARCH MEMORY
# ============================================================

def search_memory(query):

    memory = load_memory()

    if not memory:
        return []


    query = clean_memory_text(query)

    query_words = set(
        word.lower()
        for word in re.findall(
            r"[a-zA-Z0-9']+",
            query
        )
        if len(word) > 2
    )


    results = []


    for item in memory:

        if not isinstance(item, str):
            continue

        item_words = set(
            word.lower()
            for word in re.findall(
                r"[a-zA-Z0-9']+",
                item
            )
            if len(word) > 2
        )

        score = len(
            query_words & item_words
        )

        if score > 0:

            results.append(
                (score, item)
            )


    results.sort(
        key=lambda x: x[0],
        reverse=True
    )


    return [
        item
        for score, item in results
    ]


# ============================================================
# MEMORY TOOL
# ============================================================

def memory_tool(query):

    results = search_memory(query)

    print(
        f"[MEMORY] Found {len(results)} memories."
    )

    return results