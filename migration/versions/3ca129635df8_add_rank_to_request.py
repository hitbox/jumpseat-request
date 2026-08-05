"""Add rank to request

Revision ID: 3ca129635df8
Revises: cd8c395210bb
Create Date: 2026-08-03 13:22:46.804642

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision  = '3ca129635df8'
down_revision = 'cd8c395210bb'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade schema."""
    op.add_column('jumpseat_request', sa.Column('rank', sa.String(length=2), nullable=True))
    op.create_index(op.f('ix_jumpseat_request_rank'), 'jumpseat_request', ['rank'], unique=False)
    # Add Rank table.
    op.create_table('rank',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rank_code'), 'rank', ['code'], unique=False)
    op.add_column('jumpseat_request', sa.Column('rank_id', sa.UUID(), nullable=True))
    op.create_foreign_key(
        constraint_name = None,
        source_table = 'jumpseat_request',
        referent_table = 'rank',
        local_cols = ['rank_id'],
        remote_cols = ['id'],
    )

def downgrade():
    """Downgrade schema."""
    op.drop_constraint(None, 'jumpseat_request', type_='foreignkey')
    op.drop_column('jumpseat_request', 'rank_id')
    op.drop_index(op.f('ix_rank_code'), table_name='rank')
    op.drop_table('rank')

    op.drop_index(op.f('ix_jumpseat_request_rank'), table_name='jumpseat_request')
    op.drop_column('jumpseat_request', 'rank')
