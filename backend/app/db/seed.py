import uuid

from sqlalchemy import select

from app.core.config import settings
from app.db.models import User
from app.db.session import SessionLocal


def seed() -> None:
    dev_id = uuid.UUID(settings.dev_user_id)
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.id == dev_id))
        if existing:
            print("Dev user already exists.")
            return
        db.add(User(id=dev_id, email="dev@prepai.local", display_name="Dev Student"))
        db.commit()
        print("Dev user created.")


if __name__ == "__main__":
    seed()