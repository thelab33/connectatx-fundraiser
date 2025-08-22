from __future__ import annotations

"""
Starforge SaaS — Flask Config Loader

Usage:
    app.config.from_object("app.config.config.DevelopmentConfig")

Priority:
1. Explicit `app.config`
2. Environment variables (12-factor style)
3. Safe fallback defaults (NEVER for prod secrets)
"""

import json
import logging
import os
from datetime import timedelta
from pathlib import Path
from typing import Final, Iterable

# ─── Env Helper Functions ─────────────────────────────────────────────────────

def _bool(key: str, default: str | bool = "false") -> bool:
    """
    Fetches and converts an environment variable to a boolean.
    Handles common truthy and falsy values.
    """
    val = os.getenv(key, str(default)).strip().lower()
    return val in {"1", "true", "yes", "on"}

def _int(key: str, default: int | str) -> int:
    """
    Fetches and converts an environment variable to an integer.
    Raises a runtime exception if the conversion fails.
    """
    try:
        return int(os.getenv(key, default))
    except ValueError:
        raise RuntimeError(f"⚠️ Env var {key} must be an integer, got: {os.getenv(key)}")

# ─── Base Path for Relatives ──────────────────────────────────────────────────

BASE_DIR: Final[Path] = Path(__file__).resolve().parents[2]

# ─── Base Config ─ Shared across all environments ─────────────────────────────

class BaseConfig:
    """
    Base configuration with common settings shared across all environments.
    """
    # ─── Core Flask ───────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-override-me")
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # ─── SQLAlchemy ──────────────────────────────
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ─── Email (Flask-Mail) ──────────────────────
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = _int("MAIL_PORT", 587)
    MAIL_USE_TLS = _bool("MAIL_USE_TLS", True)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")

    # ─── Stripe ──────────────────────────────────
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # ─── Redis / Caching ─────────────────────────
    REDIS_URL = os.getenv("REDIS_URL")
    CACHE_TYPE = os.getenv("CACHE_TYPE", "simple")
    CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL", REDIS_URL)

    # ─── Feature Flags ───────────────────────────
    FEATURE_CONFETTI = _bool("FEATURE_CONFETTI")
    FEATURE_DARK_MODE = _bool("FEATURE_DARK_MODE")
    FEATURE_AI_THANK_YOU = _bool("FEATURE_AI_THANK_YOU")

    # ─── Logging ─────────────────────────────────
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    @classmethod
    def init_app(cls, app):
        """
        Initializes the Flask app with logging and optional configuration printing.
        """
        logging.basicConfig(level=cls.LOG_LEVEL, format="[%(levelname)s] %(message)s")
        if _bool("PRINT_CONFIG_AT_BOOT"):
            print("🔧 Loaded Config:", cls.__name__)
            cfg = {k: v for k, v in cls.__dict__.items() if k.isupper() and not callable(v)}
            print(json.dumps(cfg, indent=2, default=str))


# ─── Environment-Specific Configs ─────────────────────────────────────────────

class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    ENV = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://starforge_user:StarforgeDevPass@localhost:3306/starforge_dev"
    )


class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    ENV = "testing"
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    ENV = "production"
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/app/data/app.db"
    )

    REQUIRED_VARS: Iterable[str] = (
        "SECRET_KEY",
        "STRIPE_SECRET_KEY",
        "STRIPE_PUBLIC_KEY",
        "MAIL_SERVER",
        "MAIL_USERNAME",
        "MAIL_PASSWORD",
    )

    @classmethod
    def init_app(cls, app):
        """
        Initializes the Flask app for production, ensuring all required variables are set.
        """
        super().init_app(app)
        missing = [v for v in cls.REQUIRED_VARS if not os.getenv(v)]
        if missing:
            raise RuntimeError(f"❌ Missing required environment variables: {', '.join(missing)}")


# ─── Config Mapping for Factory Use ───────────────────────────────────────────

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

