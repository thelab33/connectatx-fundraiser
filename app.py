# FUNDCHAMPS-HERO-AUTO
from flask import Flask, render_template
try:
    from babel.numbers import format_currency
    HAVE_BABEL = True
except Exception:
    HAVE_BABEL = False

app = Flask(__name__)

# --- Filters ---
@app.template_filter("roll_money")
def roll_money(amount, currency="USD"):
    try:
        if HAVE_BABEL:
            return format_currency(amount, currency, locale="en_US")
        return f"${int(float(amount)):,}"
    except Exception:
        return f"${int(amount):,}"

@app.template_filter("roll_pct")
def roll_pct(pct):
    try:
        return int(round(float(pct)))
    except Exception:
        return 0

@app.template_filter("clamp_pct")
def clamp_pct(value):
    try:
        v = float(value)
        return 0 if v < 0 else 100 if v > 100 else int(round(v))
    except Exception:
        return 0

@app.route("/")
def home():
    data = dict(
        theme_hex="#fbbf24", team_name="Connect ATX Elite",
        title="Fuel the Season.", title_2="Fund the Future.",
        subtitle="Every dollar powers our journey: gear, travel, coaching, and tutoring.",
        panel_title="Live", panel_title_2="Scoreboard",
        href_donate="https://example.com/donate", href_impact="/impact", href_sponsor="/sponsor",
        text_keyword="ELITE", text_short="444321",
        raised=0, goal=50000, deadline="", currency="USD"
    )
    return render_template("pages/home.html", **data)

if __name__ == "__main__":
    app.run(debug=True)

# FUNDCHAMPS-HERO-AUTO-CSP
try:
    from flask_talisman import Talisman
    csp = {
      'default-src': "'self'",
      'img-src': "'self' data:",
      'style-src': "'self'",
      'script-src': "'self'",
      'connect-src': "'self'",
    }
    Talisman(app, content_security_policy=csp, force_https=True)
except Exception:
    pass
