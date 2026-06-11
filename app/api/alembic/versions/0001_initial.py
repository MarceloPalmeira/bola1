"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-04
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("nickname", sa.String(length=80), nullable=False),
        sa.Column("avatar", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "teams",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=8), nullable=False),
        sa.Column("flag", sa.String(length=16), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_teams_code"), "teams", ["code"], unique=True)

    op.create_table(
        "groups",
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("created_by_id", sa.String(length=36), nullable=False),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_groups_code"), "groups", ["code"], unique=True)

    op.create_table(
        "matches",
        sa.Column("home_team_id", sa.String(length=36), nullable=False),
        sa.Column("away_team_id", sa.String(length=36), nullable=False),
        sa.Column("kickoff_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("venue", sa.String(length=255), nullable=False),
        sa.Column("phase", sa.String(length=40), server_default=sa.text("'group-stage'"), nullable=False),
        sa.Column("world_cup_group", sa.String(length=8), nullable=True),
        sa.Column("status", sa.String(length=20), server_default=sa.text("'upcoming'"), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=True),
        sa.Column("away_score", sa.Integer(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["away_team_id"], ["teams.id"]),
        sa.ForeignKeyConstraint(["home_team_id"], ["teams.id"]),
        sa.CheckConstraint("home_team_id <> away_team_id", name="ck_matches_distinct_teams"),
        sa.CheckConstraint(
            "phase IN ('group-stage', 'round-of-16', 'quarter-finals', 'semi-finals', 'final')",
            name="ck_matches_phase",
        ),
        sa.CheckConstraint("status IN ('upcoming', 'live', 'finished')", name="ck_matches_status"),
        sa.CheckConstraint("home_score IS NULL OR home_score >= 0", name="ck_matches_home_score_non_negative"),
        sa.CheckConstraint("away_score IS NULL OR away_score >= 0", name="ck_matches_away_score_non_negative"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_matches_kickoff_at"), "matches", ["kickoff_at"], unique=False)

    op.create_table(
        "group_members",
        sa.Column("group_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=20), server_default=sa.text("'member'"), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("banned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_points", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("exact_scores", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("correct_winners", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.Column("misses", sa.Integer(), server_default=sa.text("0"), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.CheckConstraint("role IN ('admin', 'member')", name="ck_group_members_role"),
        sa.CheckConstraint("total_points >= 0", name="ck_group_members_total_points_non_negative"),
        sa.CheckConstraint("exact_scores >= 0", name="ck_group_members_exact_scores_non_negative"),
        sa.CheckConstraint("correct_winners >= 0", name="ck_group_members_correct_winners_non_negative"),
        sa.CheckConstraint("misses >= 0", name="ck_group_members_misses_non_negative"),
        sa.PrimaryKeyConstraint("group_id", "user_id"),
        sa.UniqueConstraint("group_id", "user_id", name="uq_group_members_group_user"),
    )

    op.create_table(
        "predictions",
        sa.Column("match_id", sa.String(length=36), nullable=False),
        sa.Column("group_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("home_score", sa.Integer(), nullable=False),
        sa.Column("away_score", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("result_type", sa.String(length=20), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.CheckConstraint("home_score >= 0", name="ck_predictions_home_score_non_negative"),
        sa.CheckConstraint("away_score >= 0", name="ck_predictions_away_score_non_negative"),
        sa.CheckConstraint("points IS NULL OR points IN (0, 1, 3)", name="ck_predictions_points"),
        sa.CheckConstraint("result_type IS NULL OR result_type IN ('exact', 'winner', 'miss')", name="ck_predictions_result_type"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "group_id", "match_id", name="uq_predictions_user_group_match"),
    )

    op.create_table(
        "activity_events",
        sa.Column("group_id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=True),
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("match_id", sa.String(length=36), nullable=True),
        sa.Column("prediction_id", sa.String(length=36), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.ForeignKeyConstraint(["prediction_id"], ["predictions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.CheckConstraint("type IN ('join', 'prediction', 'result')", name="ck_activity_events_type"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("activity_events")
    op.drop_table("predictions")
    op.drop_table("group_members")
    op.drop_index(op.f("ix_matches_kickoff_at"), table_name="matches")
    op.drop_table("matches")
    op.drop_index(op.f("ix_groups_code"), table_name="groups")
    op.drop_table("groups")
    op.drop_index(op.f("ix_teams_code"), table_name="teams")
    op.drop_table("teams")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
