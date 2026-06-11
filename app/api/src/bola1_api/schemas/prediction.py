from datetime import datetime

from pydantic import Field

from bola1_api.models import PredictionResultType
from bola1_api.schemas.base import APIModel
from bola1_api.schemas.user import UserPublic


class PredictionUpsert(APIModel):
    home_score: int = Field(ge=0)
    away_score: int = Field(ge=0)


class PredictionRead(APIModel):
    id: str
    match_id: str
    user_id: str
    user: UserPublic
    group_id: str
    home_score: int
    away_score: int
    points: int | None = None
    result_type: PredictionResultType | None = None
    created_at: datetime
    updated_at: datetime
