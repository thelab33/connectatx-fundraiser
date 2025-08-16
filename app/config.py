from __future__ import annotations

"""
Starforge SaaS — Flask Config Loader (Enhanced)
"""

import json
import logging
import os
import sys
from datetime import timedelta
from pathlib import Path
from typing import Final, Iterable

# ─── Env Helpers ──────────────────────────────────────────────────────────────
def _bool(key: str, default: str | bool = "false") -> bool:
    """Return env var as bool, handling common truthy/falsy strings."""
    val = os.getenv(key, str(default)).strip().lower()
    return val in {"1", "true", "yes", "on"}

def _int(key: str, default: int | str) -> int:
    """Return env var as int, raise if invalid."""
    try:
        return int(os.getenv(key, default))
    except ValueError:
        raise RuntimeError(f"⚠️ Env var {key} must be an integer, got: {os.getenv(key)}")

def _str(key: str, default: str | None = None) -> str | None:
    """Return env var as string, strip surrounding whitespace."""
    val = os.getenv(key, default)
    return val.strip() if isinstance(val, str) else val

# ─── Base Path ────────────────────────────────────────────────────────────────
BASE_DIR: Final[Path] = Path(__file__).resolve().parents[2]

# ─── Base Config ──────────────────────────────────────────────────────────────
class BaseConfig:
    """Base configuration shared across environments."""

    # Core Flask
    SECRET_KEY = _str("SECRET_KEY", "dev-secret-override-me")
    SESSION_COOKIE_SECURE = _bool("SESSION_COOKIE_SECURE", False)
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    USE_CLI = _bool("USE_CLI", True)

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email (Flask-Mail)
    MAIL_SERVER = _str("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT = _int("MAIL_PORT", 587)
    MAIL_USE_TLS = _bool("MAIL_USE_TLS", True)
    MAIL_USERNAME = _str("MAIL_USERNAME")
    MAIL_PASSWORD = _str("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = _str("MAIL_DEFAULT_SENDER", "noreply@example.com")

    # Payments
    STRIPE_SECRET_KEY = _str("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY = _str("STRIPE_PUBLIC_KEY")
    STRIPE_WEBHOOK_SECRET = _str("STRIPE_WEBHOOK_SECRET")
    PAYPAL_CLIENT_ID = _str("PAYPAL_CLIENT_ID")
    PAYPAL_SECRET = _str("PAYPAL_SECRET")

    # Redis / Cache
    REDIS_URL = _str("REDIS_URL")
    CACHE_TYPE = _str("CACHE_TYPE", "simple")
    CACHE_REDIS_URL = _str("CACHE_REDIS_URL", REDIS_URL)

    # Feature Flags
    FEATURE_CONFETTI = _bool("FEATURE_CONFETTI")
    FEATURE_DARK_MODE = _bool("FEATURE_DARK_MODE")
    FEATURE_AI_THANK_YOU = _bool("FEATURE_AI_THANK_YOU")

    # Logging
    LOG_LEVEL = _str("LOG_LEVEL", "INFO").upper()

    @classmethod
    def init_app(cls, app):
        """Init app with logging and optional config print."""
        logging.basicConfig(
            level=cls.LOG_LEVEL,
            format="\033[1;36m[%(levelname)s]\033[0m %(message)s",
            stream=sys.stdout
        )
        if _bool("PRINT_CONFIG_AT_BOOT"):
            print(f"🔧 Loaded Config: {cls.__name__}")
            cfg = {}
            for k, v in cls.__dict__.items():
                if k.isupper() and not callable(v):
                    if "KEY" in k or "PASSWORD" in k or "SECRET" in k:
                        cfg[k] = "***MASKED***" if v else None
                    else:
                        cfg[k] = v
            print(json.dumps(cfg, indent=2, default=str))

# ─── Environment-Specific Configs ─────────────────────────────────────────────
class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _str(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/app/data/dev.db"
    )

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
    SQLALCHEMY_DATABASE_URI = _str(
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
        super().init_app(app)
        missing = [v for v in cls.REQUIRED_VARS if not os.getenv(v)]
        if missing:
            raise RuntimeError(f"❌ Missing required environment variables: {', '.join(missing)}")

# ─── Config Mapping ───────────────────────────────────────────────────────────
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

