# patch_style.py  (run with: flask patch-style)
from app import create_app, db
from app.models import Team
from flask.cli import with_appcontext
import click

app = create_app()

@app.cli.command('patch-style')
@with_appcontext
def patch_style():
    n = Team.query.filter(Team.template_style != 'neo').update(
        {Team.template_style: 'neo'}, synchronize_session=False)
    db.session.commit()
    click.echo(f'✅ Updated template_style to "neo" for {n} teams.')
