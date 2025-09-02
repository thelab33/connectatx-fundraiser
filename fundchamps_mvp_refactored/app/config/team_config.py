# app/config/team_config.py
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# ────────────────────────────────────────────────────────────
# Paths & logging
# ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parents[2]  # repo root
APP_DIR = BASE_DIR / "app"
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

log = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────
# Env helpers
# ────────────────────────────────────────────────────────────
def env(key: str, default: Optional[str] = None) -> str:
    return os.getenv(key, default) or ("" if default is None else default)


def env_bool(key: str, default: bool = False) -> bool:
    v = os.getenv(key)
    return default if v is None else v.strip().lower() in {"1", "true", "yes", "on"}


def env_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, str(default)))
    except Exception:
        return default


def env_list(key: str, default: List[str] | None = None, sep: str = ",") -> List[str]:
    raw = os.getenv(key)
    if not raw:
        return default or []
    return [p.strip() for p in raw.split(sep) if p.strip()]


def env_json(key: str, default: Dict[str, Any] | None = None) -> Dict[str, Any]:
    raw = os.getenv(key)
    if not raw:
        return default or {}
    try:
        return json.loads(raw)
    except Exception:
        return default or {}


# ────────────────────────────────────────────────────────────
# Database URI
# ────────────────────────────────────────────────────────────
def _sqlite_uri() -> str:
    db_path = DATA_DIR / "app.db"
    log.info("[team_config] Using SQLite DB at: %s", db_path)
    return f"sqlite:///{db_path}"


SQLALCHEMY_DATABASE_URI_DEFAULT = os.getenv("DATABASE_URL") or _sqlite_uri()


# ────────────────────────────────────────────────────────────
# Flask config classes
# ────────────────────────────────────────────────────────────
class Config:
    """Base configuration with sensible defaults."""

    SECRET_KEY = env("SECRET_KEY", "dev_secret")

    SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI_DEFAULT
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS / rate limiting / logging defaults
    CORS_ALLOW_ORIGINS = env("CORS_ALLOW_ORIGINS", "*")
    LIMITER_REDIS_URL = env("LIMITER_REDIS_URL", "memory://")
    LOG_LEVEL = env("LOG_LEVEL", "INFO")
    LOG_FILE = env("LOG_FILE", "") or None


class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    LOG_FILE = env("LOG_FILE", "development.log")
    CORS_ALLOW_ORIGINS = "*"
    LIMITER_REDIS_URL = "memory://"


class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = "INFO"
    LOG_FILE = env("LOG_FILE", "/var/log/connect_atx_elite/app.log")
    CORS_ALLOW_ORIGINS = env("CORS_ALLOW_ORIGINS", "https://yourproductiondomain.com")
    LIMITER_REDIS_URL = env("LIMITER_REDIS_URL", "redis://localhost:6379")


def get_flask_config():
    """Pick config class by ENV/FLASK_ENV."""
    mode = (os.getenv("ENV") or os.getenv("FLASK_ENV") or "development").lower()
    return ProductionConfig if mode in {"prod", "production"} else DevelopmentConfig


# ────────────────────────────────────────────────────────────
# Default TEAM_CONFIG (overridable via env / file)
# ────────────────────────────────────────────────────────────
TEAM_CONFIG_DEFAULT: Dict[str, Any] = {
    "team_name": env("TEAM_NAME", "Connect ATX Elite"),
    "location": env("TEAM_LOCATION", "Austin, TX"),
    "logo": env("TEAM_LOGO", "images/logo.webp"),
    "contact_email": env("TEAM_CONTACT_EMAIL", "info@connectatxelite.org"),
    "instagram": env("TEAM_INSTAGRAM", "https://instagram.com/connectatxelite"),
    "custom_domain": env("TEAM_DOMAIN", ""),  # optional vanity domain
    "brand_color": env("TEAM_BRAND_COLOR", "amber-400"),
    "is_trial": env_bool("TEAM_IS_TRIAL", True),
    "fundraising_goal": env_int("TEAM_GOAL", 10_000),
    "amount_raised": env_int("TEAM_RAISED", 7_850),
    "about": [
        "Connect ATX Elite is a community-powered, non-profit 12U AAU basketball program based in Austin, TX.",
        "We develop skilled athletes, but also confident, disciplined, and academically driven young leaders.",
    ],
    "players": [
        {"name": "Andre", "role": "Guard"},
        {"name": "Jordan", "role": "Forward"},
        {"name": "Malik", "role": "Center"},
        {"name": "CJ", "role": "Guard"},
        {"name": "Terrance", "role": "Forward"},
    ],
    "impact_stats": [
        {"label": "Players Enrolled", "value": 16},
        {"label": "Honor Roll Scholars", "value": 11},
        {"label": "Tournaments Played", "value": 12},
        {"label": "Years Running", "value": 3},
    ],
    # 🔐 Impact Lockers (buckets)
    "impact_costs": {
        "gym_month": {
            "label": "Lock the Next Month of Gym",
            "total_cost": 1800,
            "milestones": [
                {"label": "1 practice locked", "cost": 150},
                {"label": "3 practices locked", "cost": 450},
                {"label": "Full week locked", "cost": 600},
            ],
            "details": "Covers ~12 practices at ~$150/practice.",
        },
        "tournament_travel": {
            "label": "Next Travel Tournament",
            "total_cost": 3200,
            "milestones": [
                {"label": "Tournament fee", "cost": 600},
                {"label": "2 hotel rooms/night", "cost": 300},
                {"label": "Fuel & meals", "cost": 250},
            ],
            "details": "Fees, hotel, fuel, and meals for the team.",
        },
        "uniforms": {
            "label": "Uniforms & Gear",
            "total_cost": 2400,  # 16 × $150
            "milestones": [
                {"label": "Outfit 1 player", "cost": 150},
                {"label": "Outfit 4 players", "cost": 600},
            ],
            "details": "Jersey set, shorts, shooter shirt.",
        },
        "unity_day": {
            "label": "Unity Day (Bonding)",
            "total_cost": 600,
            "milestones": [
                {"label": "Lane rental", "cost": 200},
                {"label": "Team pizza", "cost": 150},
                {"label": "Transport", "cost": 250},
            ],
            "details": "Bowling + pizza + transport for the team.",
        },
    },
}


# ────────────────────────────────────────────────────────────
# Load/merge logic (env → file → defaults) + derived fields
# ────────────────────────────────────────────────────────────
def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _load_file_override() -> Dict[str, Any]:
    path = env("TEAM_CONFIG_FILE", "")
    if not path:
        return {}
    try:
        p = Path(path)
        if p.suffix.lower() in {".json"} and p.exists():
            return json.loads(p.read_text())
        # (You can add YAML support here later.)
    except Exception as exc:
        log.warning("TEAM_CONFIG_FILE load failed: %s", exc)
    return {}


def _validate_team_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    # Minimal sanity checks (don’t hard fail in prod)
    goal = max(0, int(cfg.get("fundraising_goal") or 0))
    raised = max(0, int(cfg.get("amount_raised") or 0))
    cfg["fundraising_goal"] = goal
    cfg["amount_raised"] = min(raised, goal or raised)

    # Derived: percent to goal
    cfg["percent_to_goal"] = (
        round((cfg["amount_raised"] / goal * 100.0), 1) if goal else 0.0
    )

    # Ensure impact_costs shapes
    costs = cfg.get("impact_costs") or {}
    for k, bucket in costs.items():
        bucket.setdefault("label", k)
        bucket["total_cost"] = float(bucket.get("total_cost") or 0.0)
        bucket["milestones"] = bucket.get("milestones") or []
        bucket["details"] = bucket.get("details") or ""
    cfg["impact_costs"] = costs
    return cfg


def get_team_config() -> Dict[str, Any]:
    """Final TEAM_CONFIG after env/file merges + validation."""
    file_override = _load_file_override()
    env_override = env_json("TEAM_CONFIG_JSON", {})  # optional full JSON override
    cfg = TEAM_CONFIG_DEFAULT
    cfg = _deep_merge(cfg, file_override)
    cfg = _deep_merge(cfg, env_override)
    cfg = _validate_team_config(cfg)
    return cfg


# Export a ready-to-use dict for convenience
TEAM_CONFIG: Dict[str, Any] = get_team_config()
