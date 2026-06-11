from datetime import datetime

from pydantic import EmailStr, Field, field_validator

from bola1_api.schemas.base import APIModel


class UserRead(APIModel):
    id: str
    email: EmailStr
    nickname: str
    avatar: str = ""
    is_superuser: bool = False
    created_at: datetime

    @field_validator("avatar", mode="before")
    @classmethod
    def default_avatar(cls, value: str | None) -> str:
        return value or ""


class UserUpdate(APIModel):
    nickname: str | None = Field(default=None, min_length=1, max_length=80)
    avatar: str | None = None


class UserPublic(APIModel):
    id: str
    nickname: str
    avatar: str = ""
    created_at: datetime

    @field_validator("avatar", mode="before")
    @classmethod
    def default_avatar(cls, value: str | None) -> str:
        return value or ""
