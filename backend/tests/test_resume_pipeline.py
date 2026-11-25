import io

import pymupdf
import pytest
from docx import Document

from app.ai.heuristic import HeuristicLLMClient
from app.core.errors import AppError
from app.services.extraction import extract_text
from app.services.file_validation import validate_upload
from app.services.redaction import redact


def make_pdf(text: str = "Hello world") -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    data = doc.tobytes()
    doc.close()
    return data


def make_docx(text: str) -> bytes:
    doc = Document()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def test_valid_pdf_and_docx_are_accepted():
    assert validate_upload("cv.pdf", make_pdf()) == "pdf"
    assert validate_upload("cv.docx", make_docx("hello")) == "docx"


def test_disguised_executable_is_rejected():
    with pytest.raises(AppError) as exc:
        validate_upload("resume.pdf", b"MZ\x90\x00 not a pdf")
    assert exc.value.code == "INVALID_FILE"


def test_wrong_extension_is_rejected():
    with pytest.raises(AppError) as exc:
        validate_upload("resume.exe", b"anything")
    assert exc.value.code == "UNSUPPORTED_FILE_TYPE"


def test_empty_and_oversized_files_are_rejected():
    with pytest.raises(AppError) as exc:
        validate_upload("cv.pdf", b"")
    assert exc.value.code == "EMPTY_FILE"
    with pytest.raises(AppError) as exc:
        validate_upload("cv.pdf", b"%PDF-" + b"0" * (5 * 1024 * 1024 + 1))
    assert exc.value.code == "FILE_TOO_LARGE"


def test_redaction_hides_contacts_but_keeps_date_ranges():
    out = redact("Mail jane@example.com or call +965 5555 1234. Worked 2019 - 2023. github.com/jane")
    assert "jane@example.com" not in out
    assert "5555" not in out
    assert "github.com/jane" not in out
    assert "2019 - 2023" in out


def test_docx_extraction_and_little_text_warning():
    text, warnings = extract_text(make_docx("Python developer " * 30), "docx")
    assert "Python developer" in text
    assert warnings == []
    _, short_warnings = extract_text(make_docx("hi"), "docx")
    assert "little_text_found" in short_warnings


def test_heuristic_reader_finds_skills_and_sections():
    text = (
        "Jane Doe\nSKILLS\nPython, SQL, Docker\nPROJECTS\nLibrary App\n"
        "- Built a library system using Python and PostgreSQL\n"
        "EDUCATION\nBSc Computer Science, Example University\n"
    )
    result = HeuristicLLMClient().extract_resume(text)
    names = {s["name"] for s in result["skills"]}
    assert {"Python", "SQL", "Docker", "PostgreSQL"} <= names
    assert result["projects"][0]["name"] == "Library App"
    assert "PostgreSQL" in result["projects"][0]["technologies"]
    assert result["education"] and result["education"][0]["degree"] == "BSc"