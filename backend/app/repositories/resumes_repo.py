import uuid

from sqlalchemy import delete as sa_delete
from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.db.models import Resume, ResumeEducation, ResumeExperience, ResumeProject, ResumeSkill
from app.schemas.resume import (
    EducationItem,
    ExperienceItem,
    ProjectItem,
    ResumeAnalysis,
    SkillItem,
)

CHILD_MODELS = (ResumeSkill, ResumeProject, ResumeExperience, ResumeEducation)


def count_for_user(db: Session, user_id: uuid.UUID) -> int:
    return db.scalar(select(func.count()).select_from(Resume).where(Resume.user_id == user_id)) or 0


def create(
    db: Session, user_id: uuid.UUID, filename: str, file_type: str, file_size: int, storage_key: str
) -> Resume:
    resume = Resume(
        user_id=user_id,
        original_filename=filename,
        file_type=file_type,
        file_size=file_size,
        storage_key=storage_key,
        status="uploaded",
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


def list_for_user(db: Session, user_id: uuid.UUID) -> list[Resume]:
    return list(
        db.scalars(
            select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
        )
    )


def get(db: Session, user_id: uuid.UUID, resume_id: uuid.UUID) -> Resume | None:
    return db.scalar(select(Resume).where(Resume.id == resume_id, Resume.user_id == user_id))


def get_for_worker(db: Session, resume_id: uuid.UUID) -> Resume | None:
    """Background worker only. The owner comes from the row itself, never from a request."""
    return db.scalar(select(Resume).where(Resume.id == resume_id))


def set_status(db: Session, resume: Resume, status: str, message: str | None = None) -> None:
    resume.status = status
    resume.status_message = message
    db.commit()


def delete_row(db: Session, resume: Resume) -> None:
    db.delete(resume)  # child rows are removed by ON DELETE CASCADE
    db.commit()


def replace_analysis(
    db: Session, resume: Resume, analysis: ResumeAnalysis, source_type: str, confirmed: bool
) -> None:
    for model in CHILD_MODELS:
        db.execute(sa_delete(model).where(model.resume_id == resume.id, model.user_id == resume.user_id))

    base = {
        "resume_id": resume.id,
        "user_id": resume.user_id,
        "source_type": source_type,
        "is_confirmed": confirmed,
    }
    db.add_all(
        [ResumeSkill(**base, position=i, **s.model_dump()) for i, s in enumerate(analysis.skills)]
    )
    db.add_all(
        [ResumeProject(**base, position=i, **p.model_dump()) for i, p in enumerate(analysis.projects)]
    )
    db.add_all(
        [
            ResumeExperience(**base, position=i, **e.model_dump())
            for i, e in enumerate(analysis.experiences)
        ]
    )
    db.add_all(
        [ResumeEducation(**base, position=i, **e.model_dump()) for i, e in enumerate(analysis.education)]
    )
    db.commit()


def get_analysis(db: Session, user_id: uuid.UUID, resume_id: uuid.UUID) -> ResumeAnalysis:
    def rows(model):
        return db.scalars(
            select(model)
            .where(model.resume_id == resume_id, model.user_id == user_id)
            .order_by(model.position)
        ).all()

    return ResumeAnalysis(
        skills=[SkillItem.model_validate(r) for r in rows(ResumeSkill)],
        projects=[ProjectItem.model_validate(r) for r in rows(ResumeProject)],
        experiences=[ExperienceItem.model_validate(r) for r in rows(ResumeExperience)],
        education=[EducationItem.model_validate(r) for r in rows(ResumeEducation)],
    )


def confirm(db: Session, resume: Resume) -> None:
    for model in CHILD_MODELS:
        db.execute(
            update(model)
            .where(model.resume_id == resume.id, model.user_id == resume.user_id)
            .values(is_confirmed=True)
        )
    resume.status = "completed"
    resume.status_message = None
    db.commit()