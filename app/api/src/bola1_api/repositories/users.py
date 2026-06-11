from sqlalchemy import select
from sqlalchemy.orm import Session

from bola1_api.models import User


def get_user(db: Session, user_id: str) -> User | None:
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email.lower()))


def create_user(db: Session, *, email: str, password_hash: str, nickname: str, avatar: str | None = None) -> User:
    user = User(
        email=email.lower(),
        password_hash=password_hash,
        nickname=nickname,
        avatar=avatar,
    )
    db.add(user)
    db.flush()
    return user
