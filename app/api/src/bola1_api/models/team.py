from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bola1_api.db.base import Base, IdMixin


class Team(IdMixin, Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(8), unique=True, index=True, nullable=False)
    flag: Mapped[str | None] = mapped_column(String(16))

    home_matches = relationship(
        "Match",
        back_populates="home_team",
        foreign_keys="Match.home_team_id",
    )
    away_matches = relationship(
        "Match",
        back_populates="away_team",
        foreign_keys="Match.away_team_id",
    )
