from app.rag.embeddings import create_embeddings
from app.rag.vectorstore import (
    search,
    replace_document
)
from app.rag.chunking import split_text
from app.rag.pdf_loader import load_pdf


# ============================================================
# INDEX PDF
# ============================================================

def index_pdf(pdf_path):

    print(
        "\n[RAG] Indexing PDF..."
    )

    print(
        "[RAG] PDF:",
        pdf_path
    )

    text = load_pdf(
        pdf_path
    )

    if not text.strip():

        raise ValueError(
            "No text could be extracted from PDF."
        )

    print(
        "[RAG] Characters:",
        len(text)
    )

    chunks = split_text(
        text,
        chunk_size=1000,
        overlap=200
    )

    if not chunks:

        raise ValueError(
            "No chunks were created."
        )

    print(
        "[RAG] Chunks:",
        len(chunks)
    )

    print(
        "[RAG] Creating embeddings..."
    )

    embeddings = create_embeddings(
        chunks
    )

    print(
        "[RAG] Embeddings created."
    )

    replace_document(
        chunks,
        embeddings
    )

    print(
        "[RAG] PDF indexed successfully."
    )

    return {
        "chunks": len(chunks),
        "characters": len(text)
    }


# ============================================================
# RETRIEVE PDF DOCUMENTS
# ============================================================

def retrieve_documents(
    question,
    top_k=3
):

    print(
        "[RAG] Creating question embedding..."
    )

    embedding = create_embeddings(
        [question]
    )[0]

    print(
        "[RAG] Searching ChromaDB..."
    )

    results = search(
        embedding,
        top_k=top_k
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    print(
        "[RAG] Retrieved:",
        len(documents),
        "chunks"
    )

    return documents


# ============================================================
# PDF SEARCH
# ============================================================

def search_pdf(
    question,
    top_k=3
):

    return retrieve_documents(
        question,
        top_k
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    question = input(
        "PDF question: "
    )

    documents = search_pdf(
        question,
        top_k=3
    )

    print(
        "\n========== RESULTS =========="
    )

    for i, document in enumerate(
        documents,
        start=1
    ):

        print(
            f"\n--- Chunk {i} ---"
        )

        print(
            document
        )