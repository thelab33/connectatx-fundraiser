# app/config/config.py
from __future__ import annotations

"""
Starforge / FundChamps – Flask configuration

Use from your factory like:
    app.config.from_object("app.config.config.DevelopmentConfig")
or via env:
    FLASK_CONFIG=app.config.config.ProductionConfig
"""

import json
import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Final


# ── Helpers ──────────────────────────────────────────────────────────────────
def _bool(key: str, default: bool | str = False) -> bool:
    val = str(os.getenv(key, default)).strip().lower()
    return val in {"1", "true", "yes", "on"}

def _int(key: str, default: int | str) -> int:
    try:
        return int(os.getenv(key, default))
    except Exception:
        raise RuntimeError(f"⚠️ Env var {key} must be an integer, got: {os.getenv(key)!r}")

def _sqlite_uri(base_dir: Path) -> str:
    data_dir = base_dir / "app" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{data_dir/'app.db'}"


# ── Paths ────────────────────────────────────────────────────────────────────
# …/repo-root/app/config/config.py  -> parents[2] == repo root
BASE_DIR: Final[Path] = Path(__file__).resolve().parents[2]


# ── Base Config (shared) ─────────────────────────────────────────────────────
class BaseConfig:
    # Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-override-me")
    ENV = os.getenv("ENV") or os.getenv("FLASK_ENV") or "development"
    DEBUG = False
    TESTING = False

    # Sessions
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Flask JSON defaults (factory also sets these, but harmless here)
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = False

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = _bool("SQLALCHEMY_ECHO", False)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
    }

    # Mail (Flask-Mail)
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = _int("MAIL_PORT", 587)
    MAIL_USE_TLS = _bool("MAIL_USE_TLS", True)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")
    # Alias used elsewhere in your code:
    DEFAULT_MAIL_SENDER = MAIL_DEFAULT_SENDER

    # Payments
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
    PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")

    # CORS / Socket
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")
    PRIMARY_ORIGIN = os.getenv("PRIMARY_ORIGIN", "https://connect-atx-elite.com")
    SOCKET_ASYNC_MODE = os.getenv("SOCKET_ASYNC_MODE", "threading")  # matches your SocketIO init

    # Cache / Redis (optional)
    REDIS_URL = os.getenv("REDIS_URL")
    CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", REDIS_URL)

    # Feature Flags
    FEATURE_CONFETTI = _bool("FEATURE_CONFETTI", True)
    FEATURE_DARK_MODE = _bool("FEATURE_DARK_MODE", False)
    FEATURE_AI_THANK_YOU = _bool("FEATURE_AI_THANK_YOU", False)

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    WERKZEUG_LOG_LEVEL = os.getenv("WERKZEUG_LOG_LEVEL", "WARNING")

    @classmethod
    def init_app(cls, app):
        # Basic logging config
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=cls.LOG_LEVEL,
                format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            )
        # Ensure alias consistency for email helpers
        app.config.setdefault("DEFAULT_MAIL_SENDER", app.config.get("MAIL_DEFAULT_SENDER"))

        # Optionally print config at boot
        if _bool("PRINT_CONFIG_AT_BOOT", False):
            printable = {k: v for k, v in app.config.items() if k.isupper()}
            print("🔧 Loaded Config:", cls.__name__)
            print(json.dumps(printable, indent=2, default=str))


# ── Environments ─────────────────────────────────────────────────────────────
class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or _sqlite_uri(BASE_DIR)


class TestingConfig(BaseConfig):
    ENV = "testing"
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    ENV = "production"
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or _sqlite_uri(BASE_DIR)

    @classmethod
    def init_app(cls, app):
        super().init_app(app)
        # Be helpful but not blocking for day-one launch:
        missing_warn = []
        if not app.config.get("SECRET_KEY") or app.config.get("SECRET_KEY") == "dev-secret-override-me":
            missing_warn.append("SECRET_KEY")
        if not app.config.get("STRIPE_SECRET_KEY"):
            missing_warn.append("STRIPE_SECRET_KEY")
        if not app.config.get("STRIPE_WEBHOOK_SECRET"):
            missing_warn.append("STRIPE_WEBHOOK_SECRET")
        if missing_warn:
            app.logger.warning("⚠️ Missing recommended env vars for production: %s", ", ".join(missing_warn))


# ── Mapping for factories / CLIs ─────────────────────────────────────────────
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

