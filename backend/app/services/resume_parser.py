"""
Extracts plain text from an uploaded resume file so it can be stored in
Profile.resume_text and used for AI matching / cover letter generation.
"""
import io

from docx import Document
from pypdf import PdfReader


class UnsupportedFileType(Exception):
    pass


def extract_text(filename: str, content: bytes) -> str:
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "pdf":
        return _extract_pdf(content)
    if ext == "docx":
        return _extract_docx(content)
    if ext == "txt":
        return content.decode("utf-8", errors="ignore")

    raise UnsupportedFileType(
        f"Unsupported file type '.{ext}'. Please upload a PDF, DOCX, or TXT file."
    )


def _extract_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    pages_text = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages_text).strip()


def _extract_docx(content: bytes) -> str:
    doc = Document(io.BytesIO(content))
    paragraphs = [p.text for p in doc.paragraphs if p.text]
    return "\n".join(paragraphs).strip()