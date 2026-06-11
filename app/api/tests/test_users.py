from fastapi.testclient import TestClient

from tests.conftest import auth_headers, create_group_for_token, register_and_login, register_user


def test_update_nickname_success(client: TestClient) -> None:
    token = register_and_login(client, email="user@example.com")

    response = client.patch(
        "/api/v1/users/me",
        json={"nickname": "Updated"},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["nickname"] == "Updated"


def test_update_nickname_empty_fails(client: TestClient) -> None:
    token = register_and_login(client, email="user@example.com")

    response = client.patch(
        "/api/v1/users/me",
        json={"nickname": ""},
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_avatar_null_or_absent_serializes_as_empty_string(client: TestClient) -> None:
    body = register_user(client, email="avatar@example.com")
    token = register_and_login(client, email="other@example.com")

    patch_response = client.patch(
        "/api/v1/users/me",
        json={"avatar": None},
        headers=auth_headers(token),
    )

    assert body["avatar"] == ""
    assert patch_response.status_code == 200
    assert patch_response.json()["avatar"] == ""


def test_public_user_dtos_do_not_expose_email(client: TestClient) -> None:
    token = register_and_login(client, email="owner@example.com")
    group = create_group_for_token(client, token)

    members_response = client.get(f"/api/v1/groups/{group['id']}/members", headers=auth_headers(token))
    ranking_response = client.get(f"/api/v1/groups/{group['id']}/ranking", headers=auth_headers(token))

    assert members_response.status_code == 200
    assert ranking_response.status_code == 200
    assert "email" not in members_response.json()[0]["user"]
    assert "email" not in ranking_response.json()[0]["user"]
