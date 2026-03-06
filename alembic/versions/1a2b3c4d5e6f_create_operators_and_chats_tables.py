"""create operators and chats tables

Revision ID: 1a2b3c4d5e6f
Revises: 0d2d02e51097
Create Date: 2026-03-03 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1a2b3c4d5e6f'
down_revision: Union[str, Sequence[str], None] = '0d2d02e51097'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    
    op.create_table(
        'operators',
        sa.Column('id', sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column('tg_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='offline'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.literal(True)),
        sa.Column('rating', sa.Float(), nullable=False, server_default=sa.literal(5.0)),
        sa.Column('total_chats', sa.Integer(), nullable=False, server_default=sa.literal(0)),
        sa.Column('active_chats', sa.Integer(), nullable=False, server_default=sa.literal(0)),
        sa.Column('max_concurrent_chats', sa.Integer(), nullable=False, server_default=sa.literal(3)),
        sa.Column('bio', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tg_id')
    )
    
    op.create_table(
        'operator_chats',
        sa.Column('id', sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('operator_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('user_rating', sa.Integer(), nullable=True),
        sa.Column('messages_count', sa.Integer(), nullable=False, server_default=sa.literal(0)),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['operators.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'chat_messages',
        sa.Column('id', sa.Integer(), sa.Identity(always=True), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=False, server_default='text'),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default=sa.literal(False)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['operator_chats.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    
    op.drop_table('chat_messages')
    op.drop_table('operator_chats')
    op.drop_table('operators')
