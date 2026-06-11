from datetime import datetime
from typing import Literal

from pydantic import AliasChoices, Field

from bola1_api.models import MatchPhase, MatchStatus
from bola1_api.schemas.base import APIModel
from bola1_api.schemas.team import TeamRead

MatchPublicStatus = MatchStatus | Literal["locked"]


class MatchBase(APIModel):
    home_team_id: str
    away_team_id: str
    kickoff_at: datetime
    venue: str
    phase: MatchPhase
    world_cup_group: str | None = Field(
        default=None,
        validation_alias=AliasChoices("world_cup_group", "worldCupGroup", "group"),
        serialization_alias="group",
    )
    status: MatchStatus = MatchStatus.upcoming
    home_score: int | None = None
    away_score: int | None = None


class MatchCreate(MatchBase):
    pass


class MatchUpdate(APIModel):
    home_team_id: str | None = None
    away_team_id: str | None = None
    kickoff_at: datetime | None = None
    venue: str | None = None
    phase: MatchPhase | None = None
    world_cup_group: str | None = Field(
        default=None,
        validation_alias=AliasChoices("world_cup_group", "worldCupGroup", "group"),
        serialization_alias="group",
    )
    status: MatchStatus | None = None


class MatchResultUpdate(APIModel):
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)


class MatchRead(APIModel):
    id: str
    home_team: TeamRead
    away_team: TeamRead
    kickoff_at: datetime
    date: str
    time: str
    venue: str
    phase: MatchPhase
    world_cup_group: str | None = Field(default=None, serialization_alias="group")
    status: MatchPublicStatus
    home_score: int | None = None
    away_score: int | None = None
