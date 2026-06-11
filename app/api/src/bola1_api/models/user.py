from sqlalchemy import Boolean, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bola1_api.db.base import Base, IdMixin, TimestampMixin


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nickname: Mapped[str] = mapped_column(String(80), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default=text("true"), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, server_default=text("false"), nullable=False)

    memberships = relationship("GroupMember", back_populates="user")
    created_groups = relationship("Group", back_populates="created_by")
    predictions = relationship("Prediction", back_populates="user")
    activities = relationship("ActivityEvent", back_populates="user")
