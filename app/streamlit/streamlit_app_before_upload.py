import streamlit as st
import sys
from pathlib import Path

# ==========================================
# PROJECT PATH
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_DIR / "app"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


# ==========================================
# IMPORT AGENT
# ==========================================

from agent.agent import graph


# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🤖",
    layout="wide"
)


# ==========================================
# TITLE
# ==========================================

st.title("🤖 AI Research Assistant")

st.write(
    "Ask questions about your PDF, search the web, "
    "use memory, or ask Gemini general questions."
)


# ==========================================
# CHAT HISTORY
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================
# SHOW PREVIOUS MESSAGES
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# ==========================================
# USER INPUT
# ==========================================

question = st.chat_input(
    "Ask your question..."
)


# ==========================================
# PROCESS QUESTION
# ==========================================

if question:

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Generate answer
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            try:

                result = graph.invoke({
                    "question": question,
                    "context": "",
                    "answer": ""
                })

                answer = result["answer"]

            except Exception as e:

                answer = f"Error: {e}"

            st.markdown(answer)

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.header("AI Research Assistant")

    st.write("Available capabilities:")

    st.write("📄 PDF RAG")
    st.write("🌐 Web Search")
    st.write("🧠 Memory")
    st.write("🤖 Gemini")
    st.write("🔀 LangGraph")

    st.divider()

    if st.button("Clear Chat"):

        st.session_state.messages = []

        st.rerun()