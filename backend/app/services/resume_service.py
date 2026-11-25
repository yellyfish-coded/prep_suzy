import logging
import uuid

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.db.models import Resume, User
from app.repositories import resumes_repo
from app.services.file_validation import ALLOWED, safe_filename, validate_upload
from app.storage import supabase_storage as storage
from app.workers.tasks import process_resume

log = logging.getLogger(__name__)


def create_resume(db: Session, user: User, filename: str, data: bytes) -> Resume:
    file_type = validate_upload(filename, data)

    if resumes_repo.count_for_user(db, user.id) >= settings.max_resumes_per_user:
        raise AppError(
            409,
            "RESUME_LIMIT_REACHED",
            f"You can keep up to {settings.max_resumes_per_user} resumes. Delete one first.",
        )

    key = f"{uuid.uuid4().hex}.{file_type}"  # random key, no personal information
    try:
        storage.put(key, data, ALLOWED[file_type])
    except storage.StorageError:
        raise AppError(502, "STORAGE_ERROR", "Could not save the file. Please try again.")

    try:
        resume = resumes_repo.create(
            db, user.id, safe_filename(filename), file_type, len(data), key
        )
    except Exception:
        _delete_quietly(key)
        raise

    queue_processing(db, resume)
    return resume


def queue_processing(db: Session, resume: Resume) -> None:
    try:
        process_resume.delay(str(resume.id))
    except Exception:
        log.exception("Could not queue resume processing")
        resumes_repo.set_status(
            db, resume, "failed", "Could not start processing. Please try again."
        )


def delete_resume(db: Session, resume: Resume) -> None:
    try:
        storage.delete(resume.storage_key)
    except storage.StorageNotFound:
        pass
    except storage.StorageError:
        raise AppError(502, "STORAGE_ERROR", "Could not delete the file. Please try again.")
    resumes_repo.delete_row(db, resume)


def _delete_quietly(key: str) -> None:
    try:
        storage.delete(key)
    except storage.StorageError:
        log.warning("Could not clean up orphaned file")