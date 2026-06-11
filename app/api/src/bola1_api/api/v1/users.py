from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from bola1_api.api.v1.deps import get_current_user
from bola1_api.db.session import get_db
from bola1_api.models import User
from bola1_api.schemas import PredictionRead, UserRead, UserUpdate
from bola1_api.services.predictions import list_user_predictions

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.patch("/me", response_model=UserRead)
def update_me(payload: UserUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    if payload.nickname is not None:
        current_user.nickname = payload.nickname
    if payload.avatar is not None:
        current_user.avatar = payload.avatar
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/me/predictions", response_model=list[PredictionRead])
def get_my_predictions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_user_predictions(db, user=current_user)
