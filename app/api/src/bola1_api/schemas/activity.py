from datetime import datetime

from bola1_api.models import ActivityEventType
from bola1_api.schemas.base import APIModel
from bola1_api.schemas.match import MatchRead
from bola1_api.schemas.prediction import PredictionRead
from bola1_api.schemas.user import UserPublic


class ActivityEventRead(APIModel):
    id: str
    type: ActivityEventType
    user_id: str | None = None
    user: UserPublic | None = None
    group_id: str
    match_id: str | None = None
    match: MatchRead | None = None
    prediction: PredictionRead | None = None
    created_at: datetime
    payload_json: dict | None = None
