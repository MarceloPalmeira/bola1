"""add matches.external_id

Revision ID: 0002_match_external_id
Revises: 0001_initial
Create Date: 2026-06-22
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

revision: str = "0002_match_external_id"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("matches", sa.Column("external_id", sa.String(length=64), nullable=True))
    op.create_index(op.f("ix_matches_external_id"), "matches", ["external_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_matches_external_id"), table_name="matches")
    op.drop_column("matches", "external_id")
