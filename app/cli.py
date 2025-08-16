import click
from faker import Faker
from werkzeug.security import generate_password_hash
from flask.cli import AppGroup
from app.extensions import db
from app.models import CampaignGoal, Sponsor, User, Team, Player

# 🎯 CLI Group
starforge = AppGroup("starforge")
fake = Faker()

@starforge.command("seed-demo")
@click.option("--users", default=5, show_default=True, help="Number of demo users to create.")
@click.option("--sponsors", default=8, show_default=True, help="Number of demo sponsors to create.")
@click.option("--players", default=10, show_default=True, help="Number of demo players to create.")
@click.option("--teams", default=1, show_default=True, help="Number of demo teams to create.")
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
            _clear_demo_data()

        with db.session.begin():
            # Seed in logical order so FKs are valid
            team_objs = _seed_teams(teams)
            _seed_users(users, team_objs)
            _seed_players(players, team_objs)
            _seed_sponsors(sponsors, team_objs)
            _ensure_campaign_goals(team_objs)

        click.secho("✅ Demo data seeded successfully!", fg="bright_green", bold=True)
        click.echo("🔐 Demo password for all users: demo123")


# --------------------------
#   Internal seed helpers
# --------------------------

def _clear_demo_data():
    click.secho("🧹 Clearing existing data…", fg="yellow")
    for model in (Sponsor, User, Player, Team, CampaignGoal):
        deleted = model.query.delete()
        click.secho(f"  ↳ Cleared {deleted} {model.__name__}(s)", fg="yellow")
    db.session.commit()


def _seed_teams(count):
    click.secho(f"🏀 Seeding {count} team(s)…", fg="green")
    teams = []
    for _ in range(count):
        team = Team(
            slug=fake.unique.slug(),
            team_name=f"{fake.city()} {fake.word().capitalize()}",
            meta_description=fake.sentence(nb_words=10),
            theme_color=fake.hex_color()
        )
        db.session.add(team)
        teams.append(team)
    return teams


def _seed_users(count, teams):
    click.secho(f"👤 Seeding {count} user(s)…", fg="green")
    demo_password_hash = generate_password_hash("demo123")
    for _ in range(count):
        db.session.add(User(
            email=fake.unique.email(),
            password_hash=demo_password_hash,
            is_admin=fake.boolean(chance_of_getting_true=20),
            team_id=fake.random_element(teams).id if teams else None
        ))


def _seed_players(count, teams):
    click.secho(f"🏅 Seeding {count} player(s)…", fg="green")
    roles = ["Guard", "Forward", "Center"]
    for _ in range(count):
        db.session.add(Player(
            name=fake.name(),
            role=fake.random_element(roles),
            photo_url=f"https://i.pravatar.cc/200?img={fake.random_int(1, 70)}",
            team_id=fake.random_element(teams).id if teams else None
        ))


def _seed_sponsors(count, teams):
    click.secho(f"💸 Seeding {count} sponsor(s)…", fg="green")
    tiers = ["Bronze", "Silver", "Gold", "Platinum", "VIP"]
    for _ in range(count):
        db.session.add(Sponsor(
            name=fake.company(),
            email=fake.unique.company_email(),
            amount=fake.random_int(min=100, max=5000),
            message=fake.catch_phrase(),
            status="approved",
            deleted=False,
            tier=fake.random_element(tiers),
            team_id=fake.random_element(teams).id if teams else None
        ))


def _ensure_campaign_goals(teams):
    click.secho("🎯 Ensuring campaign goals per team…", fg="green")
    for team in teams:
        if not CampaignGoal.query.filter_by(team_id=team.id, active=True).first():
            db.session.add(CampaignGoal(
                goal_amount=10000,
                active=True,
                team_id=team.id
            ))

