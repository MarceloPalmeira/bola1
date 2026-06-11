from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from bola1_api.models import Match, Team


def list_matches(db: Session, *, phase: str | None = None, status: str | None = None) -> list[Match]:
    stmt = (
        select(Match)
        .options(selectinload(Match.home_team), selectinload(Match.away_team))
        .order_by(Match.kickoff_at)
    )
    if phase:
        stmt = stmt.where(Match.phase == phase)
    if status:
        stmt = stmt.where(Match.status == status)
    return list(db.scalars(stmt))


def get_match(db: Session, match_id: str) -> Match | None:
    return db.scalar(
        select(Match)
        .where(Match.id == match_id)
        .options(selectinload(Match.home_team), selectinload(Match.away_team))
    )


def get_team(db: Session, team_id: str) -> Team | None:
    return db.get(Team, team_id)


def get_team_by_code(db: Session, code: str) -> Team | None:
    return db.scalar(select(Team).where(Team.code == code.upper()))
