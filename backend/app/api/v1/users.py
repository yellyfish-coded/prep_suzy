import uuid
from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.models import User
from app.db.session import get_db
from app.repositories import users_repo

router = APIRouter(prefix="/users", tags=["users"])


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    display_name: str | None
    education_level: str | None
    target_role: str | None
    experience_level: str | None
    created_at: datetime


class UserUpdate(BaseModel):
    # Only these fields can ever be changed. Extra fields (role, account_status...) are rejected.
    model_config = ConfigDict(extra="forbid")

    display_name: str | None = Field(default=None, max_length=100)
    education_level: str | None = Field(default=None, max_length=50)
    target_role: str | None = Field(default=None, max_length=100)
    experience_level: str | None = Field(default=None, max_length=50)


@router.get("/me", response_model=UserOut)
def read_me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return users_repo.update_profile(db, user, payload.model_dump(exclude_unset=True))