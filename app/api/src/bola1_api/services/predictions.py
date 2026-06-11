from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from bola1_api.models import ActivityEventType, MatchStatus, Prediction, User
from bola1_api.repositories import matches as match_repo
from bola1_api.repositories import predictions as prediction_repo
from bola1_api.schemas import PredictionUpsert
from bola1_api.services.activities import create_activity
from bola1_api.services.groups import require_active_member
from bola1_api.services.matches import normalize_dt


def ensure_match_open_for_prediction(match) -> None:
    if match.status in {MatchStatus.live.value, MatchStatus.finished.value}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match is locked")
    if normalize_dt(match.kickoff_at) <= datetime.now(UTC):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match is locked")


def list_match_predictions(db: Session, *, group_id: str, match_id: str, user: User) -> list[Prediction]:
    require_active_member(db, group_id=group_id, user=user)
    return prediction_repo.list_predictions_for_match(db, group_id=group_id, match_id=match_id)


def get_my_prediction(db: Session, *, group_id: str, match_id: str, user: User) -> Prediction | None:
    require_active_member(db, group_id=group_id, user=user)
    return prediction_repo.get_user_prediction(db, group_id=group_id, match_id=match_id, user_id=user.id)


def upsert_prediction(
    db: Session,
    *,
    group_id: str,
    match_id: str,
    payload: PredictionUpsert,
    user: User,
) -> Prediction:
    require_active_member(db, group_id=group_id, user=user)
    match = match_repo.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    ensure_match_open_for_prediction(match)

    prediction = prediction_repo.get_user_prediction(
        db,
        group_id=group_id,
        match_id=match_id,
        user_id=user.id,
    )
    if prediction:
        prediction.home_score = payload.home_score
        prediction.away_score = payload.away_score
    else:
        prediction = Prediction(
            group_id=group_id,
            match_id=match_id,
            user_id=user.id,
            home_score=payload.home_score,
            away_score=payload.away_score,
        )
        db.add(prediction)
        db.flush()

    create_activity(
        db,
        group_id=group_id,
        user_id=user.id,
        match_id=match_id,
        prediction_id=prediction.id,
        event_type=ActivityEventType.prediction,
    )
    db.commit()
    db.refresh(prediction)
    return prediction


def list_user_predictions(db: Session, *, user: User) -> list[Prediction]:
    return prediction_repo.list_predictions_for_user(db, user_id=user.id)
