from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from bola1_api.models import Group, GroupMember, GroupRole, User


def list_user_groups(db: Session, user_id: str) -> list[Group]:
    return list(
        db.scalars(
            select(Group)
            .join(GroupMember)
            .where(GroupMember.user_id == user_id, GroupMember.banned_at.is_(None))
            .options(selectinload(Group.members).selectinload(GroupMember.user))
            .order_by(Group.created_at)
        )
    )


def get_group(db: Session, group_id: str) -> Group | None:
    return db.scalar(
        select(Group)
        .where(Group.id == group_id)
        .options(selectinload(Group.members).selectinload(GroupMember.user))
    )


def get_group_by_code(db: Session, code: str) -> Group | None:
    return db.scalar(select(Group).where(Group.code == code.upper()))


def create_group(db: Session, *, name: str, code: str, creator: User) -> Group:
    group = Group(name=name, code=code.upper(), created_by_id=creator.id)
    db.add(group)
    db.flush()
    add_member(db, group=group, user=creator, role=GroupRole.admin.value)
    return group


def get_member(db: Session, *, group_id: str, user_id: str) -> GroupMember | None:
    return db.get(GroupMember, {"group_id": group_id, "user_id": user_id})


def add_member(db: Session, *, group: Group, user: User, role: str = GroupRole.member.value) -> GroupMember:
    member = GroupMember(
        group_id=group.id,
        user_id=user.id,
        role=role,
        joined_at=datetime.now(UTC),
    )
    db.add(member)
    db.flush()
    return member
