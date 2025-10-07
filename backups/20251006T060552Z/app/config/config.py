# app/config/config.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Optional


# ── Helpers ────────────────────────────────────────────────────────────────
def _as_bool(val: Optional[str] | bool, default: bool = False) -> bool:
    if isinstance(val, bool):
        return val
    if val is None:
        return bool(default)
    return str(val).strip().lower() in {"1", "true", "yes", "on"}

def _repo_root() -> Path:
    # this file lives at app/config/config.py → parents[2] is repo root
    return Path(__file__).resolve().parents[2]

def _normalize_sqlite(uri: str) -> str:
    """
    If DATABASE_URL is sqlite and relative, make it repo-root anchored.
    Ensures parent directory exists.
    """
    raw = uri.split("sqlite:///")[1]
    p = Path(raw)
    if not p.is_absolute():
        p = (_repo_root() / raw).resolve()
    p.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{p.as_posix()}"

def _database_url() -> str:
    """
    DATABASE_URL precedence:
      1) Use DATABASE_URL if set (normalize sqlite paths).
      2) Default to sqlite under repo/app/data/app.db.
    """
    url = (os.getenv("DATABASE_URL") or "").strip()
    if url:
        if url.startswith("sqlite:///"):
            return _normalize_sqlite(url)
        return url
    default_db = _repo_root() / "app" / "data" / "app.db"
    default_db.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{default_db.as_posix()}"


# ── Base config ─────────────────────────────────────────────────────────────
class BaseConfig:
    # Flask core
    ENV = os.getenv("ENV") or os.getenv("FLASK_ENV", "development")
    DEBUG = _as_bool(os.getenv("FLASK_DEBUG"), default=(ENV == "development"))
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    JSON_SORT_KEYS = False
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "http")

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}

    # Payments (support legacy alias envs)
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY") or os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Realtime
    SOCKETIO_ASYNC_MODE = (
        os.getenv("SOCKETIO_ASYNC_MODE")
        or os.getenv("SOCKET_ASYNC_MODE")
        or "threading"
    )

    # Security (cookies/sessions)
    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "fundchamps")
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = False   # tightened in Production
    REMEMBER_COOKIE_SECURE = False  # tightened in Production

    # CORS (only used if you enable CORS in the app)
    CORS_ORIGINS = os.getenv("CORS_ORIGINS")  # e.g. "https://a.com,https://b.com"

    # Sentry (opt-in)
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES", "0.0"))

    # Analytics / UI (optional)
    GA_ID = os.getenv("GA_ID")
    POSTHOG_KEY = os.getenv("POSTHOG_KEY")
    POSTHOG_HOST = os.getenv("POSTHOG_HOST", "https://app.posthog.com")
    WEB_MANIFEST = os.getenv("WEB_MANIFEST")  # e.g. "site.webmanifest"


class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False


class ProductionConfig(BaseConfig):
    ENV = "production"
    DEBUG = False
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    # If deploying behind a proxy and you enable ProxyFix in your launcher:
    USE_X_SENDFILE = _as_bool(os.getenv("USE_X_SENDFILE"))
    APPLICATION_ROOT = os.getenv("APPLICATION_ROOT", "/")


class TestingConfig(BaseConfig):
    ENV = "testing"
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


# Handy lookup if you prefer FLASK_CONFIG="app.config.ProductionConfig"
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

