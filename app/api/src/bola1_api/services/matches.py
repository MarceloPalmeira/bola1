from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from bola1_api.models import ActivityEventType, Match, MatchStatus, User
from bola1_api.repositories import matches as match_repo
from bola1_api.schemas import MatchCreate, MatchRead, MatchResultUpdate, MatchUpdate
from bola1_api.services.activities import create_activity
from bola1_api.services.scoring import recalculate_match_points


def require_superuser(user: User) -> None:
    if not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permission required")


def normalize_dt(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value


def public_match_status(match: Match) -> str:
    if match.status in {MatchStatus.finished.value, MatchStatus.live.value}:
        return match.status
    if normalize_dt(match.kickoff_at) <= datetime.now(UTC):
        return "locked"
    return MatchStatus.upcoming.value


def to_match_read(match: Match) -> MatchRead:
    kickoff_at = normalize_dt(match.kickoff_at)
    return MatchRead(
        id=match.id,
        home_team=match.home_team,
        away_team=match.away_team,
        kickoff_at=match.kickoff_at,
        date=kickoff_at.date().isoformat(),
        time=kickoff_at.strftime("%H:%M"),
        venue=match.venue,
        phase=match.phase,
        world_cup_group=match.world_cup_group,
        status=public_match_status(match),
        home_score=match.home_score,
        away_score=match.away_score,
    )


def list_matches(db: Session, *, phase: str | None = None, status: str | None = None) -> list[MatchRead]:
    matches = match_repo.list_matches(db, phase=phase)
    reads = [to_match_read(match) for match in matches]
    if status:
        return [match for match in reads if match.status == status]
    return reads


def get_match_read(db: Session, match_id: str) -> MatchRead:
    match = match_repo.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")
    return to_match_read(match)


def validate_match_teams(db: Session, *, home_team_id: str, away_team_id: str) -> None:
    if home_team_id == away_team_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Match teams must be different")
    if not match_repo.get_team(db, home_team_id) or not match_repo.get_team(db, away_team_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid team")


def create_match(db: Session, *, payload: MatchCreate, user: User) -> MatchRead:
    require_superuser(user)
    validate_match_teams(db, home_team_id=payload.home_team_id, away_team_id=payload.away_team_id)

    match = Match(**payload.model_dump())
    db.add(match)
    db.commit()
    return get_match_read(db, match.id)


def update_match(db: Session, *, match_id: str, payload: MatchUpdate, user: User) -> MatchRead:
    require_superuser(user)
    match = match_repo.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    changes = payload.model_dump(exclude_unset=True)
    home_team_id = changes.get("home_team_id", match.home_team_id)
    away_team_id = changes.get("away_team_id", match.away_team_id)
    if "home_team_id" in changes or "away_team_id" in changes:
        validate_match_teams(db, home_team_id=home_team_id, away_team_id=away_team_id)

    for field, value in changes.items():
        setattr(match, field, value)
    db.commit()
    return get_match_read(db, match.id)


def register_result(db: Session, *, match_id: str, payload: MatchResultUpdate, user: User) -> MatchRead:
    require_superuser(user)
    match = match_repo.get_match(db, match_id)
    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Match not found")

    match.home_score = payload.home_score
    match.away_score = payload.away_score
    match.status = MatchStatus.finished.value
    recalculate_match_points(db, match=match)

    group_ids = {prediction.group_id for prediction in match.predictions}
    for group_id in group_ids:
        create_activity(
            db,
            group_id=group_id,
            user_id=user.id,
            match_id=match.id,
            event_type=ActivityEventType.result,
        )

    db.commit()
    return get_match_read(db, match.id)
