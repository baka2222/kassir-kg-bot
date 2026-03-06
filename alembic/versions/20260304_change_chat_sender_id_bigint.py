"""change chat_messages.sender_id to bigint

Revision ID: 20260304_chat_sender_bigint
Revises: 20260303_charsize
Create Date: 2026-03-04 14:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260304_chat_sender_bigint'
down_revision: Union[str, Sequence[str], None] = '20260303_charsize'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'chat_messages',
        'sender_id',
        type_=sa.BigInteger(),
        existing_type=sa.Integer(),
        postgresql_using='sender_id::bigint',
    )


def downgrade() -> None:
    op.alter_column(
        'chat_messages',
        'sender_id',
        type_=sa.Integer(),
        existing_type=sa.BigInteger(),
        postgresql_using='sender_id::integer',
    )
