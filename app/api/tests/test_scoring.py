from fastapi.testclient import TestClient
import pytest
from sqlalchemy.orm import Session

from bola1_api.models import PredictionResultType
from bola1_api.services.scoring import score_prediction
from tests.conftest import auth_headers, create_future_match, create_group_for_token, promote_to_superuser, register_and_login


@pytest.mark.parametrize(
    ("predicted", "actual", "expected_points", "expected_result_type"),
    [
        ((2, 1), (2, 1), 3, PredictionResultType.exact),
        ((0, 0), (0, 0), 3, PredictionResultType.exact),
        ((0, 0), (1, 1), 1, PredictionResultType.winner),
        ((2, 1), (1, 0), 1, PredictionResultType.winner),
        ((1, 2), (2, 1), 0, PredictionResultType.miss),
    ],
)
def test_score_prediction_scenarios(
    predicted: tuple[int, int],
    actual: tuple[int, int],
    expected_points: int,
    expected_result_type: PredictionResultType,
) -> None:
    points, result_type = score_prediction(
        predicted_home=predicted[0],
        predicted_away=predicted[1],
        actual_home=actual[0],
        actual_away=actual[1],
    )

    assert points == expected_points
    assert result_type == expected_result_type


def test_result_change_recalculates_points_and_member_stats(client: TestClient, db: Session) -> None:
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
        headers=auth_headers(admin_token),
    )
    client.put(
        f"/api/v1/groups/{group['id']}/matches/{match.id}/prediction",
        json={"homeScore": 0, "awayScore": 0},
        headers=auth_headers(member_token),
    )

    client.post(
        f"/api/v1/admin/matches/{match.id}/result",
        json={"homeScore": 1, "awayScore": 0},
        headers=auth_headers(admin_token),
    )
    first_ranking = client.get(f"/api/v1/groups/{group['id']}/ranking", headers=auth_headers(admin_token)).json()

    client.post(
        f"/api/v1/admin/matches/{match.id}/result",
        json={"homeScore": 0, "awayScore": 0},
        headers=auth_headers(admin_token),
    )
    second_ranking = client.get(f"/api/v1/groups/{group['id']}/ranking", headers=auth_headers(admin_token)).json()

    assert first_ranking[0]["user"]["nickname"] == "User"
    assert first_ranking[0]["totalPoints"] == 3
    assert first_ranking[0]["exactScores"] == 1
    assert first_ranking[1]["misses"] == 1
    assert second_ranking[0]["totalPoints"] == 3
    assert second_ranking[0]["exactScores"] == 1
    assert second_ranking[1]["totalPoints"] == 0
    assert second_ranking[1]["misses"] == 1
