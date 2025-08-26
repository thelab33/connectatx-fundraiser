#!/usr/bin/env python3
"""
starforge_autopatch.py — FundChamps Multi-Pass Fixer
⚡ One-stop patcher for current blockers
"""

import sys
import re
from pathlib import Path
import fileinput

ROOT = Path(__file__).resolve().parent
APP_INIT = ROOT / "app/__init__.py"
MAIN_ROUTES = ROOT / "app/routes/main.py"
MODELS_INIT = ROOT / "app/models/__init__.py"
MODELS_FILE  = ROOT / "app/models/campaign_goal.py"
INDEX_HTML = ROOT / "app/templates/index.html"

# --------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------
def patch_static_url():
    if not APP_INIT.exists():
        print("❌ app/__init__.py not found"); return
    txt = APP_INIT.read_text(encoding="utf-8")
    if "static_url" in txt:
        print("✅ static_url helper already exists"); return

    pattern = re.compile(r"app\s*=\s*Flask\s*\([^)]*\)", re.MULTILINE)
    match = pattern.search(txt)
    if not match:
        print("❌ Could not detect Flask app creation in app/__init__.py")
        return

    helper = '''
    # -----------------------------------------------------------------
    # Jinja global: static_url("css/main.css") → /static/css/main.css
    # -----------------------------------------------------------------
    from flask import url_for as _url_for
    if "static_url" not in app.jinja_env.globals:
        app.jinja_env.globals["static_url"] = lambda f: _url_for("static", filename=f)
'''
    patched = txt[:match.end()] + helper + txt[match.end():]
    APP_INIT.write_text(patched, encoding="utf-8")
    print("⚡ Injected static_url helper")

def patch_sponsor_queries():
    if not MAIN_ROUTES.exists():
        print("❌ app/routes/main.py not found"); return
    txt = MAIN_ROUTES.read_text(encoding="utf-8")
    patched = txt.replace("Sponsor.deleted.is_(False)", "Sponsor.deleted_at.is_(None)")
    if txt != patched:
        MAIN_ROUTES.write_text(patched, encoding="utf-8")
        print("⚡ Patched Sponsor.deleted → Sponsor.deleted_at")
    else:
        print("✅ Sponsor query already patched")

def ensure_campaign_goal_model():
    MODELS_INIT.parent.mkdir(parents=True, exist_ok=True)
    # Check if CampaignGoal already defined
    if MODELS_FILE.exists():
        txt = MODELS_FILE.read_text(encoding="utf-8")
        if "class CampaignGoal" in txt:
            print("✅ CampaignGoal model already exists")
            return

    MODELS_FILE.write_text(
        '''from app.extensions import db
from app.models.mixins import TimestampMixin, SoftDeleteMixin

class CampaignGoal(db.Model, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "campaign_goals"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"))
    goal_amount = db.Column(db.Float, nullable=False)
    total = db.Column(db.Float, default=0)
    active = db.Column(db.Boolean, default=True)

    team = db.relationship("Team", backref="campaign_goals")
''', encoding="utf-8")
    print("⚡ Added CampaignGoal model in app/models/campaign_goal.py")

    # Ensure it's imported in models/__init__.py
    if MODELS_INIT.exists():
        txt = MODELS_INIT.read_text(encoding="utf-8")
        if "CampaignGoal" not in txt:
            txt += "\nfrom .campaign_goal import CampaignGoal\n"
            MODELS_INIT.write_text(txt, encoding="utf-8")
            print("⚡ Registered CampaignGoal in models/__init__.py")
    else:
        MODELS_INIT.write_text("from .campaign_goal import CampaignGoal\n", encoding="utf-8")
        print("⚡ Created models/__init__.py with CampaignGoal")

def clean_index_html():
    if not INDEX_HTML.exists():
        print("❌ templates/index.html not found"); return
    txt = INDEX_HTML.read_text(encoding="utf-8")
    # Remove stray inline comments like `# ...` inside dicts
    txt = re.sub(r",\s*#.*", ",", txt)
    # Fix invalid ARIA like aria-hidden="truee"
    txt = re.sub(r'aria-([a-zA-Z]+)=["\']hidden["\']', r'aria-\1="true"', txt)
    INDEX_HTML.write_text(txt, encoding="utf-8")
    print("⚡ Cleaned index.html (inline comments + ARIA fixes)")

# --------------------------------------------------------------------
# Run all patches
# --------------------------------------------------------------------
def main():
    patch_static_url()
    patch_sponsor_queries()
    ensure_campaign_goal_model()
    clean_index_html()

    print("\n✅ Starforge autopatch complete. Next steps:")
    print("   flask db migrate -m 'autopatch: campaign goals'")
    print("   flask db upgrade")

if __name__ == "__main__":
    main()

