from collections import Counter

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import auth_headers, create_future_match, create_group_for_token, promote_to_superuser, register_and_login


def test_create_group_generates_join_activity(client: TestClient) -> None:
    token = register_and_login(client, email="owner@example.com")
    group = create_group_for_token(client, token)

    response = client.get(f"/api/v1/groups/{group['id']}/activities", headers=auth_headers(token))

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["type"] == "join"
    assert response.json()[0]["groupId"] == group["id"]
    assert "email" not in response.json()[0]["user"]


def test_join_prediction_edit_and_result_generate_public_activities(client: TestClient, db: Session) -> None:
    admin_email = "admin@example.com"
    admin_token = register_and_login(client, email=admin_email)
    promote_to_superuser(db, email=admin_email)
    member_token = register_and_login(client, email="member@example.com")
    group = create_group_for_token(client, admin_token)
    client.post("/api/v1/groups/join", json={"code": group["code"]}, headers=auth_headers(member_token))
    match = create_future_match(db)
    client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(member_token),
    )
    client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 2, "awayScore": 1},
        headers=auth_headers(member_token),
    )
    client.post(
        f"/api/v1/admin/matches/{match.id}/result",
        json={"homeScore": 2, "awayScore": 1},
        headers=auth_headers(admin_token),
    )

    response = client.get(f"/api/v1/groups/{group['id']}/activities", headers=auth_headers(admin_token))

    assert response.status_code == 200
    activities = response.json()
    counts = Counter(activity["type"] for activity in activities)
    assert set(counts).issubset({"join", "prediction", "result"})
    assert counts["join"] == 2
    assert counts["prediction"] == 2
    assert counts["result"] == 1
    assert any(activity["type"] == "prediction" and activity["prediction"] for activity in activities)
    assert any(activity["type"] == "result" and activity["match"] for activity in activities)


def test_outsider_cannot_list_group_activities(client: TestClient) -> None:
    owner_token = register_and_login(client, email="owner@example.com")
    outsider_token = register_and_login(client, email="outsider@example.com")
    group = create_group_for_token(client, owner_token)

    response = client.get(f"/api/v1/groups/{group['id']}/activities", headers=auth_headers(outsider_token))

    assert response.status_code == 403
