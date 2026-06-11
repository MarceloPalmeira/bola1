from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from bola1_api.models import GroupMember
from tests.conftest import auth_headers, create_group_for_token, login_user, register_user


def test_ranking_orders_by_points_and_tiebreakers(client: TestClient, db: Session) -> None:
    alpha = register_user(client, email="alpha@example.com", nickname="Alpha")
    beta = register_user(client, email="beta@example.com", nickname="Beta")
    gamma = register_user(client, email="gamma@example.com", nickname="Gamma")
    alpha_token = login_user(client, email="alpha@example.com")
    beta_token = login_user(client, email="beta@example.com")
    gamma_token = login_user(client, email="gamma@example.com")
    group = create_group_for_token(client, alpha_token)
    client.post("/api/v1/groups/join", json={"code": group["code"]}, headers=auth_headers(beta_token))
    client.post("/api/v1/groups/join", json={"code": group["code"]}, headers=auth_headers(gamma_token))

    alpha_member = db.get(GroupMember, {"group_id": group["id"], "user_id": alpha["id"]})
    beta_member = db.get(GroupMember, {"group_id": group["id"], "user_id": beta["id"]})
    gamma_member = db.get(GroupMember, {"group_id": group["id"], "user_id": gamma["id"]})
    assert alpha_member and beta_member and gamma_member
    alpha_member.total_points = 2
    alpha_member.correct_winners = 2
    alpha_member.misses = 1
    beta_member.total_points = 5
    beta_member.exact_scores = 1
    beta_member.correct_winners = 2
    gamma_member.total_points = 5
    gamma_member.exact_scores = 2
    gamma_member.misses = 1
    db.commit()

    response = client.get(f"/api/v1/groups/{group['id']}/ranking", headers=auth_headers(alpha_token))

    assert response.status_code == 200
    ranking = response.json()
    assert [entry["position"] for entry in ranking] == [1, 2, 3]
    assert [entry["user"]["nickname"] for entry in ranking] == ["Gamma", "Beta", "Alpha"]
    assert ranking[0]["totalPoints"] == 5
    assert ranking[0]["exactScores"] == 2
    assert ranking[1]["correctWinners"] == 2
    assert ranking[2]["misses"] == 1


def test_ranking_is_scoped_to_group(client: TestClient, db: Session) -> None:
    owner_a = register_user(client, email="owner-a@example.com", nickname="Owner A")
    owner_b = register_user(client, email="owner-b@example.com", nickname="Owner B")
    token_a = login_user(client, email="owner-a@example.com")
    token_b = login_user(client, email="owner-b@example.com")
    group_a = create_group_for_token(client, token_a, name="Group A")
    group_b = create_group_for_token(client, token_b, name="Group B")
    member_a = db.get(GroupMember, {"group_id": group_a["id"], "user_id": owner_a["id"]})
    member_b = db.get(GroupMember, {"group_id": group_b["id"], "user_id": owner_b["id"]})
    assert member_a and member_b
    member_a.total_points = 1
    member_b.total_points = 99
    db.commit()

    response = client.get(f"/api/v1/groups/{group_a['id']}/ranking", headers=auth_headers(token_a))

    assert response.status_code == 200
    assert [entry["user"]["nickname"] for entry in response.json()] == ["Owner A"]
    assert response.json()[0]["totalPoints"] == 1
