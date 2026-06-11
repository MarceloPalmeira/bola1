from collections.abc import Generator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from bola1_api.core.security import hash_password
from bola1_api.db.base import Base
from bola1_api.db.session import get_db
from bola1_api.main import app
from bola1_api.models import Match, MatchPhase, MatchStatus, Team, User
from bola1_api import models  # noqa: F401

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@event.listens_for(engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture()
def db() -> Generator[Session]:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db: Session) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def register_and_login(client: TestClient, email: str = "user@example.com") -> str:
    register_user(client, email=email)
    return login_user(client, email=email)


def register_user(
    client: TestClient,
    *,
    email: str = "user@example.com",
    password: str = "secret123",
    nickname: str = "User",
    avatar: str | None = None,
) -> dict:
    payload = {"email": email, "password": password, "nickname": nickname}
    if avatar is not None:
        payload["avatar"] = avatar
    response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )
    assert response.status_code == 201
    return response.json()


def login_user(client: TestClient, *, email: str = "user@example.com", password: str = "secret123") -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()["accessToken"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def create_group_for_token(client: TestClient, token: str, name: str = "Test Group") -> dict:
    response = client.post(
        "/api/v1/groups",
        json={"name": name},
        headers=auth_headers(token),
    )
    assert response.status_code == 201
    return response.json()


def create_future_match(db: Session) -> Match:
    home = Team(name="Brasil", code="BRA", flag="🇧🇷")
    away = Team(name="Argentina", code="ARG", flag="🇦🇷")
    db.add_all([home, away])
    db.flush()
    match = Match(
        home_team_id=home.id,
        away_team_id=away.id,
        kickoff_at=datetime.now(UTC) + timedelta(days=1),
        venue="MetLife Stadium",
        phase=MatchPhase.group_stage.value,
        world_cup_group="A",
        status=MatchStatus.upcoming.value,
    )
    db.add(match)
    db.commit()
    return match


def create_match(db: Session, *, kickoff_at: datetime, status: str = MatchStatus.upcoming.value) -> Match:
    home = Team(name=f"Home {kickoff_at.timestamp()}", code=f"H{abs(hash(kickoff_at)) % 999999}", flag="H")
    away = Team(name=f"Away {kickoff_at.timestamp()}", code=f"A{abs(hash((kickoff_at, status))) % 999999}", flag="A")
    db.add_all([home, away])
    db.flush()
    match = Match(
        home_team_id=home.id,
        away_team_id=away.id,
        kickoff_at=kickoff_at,
        venue="Test Stadium",
        phase=MatchPhase.group_stage.value,
        world_cup_group="A",
        status=status,
    )
    if status == MatchStatus.finished.value:
        match.home_score = 1
        match.away_score = 0
    db.add(match)
    db.commit()
    return match


def create_teams(db: Session) -> tuple[Team, Team]:
    home = Team(name="Admin Home", code="ADM1", flag="H")
    away = Team(name="Admin Away", code="ADM2", flag="A")
    db.add_all([home, away])
    db.commit()
    return home, away


def promote_to_superuser(db: Session, *, email: str) -> None:
    user = db.query(User).filter_by(email=email.lower()).one()
    user.is_superuser = True
    db.commit()


def create_superuser(db: Session, *, email: str = "admin@example.com") -> User:
    user = User(
        email=email.lower(),
        password_hash=hash_password("secret123"),
        nickname="Admin",
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
