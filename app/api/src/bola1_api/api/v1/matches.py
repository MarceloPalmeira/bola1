from typing import Literal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from bola1_api.db.session import get_db
from bola1_api.models import MatchPhase
from bola1_api.schemas import MatchRead
from bola1_api.services.matches import get_match_read, list_matches

router = APIRouter(prefix="/matches", tags=["matches"])
MatchStatusFilter = Literal["upcoming", "live", "finished", "locked"]


@router.get("", response_model=list[MatchRead])
def get_matches(
    phase: MatchPhase | None = None,
    status: MatchStatusFilter | None = None,
    db: Session = Depends(get_db),
):
    return list_matches(db, phase=phase, status=status)


@router.get("/{match_id}", response_model=MatchRead)
def get_match(match_id: str, db: Session = Depends(get_db)):
    return get_match_read(db, match_id)
