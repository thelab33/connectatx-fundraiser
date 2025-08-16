"""Add tier + notes + team_id to Sponsor

Revision ID: a9a0a62150e4
Revises: b0cd58a096f1
Create Date: 2025-08-15 13:11:14.884587
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a9a0a62150e4'
down_revision = 'b0cd58a096f1'
branch_labels = None
depends_on = None


def upgrade():
    """Upgrade sponsors table with tier, notes, and team_id FK."""
    with op.batch_alter_table('sponsors', schema=None) as batch_op:
        # New columns
        batch_op.add_column(sa.Column('team_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('tier', sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column('notes', sa.Text(), nullable=True))

        # Indexes
        batch_op.create_index(batch_op.f('ix_sponsors_team_id'), ['team_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_sponsors_tier'), ['tier'], unique=False)

        # Explicitly named FK for SQLite batch mode
        batch_op.create_foreign_key(
            'fk_sponsors_team_id',  # Explicit name required in batch mode
            'teams',
            ['team_id'],
            ['id'],
            ondelete='SET NULL'
        )


def downgrade():
    """Downgrade sponsors table by removing tier, notes, and team_id FK."""
    with op.batch_alter_table('sponsors', schema=None) as batch_op:
        batch_op.drop_constraint('fk_sponsors_team_id', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_sponsors_tier'))
        batch_op.drop_index(batch_op.f('ix_sponsors_team_id'))
        batch_op.drop_column('notes')
        batch_op.drop_column('tier')
        batch_op.drop_column('team_id')

