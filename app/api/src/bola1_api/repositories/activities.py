from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from bola1_api.models import ActivityEvent, Match, Prediction


def list_group_activities(db: Session, *, group_id: str, limit: int = 50) -> list[ActivityEvent]:
    return list(
        db.scalars(
            select(ActivityEvent)
            .where(ActivityEvent.group_id == group_id)
            .options(
                selectinload(ActivityEvent.user),
                selectinload(ActivityEvent.match).selectinload(Match.home_team),
                selectinload(ActivityEvent.match).selectinload(Match.away_team),
                selectinload(ActivityEvent.prediction).selectinload(Prediction.user),
            )
            .order_by(ActivityEvent.created_at.desc())
            .limit(limit)
        )
    )
