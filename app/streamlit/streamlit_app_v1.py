import streamlit as st

# ==========================================
# PAGE CONFIGURATION
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
    "or ask the agent about stored memory."
)


# ==========================================
# QUESTION INPUT
# ==========================================

question = st.text_input(
    "Ask a question:",
    placeholder="Example: What company is mentioned in the PDF?"
)


# ==========================================
# ASK BUTTON
# ==========================================

if st.button("Ask"):

    if not question.strip():

        st.warning("Please enter a question.")

    else:

        st.info("Your question was received.")

        st.write("Question:", question)