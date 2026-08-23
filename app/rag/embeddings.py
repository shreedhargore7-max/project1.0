from sentence_transformers import SentenceTransformer


# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def create_embeddings(chunks):
    """
    Convert text chunks into embedding vectors.
    """

    embeddings = model.encode(
        chunks,
        convert_to_numpy=True
    )

    return embeddings


if __name__ == "__main__":

    test_chunks = [
        "RAG stands for Retrieval Augmented Generation.",
        "Machine learning is a branch of artificial intelligence.",
        "Python is a programming language."
    ]

    embeddings = create_embeddings(test_chunks)

    print("Number of chunks:", len(test_chunks))
    print("Embedding shape:", embeddings.shape)

    print("\nFirst embedding:")
    print(embeddings[0])