import os
import sys
import streamlit as st

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# AGENT
# ============================================================

from app.agent.agent import graph


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Intelligent AI Assistant",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# TITLE
# ============================================================

st.title("🤖 Intelligent AI Assistant")
st.caption("Memory • PDF RAG • Chat History • Gemini")


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("Chat Controls")

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.write("### Agent capabilities")
    st.write("🧠 Long-term memory")
    st.write("📄 PDF RAG")
    st.write("💬 Chat history")
    st.write("✨ General conversation")


# ============================================================
# DISPLAY PREVIOUS MESSAGES
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# BUILD CHAT HISTORY
# ============================================================

def get_chat_history():

    history = []

    for message in st.session_state.messages:

        role = message["role"]
        content = message["content"]

        if role == "user":
            history.append(f"user: {content}")

        elif role == "assistant":
            history.append(f"assistant: {content}")

    return "\n".join(history)


# ============================================================
# CHAT INPUT
# ============================================================

user_question = st.chat_input("Ask me anything...")


if user_question:

    # --------------------------------------------------------
    # Show user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_question)

    # --------------------------------------------------------
    # Build previous conversation
    # --------------------------------------------------------

    chat_history = get_chat_history()

    # --------------------------------------------------------
    # Agent state
    # --------------------------------------------------------

    initial_state = {
        "question": user_question,
        "chat_history": chat_history,
        "memory_context": "",
        "tool": "",
        "tool_result": "",
        "answer": "",
    }

    # --------------------------------------------------------
    # Run agent
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                result = graph.invoke(initial_state)

                answer = result.get(
                    "answer",
                    "I couldn't generate an answer."
                )

            except Exception as e:

                answer = f"Sorry, something went wrong: {e}"

            st.markdown(answer)

    # --------------------------------------------------------
    # Save assistant response to UI history
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )