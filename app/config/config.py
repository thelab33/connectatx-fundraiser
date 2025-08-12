import os
import json
from datetime import timedelta
from typing import Final, Dict, Type

# ────────────── Directory Constants ──────────────
BASE_DIR: Final = os.path.abspath(os.path.dirname(__file__))

# ────────────── Env Helpers (blank-safe) ──────────────
def _raw(key: str) -> str | None:
    """Return trimmed env var or None if missing/blank."""
    val = os.getenv(key)
    if val is None:
        return None
    val = str(val).strip()
    return val or None

def _str(key: str, default: str) -> str:
    val = _raw(key)
    return default if val is None else val

def _bool(key: str, default: bool = False) -> bool:
    val = _raw(key)
    if val is None:
        return bool(default)
    return val.lower() in {"1", "true", "yes", "y", "on"}

def _int(key: str, default: int) -> int:
    val = _raw(key)
    if val is None:
        return int(default)
    try:
        return int(val)
    except (ValueError, TypeError):
        # In production: fail fast. In non-prod: fall back to default.
        if _str("FLASK_ENV", "production").lower() == "production":
            raise RuntimeError(f"Env var {key} must be integer, got: {os.getenv(key)}")
        return int(default)

def _masked(val: str | None, keep: int = 4) -> str | None:
    """Mask secrets for console output."""
    if not val:
        return val
    s = str(val)
    if len(s) <= 8:
        return "••••"
    return f"{s[:keep]}…{'•' * (len(s) - keep - 1)}"

def _export_config(cls) -> dict:
    out = {k: v for k, v in cls.__dict__.items() if k.isupper()}
    for k in ("SECRET_KEY", "STRIPE_SECRET_KEY", "STRIPE_PUBLIC_KEY", "MAIL_PASSWORD"):
        if k in out:
            out[k] = _masked(out[k])
    return out

# ────────────── Base Config ──────────────
class BaseConfig:
    SECRET_KEY: str = _str("SECRET_KEY", "change-me-before-prod")
    ENV: Final[str] = _str("FLASK_ENV", "production")
    DEBUG: bool = _bool("DEBUG", False)
    LOG_LEVEL: Final[str] = _str("LOG_LEVEL", "INFO").upper()

    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(days=7)

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = _str(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/app/data/app.db",
    )

    # Payments
    STRIPE_SECRET_KEY: str | None = _raw("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY: str | None = _raw("STRIPE_PUBLIC_KEY")

    # Mail
    MAIL_SERVER: str = _str("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT: int = _int("MAIL_PORT", 587)
    MAIL_USE_TLS: bool = _bool("MAIL_USE_TLS", True)
    MAIL_USERNAME: str | None = _raw("MAIL_USERNAME")
    MAIL_PASSWORD: str | None = _raw("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: str = _str("MAIL_DEFAULT_SENDER", "noreply@connectatxelite.com")
    MAIL_SUPPRESS_SEND: bool = _bool("MAIL_SUPPRESS_SEND", False)  # handy for local

    # Brand
    FEATURE_DARK_MODE: bool = _bool("FEATURE_DARK_MODE", True)
    BRAND_NAME: str = _str("BRAND_NAME", "Connect ATX Elite")
    BRAND_TAGLINE: str = _str(
        "BRAND_TAGLINE",
        "Family-run AAU basketball building future leaders in East Austin.",
    )
    PRIMARY_COLOR: str = _str("PRIMARY_COLOR", "#facc15")

    @classmethod
    def init_app(cls, app):
        """Attach config to Flask app & set up logging."""
        import logging
        logging.basicConfig(
            level=cls.LOG_LEVEL,
            format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
        )
        if _bool("PRINT_CONFIG", False):
            app.logger.info(f"Loaded config: {cls.__name__}")
            print(json.dumps(_export_config(cls), indent=2))

class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True
    # default to not actually sending emails in dev unless overridden
    MAIL_SUPPRESS_SEND: bool = _bool("MAIL_SUPPRESS_SEND", True)

class TestingConfig(BaseConfig):
    ENV = "testing"
    TESTING = True  # type: ignore[attr-defined]
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = _str(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR}/app/data/app.db",
    )
    MAIL_SUPPRESS_SEND: bool = True

class ProductionConfig(BaseConfig):
    ENV = "production"
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    REQUIRED_VARS: Final[tuple[str, ...]] = (
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
        missing = [v for v in cls.REQUIRED_VARS if not _raw(v)]
        if missing:
            raise RuntimeError(f"Missing required environment vars: {', '.join(missing)}")

config_map: Dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

def get_config() -> Type[BaseConfig]:
    """Return the config class for current FLASK_ENV."""
    return config_map.get(_str("FLASK_ENV", "production"), ProductionConfig)

config = get_config()

