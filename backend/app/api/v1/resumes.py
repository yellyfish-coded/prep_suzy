import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user
from app.core.errors import AppError, not_found
from app.db.models import Resume, User
from app.db.session import get_db
from app.repositories import resumes_repo
from app.schemas.resume import AnalysisOut, ResumeAnalysis, ResumeOut
from app.services import resume_service
from app.storage import supabase_storage as storage

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _get_or_404(db: Session, user: User, resume_id: uuid.UUID) -> Resume:
    resume = resumes_repo.get(db, user.id, resume_id)
    if resume is None:
        raise not_found("Resume not found")  # same answer for "missing" and "not yours"
    return resume


def _analysis_out(db: Session, resume: Resume) -> AnalysisOut:
    analysis = resumes_repo.get_analysis(db, resume.user_id, resume.id)
    return AnalysisOut(**analysis.model_dump(), is_confirmed=resume.status == "completed")


@router.post("", response_model=ResumeOut, status_code=201)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    max_bytes = settings.max_upload_mb * 1024 * 1024
    data = file.file.read(max_bytes + 1)  # never read more than the limit + 1 byte
    return resume_service.create_resume(db, user, file.filename or "resume", data)


@router.get("", response_model=list[ResumeOut])
def list_resumes(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return resumes_repo.list_for_user(db, user.id)


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    return _get_or_404(db, user, resume_id)


@router.get("/{resume_id}/analysis", response_model=AnalysisOut)
def get_analysis(
    resume_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    resume = _get_or_404(db, user, resume_id)
    if resume.status not in ("needs_review", "completed"):
        raise AppError(409, "RESUME_NOT_READY", "This resume is still being processed.")
    return _analysis_out(db, resume)


@router.put("/{resume_id}/analysis", response_model=AnalysisOut)
def save_analysis(
    resume_id: uuid.UUID,
    payload: ResumeAnalysis,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    resume = _get_or_404(db, user, resume_id)
    if resume.status not in ("needs_review", "completed"):
        raise AppError(409, "RESUME_NOT_READY", "This resume is still being processed.")
    resumes_repo.replace_analysis(db, resume, payload, "user_edited", False)
    resumes_repo.set_status(db, resume, "needs_review")  # edits must be confirmed again
    return _analysis_out(db, resume)


@router.post("/{resume_id}/confirm", response_model=ResumeOut)
def confirm_resume(
    resume_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    resume = _get_or_404(db, user, resume_id)
    if resume.status != "needs_review":
        raise AppError(409, "RESUME_NOT_READY", "There is nothing to confirm right now.")
    resumes_repo.confirm(db, resume)
    return resume


@router.post("/{resume_id}/reprocess", response_model=ResumeOut)
def reprocess_resume(
    resume_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    resume = _get_or_404(db, user, resume_id)
    if resume.status in ("uploaded", "processing"):
        raise AppError(409, "RESUME_BUSY", "This resume is already being processed.")
    resumes_repo.set_status(db, resume, "uploaded")
    resume_service.queue_processing(db, resume)
    return resume


@router.get("/{resume_id}/file-url")
def get_file_url(
    resume_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    resume = _get_or_404(db, user, resume_id)
    try:
        url = storage.signed_url(resume.storage_key, 120)
    except storage.StorageError:
        raise AppError(502, "STORAGE_ERROR", "Could not create a download link.")
    return {"url": url, "expires_in": 120}


@router.delete("/{resume_id}", status_code=204)
def delete_resume(
    resume_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    resume = _get_or_404(db, user, resume_id)
    resume_service.delete_resume(db, resume)