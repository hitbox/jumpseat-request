"""Add jumpseat priority table

Revision ID: 51774c4208c6
Revises: b4f286a0162d
Create Date: 2026-09-12 17:14:08.407820

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision = '51774c4208c6'
down_revision = 'b4f286a0162d'
branch_labels = None
depends_on = None

def upgrade():
    """Upgrade schema."""
    op.create_table('jumpseat_request_priority',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )

    op.add_column('jumpseat_request', sa.Column('priority_id', sa.UUID(), nullable=False))
    op.create_foreign_key(None, 'jumpseat_request', 'jumpseat_request_priority', ['priority_id'], ['id'])

def downgrade():
    """Downgrade schema."""
    op.drop_constraint(None, 'jumpseat_request', type_='foreignkey')
    op.drop_column('jumpseat_request', 'priority_id')
    op.drop_table('jumpseat_request_priority')
