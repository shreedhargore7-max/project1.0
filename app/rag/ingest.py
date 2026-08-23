from pathlib import Path
import sys


# Add the app folder to Python's import path
APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))


from app.rag.pdf_loader import load_pdf
from app.rag.chunking import split_text
from app.rag.embeddings import create_embeddings
from app.rag.vectorstore import store_embeddings


# PROJECT folder
PROJECT_DIR = Path(__file__).resolve().parent.parent.parent

# PDF location
PDF_PATH = PROJECT_DIR / "data" / "sample.pdf"


print("================================")
print("       RAG INGESTION")
print("================================")


# 1. Load PDF
print("\n[1] Loading PDF...")

text = load_pdf(PDF_PATH)

print("PDF loaded successfully!")
print("Characters:", len(text))


# 2. Create chunks
print("\n[2] Creating chunks...")

chunks = split_text(
    text,
    chunk_size=800,
    overlap=150
)

print("Chunks created:", len(chunks))


# 3. Create embeddings
print("\n[3] Creating embeddings...")

embeddings = create_embeddings(chunks)

print("Embeddings created!")
print("Embedding shape:", embeddings.shape)


# 4. Store embeddings
print("\n[4] Storing in ChromaDB...")

store_embeddings(
    chunks,
    embeddings
)


print("\n================================")
print("   INGESTION COMPLETED ✅")
print("================================")