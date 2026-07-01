"""create profiles table

Revision ID: c2087dec4d48
Revises: dcfc45fd94a5
Create Date: 2026-07-01 11:36:30.068182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2087dec4d48'
down_revision: Union[str, Sequence[str], None] = 'dcfc45fd94a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("handle", sa.String(length=40), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=False),
        sa.Column("headline", sa.String(length=160), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("bio", sa.Text(), nullable=False),
        sa.Column("available", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_profiles_owner_id", "profiles", ["owner_id"], unique=True)
    op.create_index("ix_profiles_handle", "profiles", ["handle"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_profiles_handle", table_name="profiles")
    op.drop_index("ix_profiles_owner_id", table_name="profiles")
    op.drop_table("profiles")
