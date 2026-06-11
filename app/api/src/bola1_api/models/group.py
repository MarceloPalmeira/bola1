from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bola1_api.db.base import Base, IdMixin, TimestampMixin
from bola1_api.models.enums import GroupRole


class Group(IdMixin, TimestampMixin, Base):
    __tablename__ = "groups"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    created_by_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)

    created_by = relationship("User", back_populates="created_groups")
    members = relationship("GroupMember", back_populates="group")
    predictions = relationship("Prediction", back_populates="group")
    activities = relationship("ActivityEvent", back_populates="group")

    @property
    def invite_link(self) -> str:
        return f"/groups/join?code={self.code}"


class GroupMember(Base):
    __tablename__ = "group_members"
    __table_args__ = (
        UniqueConstraint("group_id", "user_id", name="uq_group_members_group_user"),
        CheckConstraint("role IN ('admin', 'member')", name="ck_group_members_role"),
        CheckConstraint("total_points >= 0", name="ck_group_members_total_points_non_negative"),
        CheckConstraint("exact_scores >= 0", name="ck_group_members_exact_scores_non_negative"),
        CheckConstraint("correct_winners >= 0", name="ck_group_members_correct_winners_non_negative"),
        CheckConstraint("misses >= 0", name="ck_group_members_misses_non_negative"),
    )

    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(
        String(20),
        default=GroupRole.member.value,
        server_default=text("'member'"),
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    banned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    total_points: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    exact_scores: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    correct_winners: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)
    misses: Mapped[int] = mapped_column(Integer, default=0, server_default=text("0"), nullable=False)

    group = relationship("Group", back_populates="members")
    user = relationship("User", back_populates="memberships")
