from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from bola1_api.api.v1.deps import get_current_user
from bola1_api.db.session import get_db
from bola1_api.models import User
from bola1_api.schemas import GroupCreate, GroupJoin, GroupMemberRead, GroupRead
from bola1_api.services.groups import ban_member, create_group, get_group_for_user, join_group, list_groups_for_user

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=list[GroupRead])
def list_groups(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_groups_for_user(db, current_user)


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create(payload: GroupCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return create_group(db, payload=payload, creator=current_user)


@router.get("/{group_id}", response_model=GroupRead)
def get(group_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_group_for_user(db, group_id=group_id, user=current_user)


@router.post("/join", response_model=GroupRead)
def join(payload: GroupJoin, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return join_group(db, payload=payload, user=current_user)


@router.get("/{group_id}/members", response_model=list[GroupMemberRead])
def members(group_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    group = get_group_for_user(db, group_id=group_id, user=current_user)
    return [member for member in group.members if member.banned_at is None]


@router.delete("/{group_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(
    group_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    ban_member(db, group_id=group_id, target_user_id=user_id, admin=current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
