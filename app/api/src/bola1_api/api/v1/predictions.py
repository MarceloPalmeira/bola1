from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from bola1_api.api.v1.deps import get_current_user
from bola1_api.db.session import get_db
from bola1_api.models import User
from bola1_api.schemas import PredictionRead, PredictionUpsert
from bola1_api.services.predictions import get_my_prediction, list_match_predictions, upsert_prediction

router = APIRouter(tags=["predictions"])


@router.get("/groups/{group_id}/matches/{match_id}/predictions", response_model=list[PredictionRead])
def get_predictions(
    group_id: str,
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_match_predictions(db, group_id=group_id, match_id=match_id, user=current_user)


@router.get("/groups/{group_id}/matches/{match_id}/prediction/me", response_model=PredictionRead)
def get_prediction_me(
    group_id: str,
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    prediction = get_my_prediction(db, group_id=group_id, match_id=match_id, user=current_user)
    if not prediction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    return prediction


@router.put("/groups/{group_id}/matches/{match_id}/prediction", response_model=PredictionRead)
def put_prediction(
    group_id: str,
    match_id: str,
    payload: PredictionUpsert,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return upsert_prediction(db, group_id=group_id, match_id=match_id, payload=payload, user=current_user)
