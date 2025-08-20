# starforge_seed.py
import click
from faker import Faker
from sqlalchemy import inspect, text, Table
from sqlalchemy.exc import OperationalError

from app import create_app, db

fake = Faker()


def _table_if_exists(engine, metadata, name: str):
    """Return a SQLAlchemy Table for name if it exists in DB, else None."""
    inspector = inspect(engine)
    if name not in inspector.get_table_names():
        return None
    # Prefer already-registered table; otherwise reflect it.
    tbl = metadata.tables.get(name)
    if tbl is None:
        tbl = Table(name, metadata, autoload_with=engine)
    return tbl


@click.command()
@click.option("--force", is_flag=True, help="Force reseed (truncate tables first)")
@click.option(
    "--env",
    "envname",
    type=click.Choice(["production", "development"], case_sensitive=False),
    default="production",
    show_default=True,
    help="App configuration to use",
)
@click.option("--donations", type=int, default=10, show_default=True)
@click.option("--sponsors", type=int, default=5, show_default=True)
@click.option("--goal", type=int, default=10_000, show_default=True)
def seed(force: bool, envname: str, donations: int, sponsors: int, goal: int):
    """Seed demo data for goals, donations, and sponsors."""
    app = create_app(envname)
    with app.app_context():
        engine = db.engine
        metadata = db.metadata
        inspector = inspect(engine)

        if force:
            print("⚠️  Forcing reseed, truncating tables...")
            existing = set(inspector.get_table_names())
            skip = {"alembic_version"}  # don't nuke migrations

            is_sqlite = engine.url.get_backend_name() == "sqlite"
            fk_was_on = False
            if is_sqlite:
                # PRAGMAs must run on the same connection/session in SQLAlchemy 2.x
                row = db.session.execute(text("PRAGMA foreign_keys")).fetchone()
                fk_was_on = bool(row[0]) if row else False
                db.session.execute(text("PRAGMA foreign_keys = OFF"))

            try:
                # Delete in reverse dependency order, and only if table actually exists
                for table in reversed(metadata.sorted_tables):
                    name = table.name
                    if name in skip:
                        continue
                    if name not in existing:
                        print(f"  ⚠️  skipped {name} (table not present)")
                        continue
                    try:
                        db.session.execute(table.delete())
                        print(f"  ✅ cleared {name}")
                    except OperationalError as e:
                        print(f"  ⚠️  skipped {name} ({e.orig})")
                db.session.commit()
            finally:
                if is_sqlite:
                    db.session.execute(
                        text(f"PRAGMA foreign_keys = {'ON' if fk_was_on else 'OFF'}")
                    )

        # --- Insert demo rows using Core to avoid ORM class name collisions ---
        campaign_tbl = _table_if_exists(engine, metadata, "campaign_goals")
        donations_tbl = _table_if_exists(engine, metadata, "donations")
        sponsors_tbl = _table_if_exists(engine, metadata, "sponsors")

        if campaign_tbl is not None:
            db.session.execute(campaign_tbl.insert().values(goal_amount=goal))
            print(f"🌟 Set campaign goal → ${goal:,}")
        else:
            print("⚠️  campaign_goals table not found — skipping goal seed")

        if donations_tbl is not None:
            rows = [
                {
                    "donor_name": fake.name(),
                    "amount": fake.random_int(25, 500),
                    "message": fake.sentence(),
                }
                for _ in range(donations)
            ]
            if rows:
                db.session.execute(donations_tbl.insert(), rows)
            print(f"💸 Inserted {donations} donations")
        else:
            print("⚠️  donations table not found — skipping donations seed")

        if sponsors_tbl is not None:
            tiers = ("Bronze", "Silver", "Gold", "VIP")
            rows = [
                {
                    "name": fake.company(),
                    "tier": fake.random_element(elements=tiers),
                    "amount": fake.random_int(1_000, 10_000),
                    "logo_url": f"https://placehold.co/200x100?text={fake.word()}",
                }
                for _ in range(sponsors)
            ]
            if rows:
                db.session.execute(sponsors_tbl.insert(), rows)
            print(f"🤝 Inserted {sponsors} sponsors")
        else:
            print("⚠️  sponsors table not found — skipping sponsors seed")

        db.session.commit()
        print("🌱 Database seeded with demo goals, donations, and sponsors.")


if __name__ == "__main__":
    seed()

