import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import User


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.scalar(select(User).where(User.id == user_id))


def update_profile(db: Session, user: User, data: dict) -> User:
    for field, value in data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user