"""change tg_id to bigint

Revision ID: 20260303_charsize
Revises: merge_20260303
Create Date: 2026-03-03 16:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260303_charsize'
down_revision: Union[str, Sequence[str], None] = 'merge_20260303'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('operators', 'tg_id', type_=sa.BigInteger(), existing_type=sa.Integer())


def downgrade() -> None:
    op.alter_column('operators', 'tg_id', type_=sa.Integer(), existing_type=sa.BigInteger())
