import click
from faker import Faker
from werkzeug.security import generate_password_hash
from flask.cli import AppGroup
from app.extensions import db
from app.models import CampaignGoal, Sponsor, User, Team, Player

# 🎯 CLI Group: starforge
starforge = AppGroup("starforge")
fake = Faker()

@starforge.command("seed-demo")
@click.option("--users", default=5, help="Number of demo users to create.")
@click.option("--sponsors", default=8, help="Number of demo sponsors to create.")
@click.option("--players", default=10, help="Number of demo players to create.")
@click.option("--teams", default=1, help="Number of demo teams to create.")
@click.option("--clear", is_flag=True, help="Clear existing demo data before seeding.")
def seed_demo_cmd(users, sponsors, players, teams, clear):
    """
    🌱 Seed demo data for FundChamps PaaS.
    Generates realistic users, players, sponsors, and campaign goals — ready for live demos.
    """

    from app import create_app
    app = create_app()

    with app.app_context():
        db.create_all()

        if clear:
            click.secho("🧹 Clearing existing data…", fg="yellow")
            for model in (Sponsor, User, Player, Team, CampaignGoal):
                deleted = model.query.delete()
                click.secho(f"  ↳ Cleared {deleted} from {model.__name__}", fg="yellow")
            db.session.commit()

        # ➤ Teams
        click.secho(f"🏀 Seeding {teams} team(s)…", fg="green")
        team_objs = []
        for i in range(teams):
            team = Team(
                slug=fake.unique.slug(),
                team_name=f"{fake.city()} {fake.word().capitalize()}",
                meta_description=fake.sentence(nb_words=10),
                theme_color=fake.hex_color()
            )
            db.session.add(team)
            team_objs.append(team)
        db.session.commit()

        # ➤ Users
        click.secho(f"👤 Seeding {users} user(s)…", fg="green")
        demo_password = "demo123"
        for _ in range(users):
            db.session.add(User(
                email=fake.unique.email(),
                password_hash=generate_password_hash(demo_password),
                is_admin=fake.boolean(chance_of_getting_true=20),
                team_id=fake.random_element(team_objs).id if team_objs else None
            ))

        # ➤ Players
        click.secho(f"🏅 Seeding {players} player(s)…", fg="green")
        roles = ["Guard", "Forward", "Center"]
        for _ in range(players):
            db.session.add(Player(
                name=fake.name(),
                role=fake.random_element(roles),
                photo_url=f"https://i.pravatar.cc/200?img={fake.random_int(1, 70)}",
                team_id=fake.random_element(team_objs).id if team_objs else None
            ))

        # ➤ Sponsors
        click.secho(f"💸 Seeding {sponsors} sponsor(s)…", fg="green")
        for _ in range(sponsors):
            db.session.add(Sponsor(
                name=fake.company(),
                email=fake.unique.company_email(),
                amount=fake.random_int(min=100, max=5000),
                message=fake.catch_phrase(),
                status="approved",
                deleted=False,
                tier=fake.random_element(["Bronze", "Silver", "Gold", "Platinum", "VIP"]),
                team_id=fake.random_element(team_objs).id if team_objs else None
            ))

        # ➤ Campaign Goals
        click.secho("🎯 Ensuring campaign goals per team…", fg="green")
        for team in team_objs:
            existing = CampaignGoal.query.filter_by(team_id=team.id, active=True).first()
            if not existing:
                db.session.add(CampaignGoal(
                    goal_amount=10000,
                    active=True,
                    team_id=team.id
                ))

        db.session.commit()
        click.secho("✅ Demo data seeded successfully!", fg="bright_green", bold=True)
        click.echo("🔐 Demo password for all users: demo123")

