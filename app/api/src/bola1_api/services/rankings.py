from sqlalchemy.orm import Session

from bola1_api.repositories import groups as group_repo
from bola1_api.schemas import RankingEntryRead
from bola1_api.services.groups import require_active_member


def get_group_ranking(db: Session, *, group_id: str, user) -> list[RankingEntryRead]:
    require_active_member(db, group_id=group_id, user=user)
    group = group_repo.get_group(db, group_id)
    if not group:
        return []

    active_members = [member for member in group.members if member.banned_at is None]
    sorted_members = sorted(
        active_members,
        key=lambda member: (-member.total_points, -member.exact_scores, -member.correct_winners, member.joined_at),
    )
    return [
        RankingEntryRead(
            position=index + 1,
            user=member.user,
            total_points=member.total_points,
            exact_scores=member.exact_scores,
            correct_winners=member.correct_winners,
            misses=member.misses,
            predictions=member.exact_scores + member.correct_winners + member.misses,
        )
        for index, member in enumerate(sorted_members)
    ]
