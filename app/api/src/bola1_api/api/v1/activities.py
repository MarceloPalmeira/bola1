from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from bola1_api.api.v1.deps import get_current_user
from bola1_api.db.session import get_db
from bola1_api.models import User
from bola1_api.repositories.activities import list_group_activities
from bola1_api.schemas import ActivityEventRead
from bola1_api.services.groups import require_active_member
from bola1_api.services.matches import to_match_read

router = APIRouter(prefix="/groups/{group_id}/activities", tags=["activities"])


@router.get("", response_model=list[ActivityEventRead])
def activities(
    group_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    require_active_member(db, group_id=group_id, user=current_user)
    return [
        ActivityEventRead(
            id=event.id,
            type=event.type,
            user_id=event.user_id,
            user=event.user,
            group_id=event.group_id,
            match_id=event.match_id,
            match=to_match_read(event.match) if event.match else None,
            prediction=event.prediction,
            created_at=event.created_at,
            payload_json=event.payload_json,
        )
        for event in list_group_activities(db, group_id=group_id)
    ]
