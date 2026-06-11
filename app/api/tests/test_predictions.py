from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from bola1_api.models import MatchStatus, Prediction
from tests.conftest import auth_headers, create_future_match, create_group_for_token, create_match, promote_to_superuser, register_and_login


def test_create_zero_zero_prediction(client: TestClient, db: Session) -> None:
    token = register_and_login(client)
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Bolao 0x0"},
        headers=auth_headers(token),
    )
    match = create_future_match(db)

    response = client.put(
        f"/api/v1/groups/{group_response.json()['id']}/matches/{match.id}/prediction",
        json={"homeScore": 0, "awayScore": 0},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["homeScore"] == 0
    assert response.json()["awayScore"] == 0


def test_edit_prediction_before_kickoff_updates_same_record_and_is_visible(client: TestClient, db: Session) -> None:
    token = register_and_login(client)
    group = create_group_for_token(client, token)
    match = create_future_match(db)

    first_response = client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(token),
    )
    second_response = client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 2, "awayScore": 1},
        headers=auth_headers(token),
    )
    list_response = client.get(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/predictions",
        headers=auth_headers(token),
    )
    me_response = client.get(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction/me",
        headers=auth_headers(token),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["id"] == second_response.json()["id"]
    assert second_response.json()["homeScore"] == 2
    assert second_response.json()["awayScore"] == 1
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1
    assert me_response.status_code == 200
    assert me_response.json()["homeScore"] == 2
    assert db.query(Prediction).count() == 1


def test_prediction_is_blocked_after_kickoff(client: TestClient, db: Session) -> None:
    token = register_and_login(client)
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Bolao fechado"},
        headers=auth_headers(token),
    )
    match = create_match(db, kickoff_at=datetime.now(UTC) - timedelta(minutes=1))

    response = client.put(
        f"/api/v1/groups/{group_response.json()['id']}/matches/{match.id}/prediction",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(token),
    )

    assert response.status_code == 400


@pytest.mark.parametrize("match_status", [MatchStatus.live.value, MatchStatus.finished.value])
def test_prediction_is_blocked_for_live_or_finished_match(
    client: TestClient,
    db: Session,
    match_status: str,
) -> None:
    token = register_and_login(client)
    group = create_group_for_token(client, token)
    match = create_match(db, kickoff_at=datetime.now(UTC) + timedelta(days=1), status=match_status)

    response = client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(token),
    )

    assert response.status_code == 400


def test_prediction_requires_group_membership(client: TestClient, db: Session) -> None:
    owner_token = register_and_login(client, email="owner@example.com")
    outsider_token = register_and_login(client, email="outsider@example.com")
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Bolao privado"},
        headers=auth_headers(owner_token),
    )
    match = create_future_match(db)

    response = client.put(
        f"/api/v1/groups/{group_response.json()['id']}/matches/{match.id}/prediction",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(outsider_token),
    )

    assert response.status_code == 403


def test_prediction_is_blocked_for_banned_member(client: TestClient, db: Session) -> None:
    owner_token = register_and_login(client, email="owner@example.com")
    member_token = register_and_login(client, email="member@example.com")
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Bolao com ban"},
        headers=auth_headers(owner_token),
    )
    group = group_response.json()
    client.post("/api/v1/groups/join", json={"code": group["code"]}, headers=auth_headers(member_token))
    member = client.get("/api/v1/users/me", headers=auth_headers(member_token)).json()
    client.delete(
        f"/api/v1/groups/{group['id']}/members/{member['id']}",
        headers=auth_headers(owner_token),
    )
    match = create_future_match(db)

    response = client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(member_token),
    )

    assert response.status_code == 403


def test_prediction_unique_constraint_prevents_duplicate_rows(client: TestClient, db: Session) -> None:
    token = register_and_login(client)
    user = client.get("/api/v1/users/me", headers=auth_headers(token)).json()
    group = create_group_for_token(client, token)
    match = create_future_match(db)
    client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(token),
    )
    db.add(
        Prediction(
            group_id=group["id"],
            match_id=match.id,
            user_id=user["id"],
            home_score=2,
            away_score=1,
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()


@pytest.mark.parametrize(
    ("predicted", "actual", "expected_points", "expected_result_type"),
    [
        ((0, 0), (0, 0), 3, "exact"),
        ((1, 1), (0, 0), 1, "winner"),
        ((2, 1), (1, 0), 1, "winner"),
        ((0, 1), (1, 0), 0, "miss"),
    ],
)
def test_prediction_scoring_cases_after_result(
    client: TestClient,
    db: Session,
    predicted: tuple[int, int],
    actual: tuple[int, int],
    expected_points: int,
    expected_result_type: str,
) -> None:
    admin_email = "admin@example.com"
    token = register_and_login(client, email=admin_email)
    promote_to_superuser(db, email=admin_email)
    group = create_group_for_token(client, token)
    match = create_future_match(db)
    client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": predicted[0], "awayScore": predicted[1]},
        headers=auth_headers(token),
    )

    client.post(
        f"/api/v1/admin/matches/{match.id}/result",
        json={"homeScore": actual[0], "awayScore": actual[1]},
        headers=auth_headers(token),
    )
    response = client.get(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction/me",
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["points"] == expected_points
    assert response.json()["resultType"] == expected_result_type


def test_result_recalculates_points_and_ranking_for_zero_zero_draw(client: TestClient, db: Session) -> None:
    admin_email = "admin@example.com"
    admin_token = register_and_login(client, email=admin_email)
    promote_to_superuser(db, email=admin_email)
    member_token = register_and_login(client, email="member@example.com")
    group_response = client.post(
        "/api/v1/groups",
        json={"name": "Bolao ranking"},
        headers=auth_headers(admin_token),
    )
    group = group_response.json()
    client.post("/api/v1/groups/join", json={"code": group["code"]}, headers=auth_headers(member_token))
    match = create_future_match(db)

    client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 0, "awayScore": 0},
        headers=auth_headers(admin_token),
    )
    client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 1, "awayScore": 1},
        headers=auth_headers(member_token),
    )
    result_response = client.post(
        f"/api/v1/admin/matches/{match.id}/result",
        json={"homeScore": 0, "awayScore": 0},
        headers=auth_headers(admin_token),
    )
    ranking_response = client.get(f"/api/v1/groups/{group['id']}/ranking", headers=auth_headers(admin_token))

    assert result_response.status_code == 200
    assert ranking_response.status_code == 200
    ranking = ranking_response.json()
    assert ranking[0]["totalPoints"] == 3
    assert ranking[0]["exactScores"] == 1
    assert ranking[1]["totalPoints"] == 1
    assert ranking[1]["correctWinners"] == 1
