import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from app.rag.embeddings import create_embeddings
from app.rag.vectorstore import search, replace_document
from app.rag.chunking import split_text
from app.rag.pdf_loader import load_pdf


# ==========================================
# LOAD .ENV FROM PROJECT ROOT
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parents[2]

ENV_FILE = PROJECT_DIR / ".env"

print("Loading .env from:")
print(ENV_FILE)

load_dotenv(ENV_FILE)


# ==========================================
# GEMINI API KEY
# ==========================================

api_key = os.getenv("GEMINI_API_KEY")

print("API key loaded:", bool(api_key))

print(
    "API key length:",
    len(api_key) if api_key else 0
)

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in PROJECT/.env"
    )


# ==========================================
# GEMINI CLIENT
# ==========================================

client = genai.Client(
    api_key=api_key
)

MODEL_NAME = "gemini-3.6-flash"


def index_pdf(pdf_path):
    """
    Load a PDF, split it into chunks,
    create embeddings, and store them in ChromaDB.
    """

    print("\nIndexing PDF...")
    print("PDF:", pdf_path)

    # Load PDF
    text = load_pdf(pdf_path)

    if not text.strip():
        raise ValueError(
            "No text could be extracted from the PDF."
        )

    print("PDF loaded.")
    print("Characters:", len(text))

    # Split text into chunks
    chunks = split_text(
        text,
        chunk_size=1000,
        overlap=200
    )

    if not chunks:
        raise ValueError(
            "No chunks were created from the PDF."
        )

    print("Chunks created:", len(chunks))

    # Create embeddings
    print("Creating embeddings...")

    embeddings = create_embeddings(chunks)

    print("Embeddings created.")

    # Replace existing PDF in ChromaDB
    replace_document(
        chunks,
        embeddings
    )

    print("PDF indexed successfully.")

    return {
        "chunks": len(chunks),
        "characters": len(text)
    }


# ==========================================
# RETRIEVE RELEVANT DOCUMENTS
# ==========================================

def retrieve_documents(question, top_k=3):

    print("\nCreating question embedding...")

    embedding = create_embeddings([question])[0]

    print("Searching ChromaDB...")

    results = search(
        embedding,
        top_k=top_k
    )

    documents = results["documents"][0]

    print(
        f"Retrieved {len(documents)} relevant chunks."
    )

    return documents


# ==========================================
# SEARCH PDF
# ==========================================

def search_pdf(question, top_k=3):

    """
    Search the PDF and return relevant chunks.
    Used by the LangGraph agent.
    """

    return retrieve_documents(
        question,
        top_k
    )


# ==========================================
# GENERATE ANSWER
# ==========================================

def generate_answer(question, documents):

    context = "\n\n".join(documents)

    prompt = f"""
You are a helpful PDF assistant.

Answer the user's question using ONLY the
information provided in the context.

If the answer is not available in the context,
say:

"I could not find this information in the PDF."

Do not invent information.

---------------- CONTEXT ----------------

{context}

-------------- END CONTEXT --------------

Question:
{question}

Answer:
"""

    print("\nSending context to Gemini...")

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    return response.text


# ==========================================
# MAIN APPLICATION
# ==========================================

def main():

    print("\n====================================")
    print("        PDF RAG APPLICATION")
    print("====================================")

    while True:

        question = input(
            "\nAsk a question about the PDF "
            "(type 'exit' to quit): "
        )

        if question.lower() == "exit":

            print("\nGoodbye!")

            break

        if not question.strip():

            print("Please enter a question.")

            continue

        try:

            # Step 1: Retrieve documents

            documents = retrieve_documents(
                question,
                top_k=3
            )


            # Step 2: Generate answer

            answer = generate_answer(
                question,
                documents
            )


            # Step 3: Show answer

            print("\n====================================")
            print("                ANSWER")
            print("====================================")

            print(answer)


            # Step 4: Show retrieved chunks

            print("\n====================================")
            print("          RETRIEVED SOURCES")
            print("====================================")

            for i, document in enumerate(documents):

                print(
                    f"\n--- Chunk {i + 1} ---"
                )

                print(document[:300])

                if len(document) > 300:

                    print("...")


        except Exception as e:

            print("\nERROR:")

            print(e)


# ==========================================
# START PROGRAM
# ==========================================

if __name__ == "__main__":

    main()