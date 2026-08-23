from pathlib import Path
import chromadb


PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

CHROMA_PATH = PROJECT_DIR / "chroma_db"


client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


collection = client.get_or_create_collection(
    name="pdf_documents"
)


def store_embeddings(chunks, embeddings):

    ids = [
        f"chunk_{i}"
        for i in range(len(chunks))
    ]

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings.tolist()
    )

    print(
        f"Stored {len(chunks)} chunks in ChromaDB."
    )


def search(query_embedding, top_k=3):

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=top_k
    )

    return results


if __name__ == "__main__":

    print(
        "ChromaDB initialized successfully!"
    )

    print(
        "Database location:",
        CHROMA_PATH
    )

    print(
        "Collection:",
        collection.name
    )

    print(
        "Documents currently stored:",
        collection.count()
    )