from pydantic import EmailStr, Field

from bola1_api.schemas.base import APIModel
from bola1_api.schemas.user import UserRead


class RegisterRequest(APIModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nickname: str = Field(min_length=1, max_length=80)
    avatar: str | None = None


class LoginRequest(APIModel):
    email: EmailStr
    password: str


class TokenResponse(APIModel):
    access_token: str
    token_type: str = "bearer"


class AuthMeResponse(UserRead):
    pass
