"""make phone nullable

Revision ID: f80cce9ba60f
Revises: 20260304_chat_sender_bigint
Create Date: 2026-03-09 17:56:58.956440

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f80cce9ba60f'
down_revision: Union[str, Sequence[str], None] = '20260304_chat_sender_bigint'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
