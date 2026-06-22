from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bola1_api.db.base import Base, IdMixin, TimestampMixin
from bola1_api.models.enums import MatchPhase, MatchStatus


class Match(IdMixin, TimestampMixin, Base):
    __tablename__ = "matches"
    __table_args__ = (
        CheckConstraint("home_team_id <> away_team_id", name="ck_matches_distinct_teams"),
        CheckConstraint(
            "phase IN ('group-stage', 'round-of-16', 'quarter-finals', 'semi-finals', 'final')",
            name="ck_matches_phase",
        ),
        CheckConstraint("status IN ('upcoming', 'live', 'finished')", name="ck_matches_status"),
        CheckConstraint("home_score IS NULL OR home_score >= 0", name="ck_matches_home_score_non_negative"),
        CheckConstraint("away_score IS NULL OR away_score >= 0", name="ck_matches_away_score_non_negative"),
    )

    home_team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"), nullable=False)
    away_team_id: Mapped[str] = mapped_column(ForeignKey("teams.id"), nullable=False)
    # Raw match id from the external football data provider. Stable across
    # reschedules, unlike (teams, kickoff_at) — used as the primary upsert key
    # during sync to avoid duplicating fixtures whose kickoff time shifts.
    external_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)
    kickoff_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    venue: Mapped[str] = mapped_column(String(255), nullable=False)
    phase: Mapped[str] = mapped_column(
        String(40),
        default=MatchPhase.group_stage.value,
        server_default=text("'group-stage'"),
        nullable=False,
    )
    world_cup_group: Mapped[str | None] = mapped_column(String(8))
    status: Mapped[str] = mapped_column(
        String(20),
        default=MatchStatus.upcoming.value,
        server_default=text("'upcoming'"),
        nullable=False,
    )
    home_score: Mapped[int | None] = mapped_column(Integer)
    away_score: Mapped[int | None] = mapped_column(Integer)

    home_team = relationship("Team", back_populates="home_matches", foreign_keys=[home_team_id])
    away_team = relationship("Team", back_populates="away_matches", foreign_keys=[away_team_id])
    predictions = relationship("Prediction", back_populates="match")
    activities = relationship("ActivityEvent", back_populates="match")
