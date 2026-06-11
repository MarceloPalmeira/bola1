from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from bola1_api.api.v1.deps import get_current_user
from bola1_api.db.session import get_db
from bola1_api.models import Match, MatchStatus, User
from bola1_api.schemas import MatchCreate, MatchRead, MatchResultUpdate, MatchUpdate
from bola1_api.services.football_api import FootballApiCooldown, FootballApiError, FootballApiNotConfigured, sync_matches
from bola1_api.services.matches import create_match, register_result, require_superuser, update_match
from bola1_api.services.scoring import recalculate_match_points

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/matches", response_model=MatchRead, status_code=status.HTTP_201_CREATED)
def post_match(payload: MatchCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_match(db, payload=payload, user=current_user)


@router.patch("/matches/{match_id}", response_model=MatchRead)
def patch_match(
    match_id: str,
    payload: MatchUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return update_match(db, match_id=match_id, payload=payload, user=current_user)


@router.post("/matches/{match_id}/result", response_model=MatchRead)
def post_match_result(
    match_id: str,
    payload: MatchResultUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return register_result(db, match_id=match_id, payload=payload, user=current_user)


@router.post("/rankings/recalculate")
def recalculate_rankings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> dict[str, str]:
    require_superuser(current_user)
    for match in db.query(Match).filter_by(status=MatchStatus.finished.value):
        recalculate_match_points(db, match=match)
    db.commit()
    return {"status": "ok"}


@router.post("/matches/sync")
def sync_matches_from_api(
    competition_id: str = "2000",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    """Pull live match data from the external football API and upsert into the DB.

    Requires FOOTBALL_API_BASE_URL and FOOTBALL_API_KEY to be set.
    competition_id defaults to 2000 (FIFA World Cup on football-data.org).
    """
    require_superuser(current_user)
    try:
        result = sync_matches(db, competition_id=competition_id)
        db.commit()
        return {"status": "ok", **result}
    except FootballApiNotConfigured as exc:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(exc))
    except FootballApiCooldown as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(exc))
    except FootballApiError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
