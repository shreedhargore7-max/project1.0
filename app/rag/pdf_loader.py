from pathlib import Path
from pypdf import PdfReader


def load_pdf(pdf_path):
    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


if __name__ == "__main__":

    # Get PROJECT folder
    project_dir = Path(__file__).resolve().parent.parent

    # PROJECT/data/sample.pdf
    pdf_path = project_dir / "data" / "sample.pdf"

    print("Looking for PDF at:")
    print(pdf_path)

    if not pdf_path.exists():
        print("\nERROR: PDF not found!")
        print("Put your PDF here:")
        print(pdf_path)
        exit()

    text = load_pdf(pdf_path)

    print("\nPDF loaded successfully!")
    print("Characters:", len(text))

    print("\nFirst 1000 characters:\n")
    print(text[:1000])