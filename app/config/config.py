# app/config.py
import os
from datetime import timedelta
from typing import Final

# ────────────── Directory Constants ──────────────
BASE_DIR: Final = os.path.abspath(os.path.dirname(__file__))

# ────────────── Env Helpers ──────────────
def _bool(key: str, default: bool = False) -> bool:
    return os.getenv(key, str(int(default))).strip().lower() in {"1", "true", "yes", "on"}

def _int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        raise RuntimeError(f"Env var {key} must be integer, got: {os.getenv(key)}")

# ────────────── Base Config ──────────────
class BaseConfig:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-before-prod")
    ENV: Final = os.getenv("FLASK_ENV", "production")
    DEBUG: bool = _bool("DEBUG", False)
    LOG_LEVEL: Final = os.getenv("LOG_LEVEL", "INFO").upper()
    PERMANENT_SESSION_LIFETIME: timedelta = timedelta(days=7)
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR}/app/data/app.db"

    STRIPE_SECRET_KEY: str | None = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLIC_KEY: str | None = os.getenv("STRIPE_PUBLIC_KEY")

    MAIL_SERVER: str = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_PORT: int = _int("MAIL_PORT", 587)
    MAIL_USE_TLS: bool = _bool("MAIL_USE_TLS", True)
    MAIL_USERNAME: str | None = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str | None = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER: str = os.getenv("MAIL_DEFAULT_SENDER", "noreply@connectatxelite.com")

    FEATURE_DARK_MODE: bool = _bool("FEATURE_DARK_MODE", True)
    BRAND_NAME: str = os.getenv("BRAND_NAME", "Connect ATX Elite")
    BRAND_TAGLINE: str = os.getenv("BRAND_TAGLINE", "Family-run AAU basketball building future leaders in East Austin.")
    PRIMARY_COLOR: str = os.getenv("PRIMARY_COLOR", "#facc15")

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
            print(
                json.dumps(
                    {k: v for k, v in cls.__dict__.items() if k.isupper()},
                    indent=2,
                )
            )

class DevelopmentConfig(BaseConfig):
    ENV = "development"
    DEBUG = True

class TestingConfig(BaseConfig):
    ENV = "testing"
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{BASE_DIR}/app/data/app.db"

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
        missing = [v for v in cls.REQUIRED_VARS if not os.getenv(v)]
        if missing:
            raise RuntimeError(
                f"Missing required environment vars: {', '.join(missing)}"
            )

config_map: dict[str, type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

def get_config() -> type[BaseConfig]:
    """Return the config class for current FLASK_ENV."""
    return config_map.get(os.getenv("FLASK_ENV", "production"), ProductionConfig)

config = get_config()

