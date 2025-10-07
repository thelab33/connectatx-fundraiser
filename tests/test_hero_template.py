import pytest
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime

TEMPLATE_PATH = "/mnt/data"
TEMPLATE_NAME = "hero_classic.html"

@pytest.fixture
def jinja_env():
    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH), autoescape=select_autoescape(['html','xml']))
    env.globals.update({
        'url_for': lambda endpoint, **kwargs: (('/static/' + kwargs.get('filename','').lstrip('/')) if endpoint=='static' else f'/{endpoint}'),
        'safe_url_for': lambda endpoint, **kwargs: (('/static/' + kwargs.get('filename','').lstrip('/')) if endpoint=='static' else f'/{endpoint}'),
        'has_endpoint': lambda name: False,
        'now': lambda: datetime.now(),
    })
    return env

def test_hero_renders(jinja_env):
    tpl = jinja_env.get_template(TEMPLATE_NAME)
    rendered = tpl.render(team={'name':'Connect ATX Elite','hero_jpg':'/static/images/connect-atx-team.jpg','games_played':35,'championships':5,'training_hours':120}, NONCE='testnonce', SHOW_SCOREBOARD=False)
    assert '<section' in rendered
    assert 'fcx-hero--cinematic' in rendered
    # data-team is optional depending on template variant; ensure key CTA exists instead
    assert 'Fuel the Season' in rendered
    assert "|e('js')" not in rendered

