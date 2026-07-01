"""create intro_requests table

Revision ID: 73a418f1eb23
Revises: c2087dec4d48
Create Date: 2026-07-01 17:15:55.960728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73a418f1eb23'
down_revision: Union[str, Sequence[str], None] = 'c2087dec4d48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "intro_requests",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("from_user_id", sa.Uuid(), nullable=False),
        sa.Column("to_user_id", sa.Uuid(), nullable=False),
        sa.Column("message", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_intro_requests_from_user_id", "intro_requests", ["from_user_id"])
    op.create_index("ix_intro_requests_to_user_id", "intro_requests", ["to_user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_intro_requests_to_user_id", table_name="intro_requests")
    op.drop_index("ix_intro_requests_from_user_id", table_name="intro_requests")
    op.drop_table("intro_requests")
