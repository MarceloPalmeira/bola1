from sqlalchemy import CheckConstraint, ForeignKey, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bola1_api.db.base import Base, IdMixin, TimestampMixin


class ActivityEvent(IdMixin, TimestampMixin, Base):
    __tablename__ = "activity_events"
    __table_args__ = (
        CheckConstraint("type IN ('join', 'prediction', 'result')", name="ck_activity_events_type"),
    )

    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), nullable=False)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"))
    type: Mapped[str] = mapped_column(String(40), nullable=False)
    match_id: Mapped[str | None] = mapped_column(ForeignKey("matches.id"))
    prediction_id: Mapped[str | None] = mapped_column(ForeignKey("predictions.id"))
    payload_json: Mapped[dict | None] = mapped_column(JSON)

    group = relationship("Group", back_populates="activities")
    user = relationship("User", back_populates="activities")
    match = relationship("Match", back_populates="activities")
    prediction = relationship("Prediction", back_populates="activities")
