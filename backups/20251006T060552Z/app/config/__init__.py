# app/config/__init__.py
from .config import (
    BaseConfig,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    config_by_name,
)

Config = BaseConfig  # optional alias

