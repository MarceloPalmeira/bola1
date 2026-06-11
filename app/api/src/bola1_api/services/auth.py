from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from bola1_api.core.security import create_access_token, hash_password, verify_password
from bola1_api.models import User
from bola1_api.repositories import users as user_repo
from bola1_api.schemas import LoginRequest, RegisterRequest


def register_user(db: Session, payload: RegisterRequest) -> User:
    if user_repo.get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = user_repo.create_user(
        db,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        nickname=payload.nickname,
        avatar=payload.avatar,
    )
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: LoginRequest) -> User:
    user = user_repo.get_user_by_email(db, str(payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return user


def login_user(db: Session, payload: LoginRequest) -> str:
    user = authenticate_user(db, payload)
    return create_access_token(user.id)
