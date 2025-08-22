from typing import TYPE_CHECKING
from flask import Blueprint, Flask
from app.cli import starforge

# Attempt to import blueprints, fallback to None if not found
try:
    from .main import main_bp
except ImportError:
    main_bp = None

try:
    from .api import api_bp
except ImportError:
    api_bp = None

try:
    from .sms import sms_bp
except ImportError:
    sms_bp = None

try:
    from .stripe_routes import stripe_bp
except ImportError:
    stripe_bp = None

try:
    from .webhooks import webhook_bp
except ImportError:
    webhook_bp = None


# Fallback homepage blueprint if the main route '/' is not defined
fallback = Blueprint("fallback", __name__)

@fallback.route("/")
def default_root():
    """Fallback route when the main route '/' is not defined in main_bp."""
    return "✅ FundChamps SaaS backend is running. Add a homepage to 'main_bp'."


def register_blueprints(app: Flask) -> None:
    """
    Registers all blueprints and CLI commands to the Flask app.

    This includes main, API, SMS, Stripe, webhook blueprints, and CLI commands.

    Args:
        app (Flask): The Flask app instance.
    """
    print("🔌 Registering blueprints and CLI commands...")

    # Register CLI command group
    app.cli.add_command(starforge)
    print("🛠️ Registered CLI command group: starforge")

    # Register available blueprints
    blueprints = {
        "main_bp": main_bp,
        "api_bp": api_bp,
        "sms_bp": sms_bp,
        "stripe_bp": stripe_bp,
        "webhook_bp": webhook_bp,
    }

    for blueprint_name, blueprint in blueprints.items():
        if blueprint:
            url_prefix = f"/{blueprint_name.replace('_bp', '')}"
            app.register_blueprint(blueprint, url_prefix=url_prefix)
            print(f"🧩 Registered blueprint: {blueprint_name}")
        else:
            print(f"⚠️ {blueprint_name} not found; skipping.")

    # Always register the fallback homepage blueprint last
    app.register_blueprint(fallback)
    print("🧩 Registered fallback homepage blueprint")

    print("🔌 All blueprints and CLI commands registered successfully.")

