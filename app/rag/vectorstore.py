from pathlib import Path
import chromadb


# ==========================================
# PROJECT PATH
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parents[2]

CHROMA_PATH = PROJECT_DIR / "chroma_db"


# ==========================================
# CHROMADB CLIENT
# ==========================================

client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


# ==========================================
# COLLECTION
# ==========================================

collection = client.get_or_create_collection(
    name="pdf_documents"
)


# ==========================================
# STORE EMBEDDINGS
# ==========================================

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


# ==========================================
# CLEAR COLLECTION
# ==========================================

def clear_collection():

    global collection

    print("\nClearing existing PDF collection...")

    client.delete_collection(
        name="pdf_documents"
    )

    collection = client.get_or_create_collection(
        name="pdf_documents"
    )

    print("PDF collection cleared.")


# ==========================================
# REPLACE DOCUMENT
# ==========================================

def replace_document(chunks, embeddings):

    clear_collection()

    store_embeddings(
        chunks,
        embeddings
    )


# ==========================================
# SEARCH
# ==========================================

def search(query_embedding, top_k=3):

    results = collection.query(
        query_embeddings=[
            query_embedding.tolist()
        ],
        n_results=top_k
    )

    return results


# ==========================================
# DATABASE INFO
# ==========================================

def get_document_count():

    return collection.count()


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    print("====================================")
    print("          CHROMADB TEST")
    print("====================================")

    print("\nDatabase location:")
    print(CHROMA_PATH)

    print("\nCollection:")
    print(collection.name)

    print("\nDocuments currently stored:")
    print(collection.count())