from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests.conftest import auth_headers, promote_to_superuser, register_and_login, register_user


def test_register_user_success_does_not_expose_password_or_create_superuser(client: TestClient) -> None:
    body = register_user(client, email="joao@example.com", nickname="Joao")

    assert body["email"] == "joao@example.com"
    assert body["isSuperuser"] is False
    assert "passwordHash" not in body
    assert "password_hash" not in body


def test_register_duplicate_email_fails(client: TestClient) -> None:
    register_user(client, email="joao@example.com")

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "JOAO@example.com", "password": "secret123", "nickname": "Outro"},
    )

    assert response.status_code == 409


def test_login_success(client: TestClient) -> None:
    register_user(client, email="joao@example.com")

    login_response = client.post("/api/v1/auth/login", json={"email": "joao@example.com", "password": "secret123"})

    assert login_response.status_code == 200
    assert login_response.json()["tokenType"] == "bearer"
    assert login_response.json()["accessToken"]


def test_login_with_wrong_password_fails(client: TestClient) -> None:
    register_user(client, email="joao@example.com")

    response = client.post("/api/v1/auth/login", json={"email": "joao@example.com", "password": "wrong123"})

    assert response.status_code == 401


def test_auth_me_requires_valid_token(client: TestClient) -> None:
    token = register_and_login(client, email="joao@example.com")

    no_token_response = client.get("/api/v1/auth/me")
    invalid_token_response = client.get("/api/v1/auth/me", headers=auth_headers("invalid.token"))
    valid_token_response = client.get("/api/v1/auth/me", headers=auth_headers(token))

    assert no_token_response.status_code == 401
    assert invalid_token_response.status_code == 401
    assert valid_token_response.status_code == 200
    assert valid_token_response.json()["email"] == "joao@example.com"
    assert "passwordHash" not in valid_token_response.json()


def test_admin_endpoint_authorization(client: TestClient, db: Session) -> None:
    common_token = register_and_login(client, email="common@example.com")
    admin_email = "admin@example.com"
    admin_token = register_and_login(client, email=admin_email)
    promote_to_superuser(db, email=admin_email)

    no_token_response = client.post("/api/v1/admin/rankings/recalculate")
    common_user_response = client.post("/api/v1/admin/rankings/recalculate", headers=auth_headers(common_token))
    admin_response = client.post("/api/v1/admin/rankings/recalculate", headers=auth_headers(admin_token))

    assert no_token_response.status_code == 401
    assert common_user_response.status_code == 403
    assert admin_response.status_code == 200
    assert admin_response.json() == {"status": "ok"}
