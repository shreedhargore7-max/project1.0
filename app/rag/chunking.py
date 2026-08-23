
from pathlib import Path
from app.rag.pdf_loader import load_pdf


def split_text(text, chunk_size=1000, overlap=200):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


if __name__ == "__main__":

    # Find PROJECT folder
    project_dir = Path(__file__).resolve().parent.parent

    # Find PDF
    pdf_path = project_dir / "data" / "sample.pdf"

    print("Loading PDF...")
    print("PDF:", pdf_path)

    # Load PDF
    text = load_pdf(pdf_path)

    print("\nPDF loaded successfully!")
    print("Characters:", len(text))

    # Create chunks
    chunks = split_text(
        text,
        chunk_size=800,
        overlap=150
    )

    print("Total chunks:", len(chunks))

    # Display first 3 chunks
    for i, chunk in enumerate(chunks[:3]):

        print(f"\n========== CHUNK {i + 1} ==========")

        print(chunk)

        print(f"\nChunk size: {len(chunk)} characters")