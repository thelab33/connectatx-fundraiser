# scripts/restore_dev_db.py
"""
Restore Dev DB for FundChamps
- Drops & recreates schema
- Seeds default goal + sponsors
"""

import click
from datetime import datetime
from app import create_app, db
from app.models import CampaignGoal, Sponsor  # adjust import if in different modules


@click.command()
def restore_db():
    app = create_app()
    with app.app_context():
        click.echo("⚠️ Dropping & recreating schema...")
        db.drop_all()
        db.create_all()

        # --- Seed a fundraising goal ---
        goal = CampaignGoal(
            goal_amount=10000,
            total=0,
            active=True,
            deleted=False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(goal)

        # --- Seed some sponsors ---
        sponsors = [
            Sponsor(name="TechNova", amount=500, status="approved", deleted=False),
            Sponsor(name="River BBQ", amount=250, status="approved", deleted=False),
            Sponsor(name="Sunrise Dental", amount=1000, status="approved", deleted=False),
        ]
        db.session.add_all(sponsors)

        db.session.commit()
        click.echo("✅ Database restored with sample data!")


if __name__ == "__main__":
    restore_db()

