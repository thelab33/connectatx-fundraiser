import os
from pathlib import Path

# ───────────────────────────────────────────────
# TEAM CONFIG — Dynamic, reusable, multi-org ready
# ───────────────────────────────────────────────

TEAM_CONFIG = {
    "team_name": "Connect ATX Elite",
    "location": "Austin, TX",
    "logo": "images/logo.webp",
    "contact_email": "info@connectatxelite.org",
    "instagram": "https://instagram.com/connectatxelite",
    "is_trial": True,  # 🚧 Show trial banners / lock premium-only features
    "brand_color": "amber-400",
    "fundraising_goal": 10000,
    "amount_raised": 7850,

    # 🔥 About/Mission Section
    "about": [
        "Connect ATX Elite is a community-powered, non-profit 12U AAU basketball program based in Austin, TX.",
        "We develop skilled athletes, but also confident, disciplined, and academically driven young leaders.",
    ],

    # 🏀 Player Roster (used in Hero / About partials)
    "players": [
        {"name": "Andre", "role": "Guard"},
        {"name": "Jordan", "role": "Forward"},
        {"name": "Malik", "role": "Center"},
        {"name": "CJ", "role": "Guard"},
        {"name": "Terrance", "role": "Forward"},
    ],

    # 📊 Impact Stats (used in mission & fundraising section)
    "impact_stats": [
        {"label": "Players Enrolled", "value": 16},
        {"label": "Honor Roll Scholars", "value": 11},
        {"label": "Tournaments Played", "value": 12},
        {"label": "Years Running", "value": 3},
    ],

    # ⬇️ Expand with onboarding form later
    # "sponsor_tiers": [...],
    # "event_countdown": {...},
    # "custom_domain": "elite.connectatx.org",
}


# ───────────────────────────────────────────────
# CONFIG CLASSES — Per-environment overrides
# ───────────────────────────────────────────────

class Config:
    """Base configuration with defaults and helper methods."""
    
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret")

    @staticmethod
    def get_db_uri() -> str:
        """
        Construct full absolute path to the SQLite database.
        """
        db_path = Path(__file__).resolve().parent.parent / "data" / "app.db"
        print(f"[team_config.py] 🗃️ Using SQLite DB at: {db_path}")
        return f"sqlite:///{db_path}"

    SQLALCHEMY_DATABASE_URI = get_db_uri.__func__()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Defaults for CORS, rate limiting, logging ──
    CORS_ALLOW_ORIGINS = "*"
    LIMITER_REDIS_URL = "memory://"
    LOG_LEVEL = "INFO"
    LOG_FILE = None


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    LOG_FILE = "development.log"
    CORS_ALLOW_ORIGINS = "*"
    LIMITER_REDIS_URL = "memory://"


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    LOG_LEVEL = "INFO"
    LOG_FILE = "/var/log/connect_atx_elite/app.log"  # Set by deploy target
    CORS_ALLOW_ORIGINS = "https://yourproductiondomain.com"
    LIMITER_REDIS_URL = "redis://localhost:6379"

