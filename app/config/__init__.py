# app/config/__init__.py
from __future__ import annotations

"""
Config entrypoint for the app.

Usage in factory:
    app.config.from_object("app.config.config.DevelopmentConfig")
or pick by env:
    from app.config import get_config
    app.config.from_object(get_config())

Also exposes TEAM_CONFIG (merged env/file/defaults) for templates/views.
"""

import os
from typing import Type, Dict

# Concrete config classes
from .config import DevelopmentConfig, TestingConfig, ProductionConfig

# TEAM config (content + helpers live here, not in models)
from .team_config import TEAM_CONFIG, get_team_config  # noqa: F401

# Public mapping for convenience (e.g., CLI, tests)
config_by_name: Dict[str, Type[object]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

def get_config(env: str | None = None) -> Type[object]:
    """
    Return a config class based on ENV/FLASK_ENV or provided name.
    Defaults to DevelopmentConfig.
    """
    name = (env or os.getenv("ENV") or os.getenv("FLASK_ENV") or "development").lower()
    return config_by_name.get(name, DevelopmentConfig)

# Handy shorthands if you like importing symbols
config = get_config()
team_config = TEAM_CONFIG

__all__ = [
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
    "config_by_name",
    "get_config",
    "config",
    "TEAM_CONFIG",
    "team_config",
    "get_team_config",
]

