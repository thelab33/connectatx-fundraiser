# app/config/__init__.py
"""
FundChamps Config Package (canonical import path)
Use:
    FLASK_CONFIG=app.config.DevelopmentConfig
"""

# Prefer the richer definitions in app/config/config.py if present.
try:
    from .config import BaseConfig, DevelopmentConfig, TestingConfig, ProductionConfig  # type: ignore
except Exception:
    # Fallback to legacy single-file config at app/config.py (if someone kept it)
    from ..config import BaseConfig, DevelopmentConfig, ProductionConfig  # type: ignore

config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

