from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from bola1_api.models import GroupMember
from tests.conftest import auth_headers, create_future_match, create_group_for_token, register_and_login, register_user


def test_create_group_adds_creator_as_admin(client: TestClient) -> None:
    token = register_and_login(client)
    me = client.get("/api/v1/users/me", headers=auth_headers(token)).json()
    response = client.post("/api/v1/groups", json={"name": "Bolao da Firma"}, headers=auth_headers(token))

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Bolao da Firma"
    assert body["code"]
    assert body["createdBy"] == me["id"]
    assert body["members"][0]["role"] == "admin"


def test_group_codes_are_unique(client: TestClient) -> None:
    token = register_and_login(client)

    first = create_group_for_token(client, token, name="Group 1")
    second = create_group_for_token(client, token, name="Group 2")

    assert first["code"] != second["code"]


def test_join_group_by_code_and_joining_twice_does_not_duplicate_membership(client: TestClient) -> None:
    owner_token = register_and_login(client, email="owner@example.com")
    member_token = register_and_login(client, email="member@example.com")
    group = create_group_for_token(client, owner_token)

    first_join = client.post("/api/v1/groups/join", json={"code": group["code"]}, headers=auth_headers(member_token))
    second_join = client.post("/api/v1/groups/join", json={"code": group["code"]}, headers=auth_headers(member_token))
    members = client.get(f"/api/v1/groups/{group['id']}/members", headers=auth_headers(owner_token))

    assert first_join.status_code == 200
    assert second_join.status_code == 200
    assert members.status_code == 200
    assert len(members.json()) == 2


def test_join_group_with_unknown_code_fails(client: TestClient) -> None:
    token = register_and_login(client)

    response = client.post("/api/v1/groups/join", json={"code": "missing"}, headers=auth_headers(token))

    assert response.status_code == 404


def test_outsider_cannot_access_private_group_data(client: TestClient) -> None:
    owner_token = register_and_login(client, email="owner@example.com")
    outsider_token = register_and_login(client, email="outsider@example.com")
    group = create_group_for_token(client, owner_token)

    group_response = client.get(f"/api/v1/groups/{group['id']}", headers=auth_headers(outsider_token))
    members_response = client.get(f"/api/v1/groups/{group['id']}/members", headers=auth_headers(outsider_token))
    activities_response = client.get(f"/api/v1/groups/{group['id']}/activities", headers=auth_headers(outsider_token))

    assert group_response.status_code == 403
    assert members_response.status_code == 403
    assert activities_response.status_code == 403


def test_removed_member_cannot_access_sensitive_actions_and_membership_history_remains(
    client: TestClient,
    db: Session,
) -> None:
    owner_token = register_and_login(client, email="owner@example.com")
    member_token = register_and_login(client, email="member@example.com")
    group = create_group_for_token(client, owner_token)
    client.post("/api/v1/groups/join", json={"code": group["code"]}, headers=auth_headers(member_token))
    member = client.get("/api/v1/users/me", headers=auth_headers(member_token)).json()
    match = create_future_match(db)

    remove_response = client.delete(
        f"/api/v1/groups/{group['id']}/members/{member['id']}",
        headers=auth_headers(owner_token),
    )
    prediction_response = client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(member_token),
    )
    group_response = client.get(f"/api/v1/groups/{group['id']}", headers=auth_headers(member_token))
    active_members_response = client.get(f"/api/v1/groups/{group['id']}/members", headers=auth_headers(owner_token))
    membership = db.get(GroupMember, {"group_id": group["id"], "user_id": member["id"]})

    assert remove_response.status_code == 204
    assert prediction_response.status_code == 403
    assert group_response.status_code == 403
    assert active_members_response.status_code == 200
    assert [item["userId"] for item in active_members_response.json()] == [group["createdBy"]]
    assert membership is not None
    assert membership.banned_at is not None


def test_invalid_group_role_fails_database_constraint(client: TestClient, db: Session) -> None:
    owner_token = register_and_login(client, email="owner@example.com")
    user = register_user(client, email="member@example.com")
    group = create_group_for_token(client, owner_token)
    db.add(
        GroupMember(
            group_id=group["id"],
            user_id=user["id"],
            role="owner",
            joined_at=datetime.now(UTC),
        )
    )

    with pytest.raises(IntegrityError):
        db.commit()

    db.rollback()
