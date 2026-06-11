from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from bola1_api.models import MatchStatus
from tests.conftest import (
    auth_headers,
    create_group_for_token,
    create_match,
    create_teams,
    promote_to_superuser,
    register_and_login,
)


def match_payload(home_team_id: str, away_team_id: str) -> dict[str, object]:
    return {
        "homeTeamId": home_team_id,
        "awayTeamId": away_team_id,
        "kickoffAt": (datetime.now(UTC) + timedelta(days=3)).isoformat(),
        "venue": "MetLife Stadium",
        "phase": "group-stage",
        "group": "A",
    }


def test_match_status_filter_respects_locked_status(client: TestClient, db: Session) -> None:
    future = create_match(db, kickoff_at=datetime.now(UTC) + timedelta(days=1))
    locked = create_match(db, kickoff_at=datetime.now(UTC) - timedelta(days=1))
    finished = create_match(
        db,
        kickoff_at=datetime.now(UTC) - timedelta(days=2),
        status=MatchStatus.finished.value,
    )

    upcoming_response = client.get("/api/v1/matches?status=upcoming")
    locked_response = client.get("/api/v1/matches?status=locked")
    finished_response = client.get("/api/v1/matches?status=finished")

    assert upcoming_response.status_code == 200
    assert [match["id"] for match in upcoming_response.json()] == [future.id]
    assert [match["id"] for match in locked_response.json()] == [locked.id]
    assert [match["id"] for match in finished_response.json()] == [finished.id]


def test_list_and_get_matches(client: TestClient, db: Session) -> None:
    match = create_match(db, kickoff_at=datetime.now(UTC) + timedelta(days=1))

    list_response = client.get("/api/v1/matches")
    get_response = client.get(f"/api/v1/matches/{match.id}")
    missing_response = client.get("/api/v1/matches/missing")

    assert list_response.status_code == 200
    assert [item["id"] for item in list_response.json()] == [match.id]
    assert get_response.status_code == 200
    assert get_response.json()["id"] == match.id
    assert missing_response.status_code == 404


def test_match_filters_reject_invalid_enum_values(client: TestClient) -> None:
    assert client.get("/api/v1/matches?status=invalid").status_code == 422
    assert client.get("/api/v1/matches?phase=invalid").status_code == 422


def test_admin_match_endpoint_requires_token(client: TestClient, db: Session) -> None:
    home, away = create_teams(db)

    response = client.post("/api/v1/admin/matches", json=match_payload(home.id, away.id))

    assert response.status_code == 401


def test_admin_match_endpoint_rejects_common_user(client: TestClient, db: Session) -> None:
    token = register_and_login(client)
    home, away = create_teams(db)

    response = client.post(
        "/api/v1/admin/matches",
        json=match_payload(home.id, away.id),
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_admin_match_endpoint_accepts_superuser(client: TestClient, db: Session) -> None:
    email = "admin@example.com"
    token = register_and_login(client, email=email)
    promote_to_superuser(db, email=email)
    home, away = create_teams(db)

    response = client.post(
        "/api/v1/admin/matches",
        json=match_payload(home.id, away.id),
        headers=auth_headers(token),
    )

    assert response.status_code == 201
    assert response.json()["date"]
    assert response.json()["time"]


def test_admin_match_rejects_invalid_phase_and_status(client: TestClient, db: Session) -> None:
    email = "admin@example.com"
    token = register_and_login(client, email=email)
    promote_to_superuser(db, email=email)
    home, away = create_teams(db)

    invalid_phase = match_payload(home.id, away.id) | {"phase": "invalid"}
    invalid_status = match_payload(home.id, away.id) | {"status": "invalid"}

    assert client.post("/api/v1/admin/matches", json=invalid_phase, headers=auth_headers(token)).status_code == 422
    assert client.post("/api/v1/admin/matches", json=invalid_status, headers=auth_headers(token)).status_code == 422


def test_admin_match_rejects_unknown_team(client: TestClient, db: Session) -> None:
    email = "admin@example.com"
    token = register_and_login(client, email=email)
    promote_to_superuser(db, email=email)
    home, _ = create_teams(db)

    response = client.post(
        "/api/v1/admin/matches",
        json=match_payload(home.id, "missing-team-id"),
        headers=auth_headers(token),
    )

    assert response.status_code == 400


def test_admin_match_rejects_same_team_on_create_and_update(client: TestClient, db: Session) -> None:
    email = "admin@example.com"
    token = register_and_login(client, email=email)
    promote_to_superuser(db, email=email)
    home, away = create_teams(db)
    headers = auth_headers(token)

    create_response = client.post(
        "/api/v1/admin/matches",
        json=match_payload(home.id, home.id),
        headers=headers,
    )
    ok_response = client.post(
        "/api/v1/admin/matches",
        json=match_payload(home.id, away.id),
        headers=headers,
    )
    update_response = client.patch(
        f"/api/v1/admin/matches/{ok_response.json()['id']}",
        json={"awayTeamId": home.id},
        headers=headers,
    )

    assert create_response.status_code == 400
    assert ok_response.status_code == 201
    assert update_response.status_code == 400


def test_common_user_cannot_register_result(client: TestClient, db: Session) -> None:
    token = register_and_login(client)
    match = create_match(db, kickoff_at=datetime.now(UTC) + timedelta(days=1))

    response = client.post(
        f"/api/v1/admin/matches/{match.id}/result",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(token),
    )

    assert response.status_code == 403


def test_register_result_as_superuser_recalculates_prediction_points(client: TestClient, db: Session) -> None:
    admin_email = "admin@example.com"
    token = register_and_login(client, email=admin_email)
    promote_to_superuser(db, email=admin_email)
    group = create_group_for_token(client, token)
    match = create_match(db, kickoff_at=datetime.now(UTC) + timedelta(days=1))
    client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(token),
    )

    result_response = client.post(
        f"/api/v1/admin/matches/{match.id}/result",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(token),
    )
    prediction_response = client.get(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction/me",
        headers=auth_headers(token),
    )

    assert result_response.status_code == 200
    assert result_response.json()["status"] == "finished"
    assert prediction_response.status_code == 200
    assert prediction_response.json()["points"] == 3
