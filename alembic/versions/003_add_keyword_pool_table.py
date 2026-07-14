"""Add keyword_pool table

Revision ID: 003
Revises: 002
Create Date: 2026-07-14 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "keyword_pool",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("keyword", sa.String(255), nullable=False),
        sa.Column("hub_id", sa.Integer(), nullable=True),
        sa.Column("intent", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_keyword_pool_keyword"), "keyword_pool", ["keyword"])


def downgrade() -> None:
    op.drop_index(op.f("ix_keyword_pool_keyword"), table_name="keyword_pool")
    op.drop_table("keyword_pool")
