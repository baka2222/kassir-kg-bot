"""merge heads

Revision ID: merge_20260303
Revises: 828ba3e44ef2, 1a2b3c4d5e6f
Create Date: 2026-03-03 15:50:00.000000

This is an automatically generated merge migration to combine two heads.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'merge_20260303'
down_revision: Union[str, Sequence[str], None] = ('828ba3e44ef2', '1a2b3c4d5e6f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # empty merge migration
    pass


def downgrade() -> None:
    # nothing to downgrade
    pass
