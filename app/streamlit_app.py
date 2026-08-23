import streamlit as st
import sys
import time
import json
import uuid
from pathlib import Path
from datetime import datetime


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[1]

if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


# ============================================================
# IMPORT PROJECT MODULES
# ============================================================

from app.rag.rag_tool import index_pdf
from app.agent.agent import graph


# ============================================================
# CHAT STORAGE
# ============================================================

CHAT_DIR = PROJECT_DIR / "data" / "chats"
CHAT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #888;
        margin-bottom: 25px;
    }

    section[data-testid="stSidebar"] {
        width: 300px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# CHAT FILE FUNCTIONS
# ============================================================

def chat_file(chat_id):
    return CHAT_DIR / f"{chat_id}.json"


def create_new_chat():
    chat_id = str(uuid.uuid4())

    chat = {
        "id": chat_id,
        "title": "New Chat",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "messages": []
    }

    save_chat(chat)

    return chat


def save_chat(chat):
    path = chat_file(chat["id"])

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            chat,
            f,
            indent=2,
            ensure_ascii=False
        )


def load_chat(chat_id):
    path = chat_file(chat_id)

    if not path.exists():
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    except Exception:
        return None


def load_all_chats():
    chats = []

    for path in CHAT_DIR.glob("*.json"):

        try:

            with open(path, "r", encoding="utf-8") as f:
                chat = json.load(f)

            chats.append(chat)

        except Exception:
            continue

    chats.sort(
        key=lambda x: x.get("updated_at", ""),
        reverse=True
    )

    return chats


def delete_chat(chat_id):

    path = chat_file(chat_id)

    if path.exists():
        path.unlink()


def generate_chat_title(question):

    title = question.strip()

    if not title:
        return "New Chat"

    # Remove line breaks
    title = title.replace("\n", " ")

    # Keep sidebar title short
    if len(title) > 35:
        title = title[:35].rstrip() + "..."

    return title


# ============================================================
# SESSION STATE
# ============================================================

if "current_chat_id" not in st.session_state:

    chats = load_all_chats()

    if chats:
        st.session_state.current_chat_id = chats[0]["id"]
    else:
        new_chat = create_new_chat()
        st.session_state.current_chat_id = new_chat["id"]


if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False


if "pdf_name" not in st.session_state:
    st.session_state.pdf_name = None


# ============================================================
# LOAD CURRENT CHAT
# ============================================================

current_chat = load_chat(
    st.session_state.current_chat_id
)

if current_chat is None:

    current_chat = create_new_chat()

    st.session_state.current_chat_id = current_chat["id"]


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🤖 AI Research Assistant</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Ask questions, upload documents, search the web, '
    'and use AI memory.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("💬 Chat History")


    # --------------------------------------------------------
    # NEW CHAT
    # --------------------------------------------------------

    if st.button(
        "＋ New Chat",
        use_container_width=True
    ):

        new_chat = create_new_chat()

        st.session_state.current_chat_id = new_chat["id"]

        st.rerun()


    st.divider()


    # --------------------------------------------------------
    # RECENT CHATS
    # --------------------------------------------------------

    chats = load_all_chats()

    if chats:

        st.caption("RECENT CHATS")

        for chat in chats:

            chat_title = chat.get(
                "title",
                "New Chat"
            )

            # Highlight current chat
            if chat["id"] == st.session_state.current_chat_id:

                button_label = f"🟢 {chat_title}"

            else:

                button_label = f"💬 {chat_title}"


            if st.button(
                button_label,
                key=f"chat_{chat['id']}",
                use_container_width=True
            ):

                st.session_state.current_chat_id = chat["id"]

                st.rerun()


    else:

        st.caption("No previous chats yet.")


    st.divider()


    # --------------------------------------------------------
    # DOCUMENT
    # --------------------------------------------------------

    st.header("📁 Document")

    uploaded_file = st.file_uploader(
        "Upload a PDF",
        type=["pdf"]
    )


    if uploaded_file is not None:

        if uploaded_file.name != st.session_state.pdf_name:

            temp_dir = PROJECT_DIR / "data"

            temp_dir.mkdir(
                exist_ok=True
            )

            pdf_path = temp_dir / uploaded_file.name


            with open(
                pdf_path,
                "wb"
            ) as f:

                f.write(
                    uploaded_file.getbuffer()
                )


            with st.spinner(
                "Processing PDF..."
            ):

                try:

                    index_pdf(
                        str(pdf_path)
                    )

                    st.session_state.pdf_uploaded = True

                    st.session_state.pdf_name = uploaded_file.name

                    st.success(
                        f"PDF ready: {uploaded_file.name}"
                    )

                except Exception as e:

                    st.error(
                        f"PDF processing failed: {e}"
                    )


    elif st.session_state.pdf_uploaded:

        st.success(
            f"Current PDF: {st.session_state.pdf_name}"
        )


    st.divider()


    # --------------------------------------------------------
    # DELETE CURRENT CHAT
    # --------------------------------------------------------

    if st.button(
        "🗑️ Delete Current Chat",
        use_container_width=True
    ):

        delete_chat(
            st.session_state.current_chat_id
        )

        remaining_chats = load_all_chats()

        if remaining_chats:

            st.session_state.current_chat_id = remaining_chats[0]["id"]

        else:

            new_chat = create_new_chat()

            st.session_state.current_chat_id = new_chat["id"]

        st.rerun()


# ============================================================
# CURRENT CHAT TITLE
# ============================================================

current_chat = load_chat(
    st.session_state.current_chat_id
)

if current_chat is None:

    current_chat = create_new_chat()

    st.session_state.current_chat_id = current_chat["id"]


if current_chat["title"] != "New Chat":

    st.caption(
        f"💬 {current_chat['title']}"
    )


# ============================================================
# SHOW CHAT HISTORY
# ============================================================

for message in current_chat["messages"]:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask anything..."
)


# ============================================================
# PROCESS QUESTION
# ============================================================

if question:

    # --------------------------------------------------------
    # SAVE USER MESSAGE
    # --------------------------------------------------------

    current_chat["messages"].append(
        {
            "role": "user",
            "content": question
        }
    )


    # --------------------------------------------------------
    # CREATE CHAT TITLE
    # --------------------------------------------------------

    if current_chat["title"] == "New Chat":

        current_chat["title"] = generate_chat_title(
            question
        )


    current_chat["updated_at"] = datetime.now().isoformat()

    save_chat(current_chat)


    # --------------------------------------------------------
    # DISPLAY USER MESSAGE
    # --------------------------------------------------------

    with st.chat_message("user"):

        st.markdown(
            question
        )


    # --------------------------------------------------------
    # BUILD PREVIOUS CHAT CONTEXT
    # --------------------------------------------------------

    chat_history = ""

    for message in current_chat["messages"][:-1]:

        role = (
            "User"
            if message["role"] == "user"
            else "Assistant"
        )

        chat_history += (
            f"{role}: "
            f"{message['content']}\n"
        )


    # --------------------------------------------------------
    # CREATE QUESTION WITH HISTORY
    # --------------------------------------------------------

    question_with_history = f"""
Previous conversation:

{chat_history}

Current question:

{question}
"""


    # --------------------------------------------------------
    # GENERATE ANSWER
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        response_placeholder = st.empty()

        try:

            with st.spinner(
                "Thinking..."
            ):

                result = graph.invoke(
                    {
                        "question": question_with_history,
                        "tool": "",
                        "tool_result": "",
                        "answer": ""
                    }
                )

                answer = result["answer"]


            # ------------------------------------------------
            # STREAM ANSWER
            # ------------------------------------------------

            displayed_text = ""

            words = answer.split(" ")

            for word in words:

                displayed_text += word + " "

                response_placeholder.markdown(
                    displayed_text
                )

                time.sleep(
                    0.025
                )


        except Exception as e:

            answer = f"Error: {e}"

            response_placeholder.error(
                answer
            )


    # --------------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # --------------------------------------------------------

    current_chat["messages"].append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    current_chat["updated_at"] = datetime.now().isoformat()

    save_chat(current_chat)


    # --------------------------------------------------------
    # RERUN TO UPDATE SIDEBAR
    # --------------------------------------------------------

    st.rerun()

