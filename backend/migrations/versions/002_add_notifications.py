"""Add notifications table - FAZ-2

Revision ID: 002_notifications
Revises: 001_initial
Create Date: 2025-12-01

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '002_notifications'
down_revision: Union[str, None] = '001_initial'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('message', sa.String(500), nullable=False),
        sa.Column('activity_id', sa.Integer(), nullable=True),
        sa.Column('subtask_id', sa.Integer(), nullable=True),
        sa.Column('target_user_id', sa.Integer(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['activity_id'], ['activities.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['subtask_id'], ['subtasks.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['target_user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'])
    )

    # Create indexes for faster queries
    op.create_index('ix_notifications_target_user_id', 'notifications', ['target_user_id'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])


def downgrade() -> None:
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_target_user_id', table_name='notifications')
    op.drop_table('notifications')

