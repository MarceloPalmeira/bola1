from bola1_api.schemas.base import APIModel
from bola1_api.schemas.user import UserPublic


class RankingEntryRead(APIModel):
    position: int
    user: UserPublic
    total_points: int
    exact_scores: int
    correct_winners: int
    misses: int
    predictions: int
