from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from bola1_api.models import Prediction


def list_predictions_for_match(db: Session, *, group_id: str, match_id: str) -> list[Prediction]:
    return list(
        db.scalars(
            select(Prediction)
            .where(Prediction.group_id == group_id, Prediction.match_id == match_id)
            .options(selectinload(Prediction.user))
            .order_by(Prediction.created_at)
        )
    )


def list_predictions_for_user(db: Session, *, user_id: str) -> list[Prediction]:
    return list(
        db.scalars(
            select(Prediction)
            .where(Prediction.user_id == user_id)
            .options(selectinload(Prediction.user))
            .order_by(Prediction.created_at.desc())
        )
    )


def get_user_prediction(db: Session, *, group_id: str, match_id: str, user_id: str) -> Prediction | None:
    return db.scalar(
        select(Prediction).where(
            Prediction.group_id == group_id,
            Prediction.match_id == match_id,
            Prediction.user_id == user_id,
        )
    )


def list_scored_predictions_for_group(db: Session, *, group_id: str) -> list[Prediction]:
    return list(
        db.scalars(
            select(Prediction).where(
                Prediction.group_id == group_id,
                Prediction.points.is_not(None),
            )
        )
    )
