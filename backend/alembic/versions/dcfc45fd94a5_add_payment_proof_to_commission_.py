"""add payment proof to commission installments

Revision ID: dcfc45fd94a5
Revises: 4c0f82d5c898
Create Date: 2026-07-01 01:22:03.096311

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcfc45fd94a5'
down_revision: Union[str, Sequence[str], None] = '4c0f82d5c898'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "commission_installments",
        sa.Column("proof_filename", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "commission_installments",
        sa.Column("proof_content_type", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "commission_installments",
        sa.Column("proof_size", sa.Integer(), nullable=True),
    )
    op.add_column(
        "commission_installments",
        sa.Column("proof_storage_key", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "commission_installments",
        sa.Column("proof_uploaded_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "payment_proof_blobs",
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.PrimaryKeyConstraint("storage_key"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("payment_proof_blobs")
    op.drop_column("commission_installments", "proof_uploaded_at")
    op.drop_column("commission_installments", "proof_storage_key")
    op.drop_column("commission_installments", "proof_size")
    op.drop_column("commission_installments", "proof_content_type")
    op.drop_column("commission_installments", "proof_filename")
