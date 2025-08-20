from alembic import op
import sqlalchemy as sa

revision = "62587335dfe8"
down_revision = "3a9db6782a68"   # ← make sure this matches your initial head
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "campaign_goals",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("goal_amount", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("CURRENT_TIMESTAMP")),
    )

    op.create_table(
        "donations",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("donor_name", sa.String(120), nullable=False),
        sa.Column("amount", sa.Integer, nullable=False, server_default="0"),
        sa.Column("message", sa.Text),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_donations_created_at", "donations", ["created_at"])

    op.create_table(
        "sponsors",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("tier", sa.String(20)),
        sa.Column("amount", sa.Integer, nullable=False, server_default="0"),
        sa.Column("logo_url", sa.String(255)),
        sa.Column("created_at", sa.DateTime, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_sponsors_tier", "sponsors", ["tier"])
    op.create_index("ix_sponsors_created_at", "sponsors", ["created_at"])


def downgrade():
    op.drop_index("ix_sponsors_created_at", table_name="sponsors")
    op.drop_index("ix_sponsors_tier", table_name="sponsors")
    op.drop_table("sponsors")

    op.drop_index("ix_donations_created_at", table_name="donations")
    op.drop_table("donations")

    op.drop_table("campaign_goals")

