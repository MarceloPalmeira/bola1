from datetime import datetime

from pydantic import Field

from bola1_api.models import GroupRole
from bola1_api.schemas.base import APIModel
from bola1_api.schemas.user import UserPublic


class GroupCreate(APIModel):
    name: str = Field(min_length=1, max_length=120)


class GroupJoin(APIModel):
    code: str = Field(min_length=1, max_length=32)


class GroupMemberRead(APIModel):
    user_id: str
    user: UserPublic
    role: GroupRole
    joined_at: datetime
    total_points: int
    exact_scores: int
    correct_winners: int
    misses: int


class GroupRead(APIModel):
    id: str
    name: str
    code: str
    invite_link: str
    created_by_id: str = Field(serialization_alias="createdBy")
    created_at: datetime
    members: list[GroupMemberRead] = Field(default_factory=list)
