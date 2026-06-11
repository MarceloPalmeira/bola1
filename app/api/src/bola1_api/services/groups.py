from secrets import token_hex

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from bola1_api.models import ActivityEventType, Group, GroupMember, GroupRole, User
from bola1_api.repositories import groups as group_repo
from bola1_api.schemas import GroupCreate, GroupJoin
from bola1_api.services.activities import create_activity


def generate_group_code(db: Session) -> str:
    while True:
        code = token_hex(4).upper()
        if not group_repo.get_group_by_code(db, code):
            return code


def require_active_member(db: Session, *, group_id: str, user: User) -> GroupMember:
    member = group_repo.get_member(db, group_id=group_id, user_id=user.id)
    if not member or member.banned_at is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not an active group member")
    return member


def require_group_admin(db: Session, *, group_id: str, user: User) -> GroupMember | None:
    if user.is_superuser:
        return None
    member = require_active_member(db, group_id=group_id, user=user)
    if member.role != GroupRole.admin.value:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Group admin permission required")
    return member


def list_groups_for_user(db: Session, user: User) -> list[Group]:
    return group_repo.list_user_groups(db, user.id)


def get_group_for_user(db: Session, *, group_id: str, user: User) -> Group:
    group = group_repo.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    require_active_member(db, group_id=group_id, user=user)
    return group


def create_group(db: Session, *, payload: GroupCreate, creator: User) -> Group:
    group = group_repo.create_group(
        db,
        name=payload.name,
        code=generate_group_code(db),
        creator=creator,
    )
    create_activity(
        db,
        group_id=group.id,
        user_id=creator.id,
        event_type=ActivityEventType.join,
    )
    db.commit()
    return group_repo.get_group(db, group.id) or group


def join_group(db: Session, *, payload: GroupJoin, user: User) -> Group:
    group = group_repo.get_group_by_code(db, payload.code)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

    existing_member = group_repo.get_member(db, group_id=group.id, user_id=user.id)
    if existing_member and existing_member.banned_at is None:
        return group_repo.get_group(db, group.id) or group
    if existing_member and existing_member.banned_at is not None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is banned from this group")

    group_repo.add_member(db, group=group, user=user)
    create_activity(
        db,
        group_id=group.id,
        user_id=user.id,
        event_type=ActivityEventType.join,
    )
    db.commit()
    return group_repo.get_group(db, group.id) or group


def ban_member(db: Session, *, group_id: str, target_user_id: str, admin: User) -> None:
    require_group_admin(db, group_id=group_id, user=admin)
    group = group_repo.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")
    if target_user_id == group.created_by_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot ban group creator")

    member = group_repo.get_member(db, group_id=group_id, user_id=target_user_id)
    if not member or member.banned_at is not None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Active member not found")

    from datetime import UTC, datetime

    member.banned_at = datetime.now(UTC)
    db.commit()
