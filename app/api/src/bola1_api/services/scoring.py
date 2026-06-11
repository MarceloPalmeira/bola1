from sqlalchemy.orm import Session

from bola1_api.models import GroupMember, Match, Prediction, PredictionResultType
from bola1_api.repositories.predictions import list_scored_predictions_for_group


def outcome(home_score: int, away_score: int) -> int:
    if home_score > away_score:
        return 1
    if home_score < away_score:
        return -1
    return 0


def score_prediction(
    *,
    predicted_home: int,
    predicted_away: int,
    actual_home: int,
    actual_away: int,
) -> tuple[int, PredictionResultType]:
    if predicted_home == actual_home and predicted_away == actual_away:
        return 3, PredictionResultType.exact
    if outcome(predicted_home, predicted_away) == outcome(actual_home, actual_away):
        return 1, PredictionResultType.winner
    return 0, PredictionResultType.miss


def recalculate_group_member_stats(db: Session, *, group_id: str) -> None:
    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    for member in members:
        member.total_points = 0
        member.exact_scores = 0
        member.correct_winners = 0
        member.misses = 0

    by_user = {member.user_id: member for member in members}
    for prediction in list_scored_predictions_for_group(db, group_id=group_id):
        member = by_user.get(prediction.user_id)
        if not member:
            continue
        member.total_points += prediction.points or 0
        if prediction.result_type == PredictionResultType.exact.value:
            member.exact_scores += 1
        elif prediction.result_type == PredictionResultType.winner.value:
            member.correct_winners += 1
        elif prediction.result_type == PredictionResultType.miss.value:
            member.misses += 1


def recalculate_match_points(db: Session, *, match: Match) -> None:
    if match.home_score is None or match.away_score is None:
        return

    affected_group_ids: set[str] = set()
    for prediction in match.predictions:
        points, result_type = score_prediction(
            predicted_home=prediction.home_score,
            predicted_away=prediction.away_score,
            actual_home=match.home_score,
            actual_away=match.away_score,
        )
        prediction.points = points
        prediction.result_type = result_type.value
        affected_group_ids.add(prediction.group_id)

    db.flush()
    for group_id in affected_group_ids:
        recalculate_group_member_stats(db, group_id=group_id)
