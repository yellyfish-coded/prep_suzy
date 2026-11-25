import logging
import uuid

from app.core.config import settings
from app.db.session import SessionLocal
from app.repositories import resumes_repo
from app.schemas.resume import ResumeAnalysis
from app.services import analysis as analysis_service
from app.services import extraction
from app.storage import supabase_storage as storage
from app.workers.celery_app import celery

log = logging.getLogger(__name__)

FAILED_MESSAGE = "We could not read this resume. Try another file or upload it again."
LITTLE_TEXT_MESSAGE = (
    "We found very little text in this file. You can add your details manually below."
)


@celery.task(name="process_resume")
def process_resume(resume_id: str) -> None:
    with SessionLocal() as db:
        resume = resumes_repo.get_for_worker(db, uuid.UUID(resume_id))
        if resume is None:
            return  # deleted before the worker got to it

        try:
            resumes_repo.set_status(db, resume, "processing")

            data = storage.get(resume.storage_key)
            text, warnings = extraction.extract_text(data, resume.file_type)
            resume.extracted_text = text
            resume.extraction_warnings = warnings

            if "little_text_found" in warnings and len(text.strip()) < settings.extraction_min_chars:
                resumes_repo.replace_analysis(db, resume, ResumeAnalysis(), "ai_extracted", False)
                resumes_repo.set_status(db, resume, "needs_review", LITTLE_TEXT_MESSAGE)
                return

            result = analysis_service.analyze(text)
            resumes_repo.replace_analysis(db, resume, result, "ai_extracted", False)
            resumes_repo.set_status(db, resume, "needs_review")
        except Exception:
            log.exception("Resume processing failed for %s", resume_id)
            db.rollback()
            resumes_repo.set_status(db, resume, "failed", FAILED_MESSAGE)