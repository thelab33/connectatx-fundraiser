import os
from app.config.config import DevelopmentConfig, ProductionConfig

# Optional: add TestingConfig, StagingConfig, etc., as needed
try:
    from app.config.config import TestingConfig
except ImportError:
    TestingConfig = None
    print("⚠️ TestingConfig not found. Defaulting to development config.")

# Try importing team config (handle failure gracefully)
try:
    from app.config.team_config import TEAM_CONFIG
except ImportError:
    TEAM_CONFIG = {}
    try:
        # Log the warning within Flask's app context if available
        from flask import current_app
        current_app.logger.warning("⚠️ TEAM_CONFIG not found, using empty config.")
    except Exception:
        print("⚠️ TEAM_CONFIG not found, using empty config.")

# Master config map, adding optional configurations if available
CONFIGS = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}

# If TestingConfig is available, add it to the map
if TestingConfig:
    CONFIGS["testing"] = TestingConfig

# Always include TEAM_CONFIG in the config dictionary
CONFIGS["team_config"] = TEAM_CONFIG

def get_config(env: str = None) -> object:
    """
    Returns the config class based on environment variable or argument.
    Defaults to 'development' if not specified or unknown.
    """
    env = env or os.getenv("FLASK_ENV", "development")
    # Ensure 'development' config is the fallback if unknown env
    return CONFIGS.get(env, DevelopmentConfig)

# Shorthand for quick import elsewhere
config = get_config()
team_config = TEAM_CONFIG

