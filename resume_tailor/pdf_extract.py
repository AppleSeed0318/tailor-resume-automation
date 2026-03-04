"""Extract raw text from resume PDF for LLM consumption."""

from pathlib import Path
from typing import Optional

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None  # type: ignore


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """Extract text from a PDF file. Uses pypdf."""
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")
    if path.suffix.lower() != ".pdf":
        raise ValueError("File must be a PDF")

    if PdfReader is None:
        raise ImportError("Install pypdf: pip install pypdf")

    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n\n".join(parts).strip() or ""
