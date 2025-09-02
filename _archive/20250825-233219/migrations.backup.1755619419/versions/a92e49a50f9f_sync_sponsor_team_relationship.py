"""sync sponsor/team relationship

Revision ID: a92e49a50f9f
Revises: a9a0a62150e4
Create Date: 2025-08-15 17:14:16.916586
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a92e49a50f9f'
down_revision = 'a9a0a62150e4'
branch_labels = None
depends_on = None


def upgrade():
    # --- campaign_goals table ---
    with op.batch_alter_table("campaign_goals", schema=None) as batch_op:
        batch_op.add_column(sa.Column("team_id", sa.Integer(), nullable=False))
        batch_op.create_index(
            "ix_campaign_goals_team_active",
            ["team_id", "active"],
            unique=False
        )
        batch_op.create_index(
            batch_op.f("ix_campaign_goals_team_id"),
            ["team_id"],
            unique=False
        )
        batch_op.create_foreign_key(
            "fk_campaign_goals_team_id_teams",  # named for SQLite safety
            "teams",
            ["team_id"], ["id"],
            ondelete="CASCADE"
        )

    # --- sponsors table ---
    with op.batch_alter_table("sponsors", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_sponsors_status"),
            ["status"],
            unique=False
        )


def downgrade():
    # --- sponsors table ---
    with op.batch_alter_table("sponsors", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_sponsors_status"))

    # --- campaign_goals table ---
    with op.batch_alter_table("campaign_goals", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_campaign_goals_team_id_teams",
            type_="foreignkey"
        )
        batch_op.drop_index(batch_op.f("ix_campaign_goals_team_id"))
        batch_op.drop_index("ix_campaign_goals_team_active")
        batch_op.drop_column("team_id")

