from sqlalchemy.orm import Session

from bola1_api.models import ActivityEvent, ActivityEventType


def create_activity(
    db: Session,
    *,
    group_id: str,
    event_type: ActivityEventType | str,
    user_id: str | None = None,
    match_id: str | None = None,
    prediction_id: str | None = None,
    payload: dict | None = None,
) -> ActivityEvent:
    event_type_value = event_type.value if isinstance(event_type, ActivityEventType) else event_type
    event = ActivityEvent(
        group_id=group_id,
        user_id=user_id,
        type=event_type_value,
        match_id=match_id,
        prediction_id=prediction_id,
        payload_json=payload,
    )
    db.add(event)
    db.flush()
    return event
