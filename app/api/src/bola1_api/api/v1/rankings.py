from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from bola1_api.api.v1.deps import get_current_user
from bola1_api.db.session import get_db
from bola1_api.models import User
from bola1_api.schemas import RankingEntryRead
from bola1_api.services.rankings import get_group_ranking

router = APIRouter(prefix="/groups/{group_id}/ranking", tags=["rankings"])


@router.get("", response_model=list[RankingEntryRead])
def ranking(group_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_group_ranking(db, group_id=group_id, user=current_user)
