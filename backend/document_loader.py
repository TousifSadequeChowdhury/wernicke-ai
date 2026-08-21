"""
Extracts raw text from uploaded documents.

Supports .txt, .md, .pdf, and .docx. Add a new file type by adding a
branch in load_text() — nothing else in the pipeline needs to change.
"""
from pathlib import Path


class UnsupportedFileType(Exception):
    pass


def load_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()

    if suffix in (".txt", ".md"):
        return file_path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".pdf":
        return _load_pdf(file_path)

    if suffix == ".docx":
        return _load_docx(file_path)

    raise UnsupportedFileType(
        f"'{suffix}' is not supported yet. Supported types: .txt, .md, .pdf, .docx"
    )


def _load_pdf(file_path: Path) -> str:
    from pypdf import PdfReader

    reader = PdfReader(str(file_path))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n\n".join(pages)


def _load_docx(file_path: Path) -> str:
    import docx

    doc = docx.Document(str(file_path))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)
