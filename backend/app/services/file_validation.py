import io
import re
import zipfile

import pymupdf

from app.core.config import settings
from app.core.errors import AppError

ALLOWED = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_UNZIPPED_BYTES = 50 * 1024 * 1024


def safe_filename(name: str) -> str:
    base = name.replace("\\", "/").split("/")[-1]
    base = re.sub(r"[^\w.\- ]", "", base).strip()
    return (base or "resume")[:200]


def validate_upload(filename: str, data: bytes) -> str:
    """Returns the file type ("pdf" or "docx") or raises AppError."""
    if len(data) == 0:
        raise AppError(400, "EMPTY_FILE", "The file is empty.")
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise AppError(413, "FILE_TOO_LARGE", f"The maximum file size is {settings.max_upload_mb} MB.")

    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED:
        raise AppError(415, "UNSUPPORTED_FILE_TYPE", "Only PDF and DOCX files are accepted.")

    if ext == "pdf":
        _check_pdf(data)
    else:
        _check_docx(data)
    return ext


def _check_pdf(data: bytes) -> None:
    if not data.startswith(b"%PDF-"):
        raise AppError(400, "INVALID_FILE", "This file does not look like a valid PDF.")
    try:
        with pymupdf.open(stream=data, filetype="pdf") as doc:
            if doc.needs_pass:
                raise AppError(400, "PASSWORD_PROTECTED", "Password-protected PDFs are not supported.")
            if doc.page_count > settings.max_resume_pages:
                raise AppError(
                    400, "TOO_MANY_PAGES", f"Resumes can have at most {settings.max_resume_pages} pages."
                )
    except AppError:
        raise
    except Exception:
        raise AppError(400, "INVALID_FILE", "This PDF could not be read.")


def _check_docx(data: bytes) -> None:
    buf = io.BytesIO(data)
    if not zipfile.is_zipfile(buf):
        raise AppError(400, "INVALID_FILE", "This file does not look like a valid DOCX.")
    try:
        with zipfile.ZipFile(buf) as zf:
            names = zf.namelist()
            if "word/document.xml" not in names:
                raise AppError(400, "INVALID_FILE", "This file does not look like a valid DOCX.")
            if any(n.lower().endswith("vbaproject.bin") for n in names):
                raise AppError(400, "INVALID_FILE", "Files containing macros are not accepted.")
            if sum(i.file_size for i in zf.infolist()) > MAX_UNZIPPED_BYTES:
                raise AppError(400, "INVALID_FILE", "This file is too large once unpacked.")
    except AppError:
        raise
    except zipfile.BadZipFile:
        raise AppError(400, "INVALID_FILE", "This DOCX could not be read.")