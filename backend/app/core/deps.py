import uuid

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.db.models import User
from app.db.session import get_db
from app.repositories import users_repo


def get_current_user(db: Session = Depends(get_db)) -> User:
    """TEMPORARY: returns the fixed development user.
    Phase 11 replaces this with the verified signed-in user."""
    if settings.auth_mode != "dev_stub":
        raise AppError(500, "AUTH_NOT_CONFIGURED", "Authentication is not configured.")
    user = users_repo.get_by_id(db, uuid.UUID(settings.dev_user_id))
    if user is None:
        raise AppError(500, "DEV_USER_MISSING", "Run the seed script to create the dev user.")
    return user