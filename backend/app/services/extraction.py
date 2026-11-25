import io
import re

import pymupdf
from docx import Document

from app.core.config import settings


def extract_text(data: bytes, file_type: str) -> tuple[str, list[str]]:
    if file_type == "pdf":
        text = _pdf_text(data)
    elif file_type == "docx":
        text = _docx_text(data)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

    text = _clean(text)
    warnings: list[str] = []
    if len(text.strip()) < settings.extraction_min_chars:
        warnings.append("little_text_found")
    return text[: settings.max_extracted_chars], warnings


def _pdf_text(data: bytes) -> str:
    with pymupdf.open(stream=data, filetype="pdf") as doc:
        return "\n".join(page.get_text() for page in doc)


def _docx_text(data: bytes) -> str:
    doc = Document(io.BytesIO(data))
    parts = [p.text for p in doc.paragraphs]
    for table in doc.tables:
        for row in table.rows:
            parts.append(" | ".join(cell.text.strip() for cell in row.cells))
    return "\n".join(parts)


def _clean(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()