from bola1_api.schemas.base import APIModel


class TeamRead(APIModel):
    id: str
    name: str
    code: str
    flag: str | None = None
