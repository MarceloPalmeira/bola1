from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bola1_api.db.base import Base, IdMixin, TimestampMixin


class Prediction(IdMixin, TimestampMixin, Base):
    __tablename__ = "predictions"
    __table_args__ = (
        UniqueConstraint("user_id", "group_id", "match_id", name="uq_predictions_user_group_match"),
        CheckConstraint("home_score >= 0", name="ck_predictions_home_score_non_negative"),
        CheckConstraint("away_score >= 0", name="ck_predictions_away_score_non_negative"),
        CheckConstraint("points IS NULL OR points IN (0, 1, 3)", name="ck_predictions_points"),
        CheckConstraint("result_type IS NULL OR result_type IN ('exact', 'winner', 'miss')", name="ck_predictions_result_type"),
    )

    match_id: Mapped[str] = mapped_column(ForeignKey("matches.id"), nullable=False)
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    home_score: Mapped[int] = mapped_column(Integer, nullable=False)
    away_score: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int | None] = mapped_column(Integer)
    result_type: Mapped[str | None] = mapped_column(String(20))

    match = relationship("Match", back_populates="predictions")
    group = relationship("Group", back_populates="predictions")
    user = relationship("User", back_populates="predictions")
    activities = relationship("ActivityEvent", back_populates="prediction")
