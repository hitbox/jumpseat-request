"""Add scheduled departure/arrival to request

Revision ID: cd8c395210bb
Revises: 
Create Date: 2026-08-03 12:04:39.692885

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd8c395210bb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade schema."""

    # Great big warning before deleting existing requests!
    confirmation = 'YES'
    answer = input(f'''
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !!! ALL RECORDS in the jumpseat_request table will be deleted !!!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    Type "{confirmation}" exactly to proceed:''')
    if answer != confirmation:
        raise RuntimeError('Upgrade aborted.')

    op.execute('TRUNCATE TABLE jumpseat_request RESTART IDENTITY CASCADE')

    op.add_column('jumpseat_request', sa.Column('scheduled_departure_airport', sa.String(length=3), nullable=False))
    op.add_column('jumpseat_request', sa.Column('scheduled_arrival_airport', sa.String(length=3), nullable=False))
    op.create_index(op.f('ix_jumpseat_request_scheduled_arrival_airport'), 'jumpseat_request', ['scheduled_arrival_airport'], unique=False)
    op.create_index(op.f('ix_jumpseat_request_scheduled_departure_airport'), 'jumpseat_request', ['scheduled_departure_airport'], unique=False)

def downgrade():
    """Downgrade schema."""
    op.drop_index(op.f('ix_jumpseat_request_scheduled_departure_airport'), table_name='jumpseat_request')
    op.drop_index(op.f('ix_jumpseat_request_scheduled_arrival_airport'), table_name='jumpseat_request')
    op.drop_column('jumpseat_request', 'scheduled_arrival_airport')
    op.drop_column('jumpseat_request', 'scheduled_departure_airport')
