# app/models/__init__.py
"""
Central model registry for FundChamps.

Why this exists
---------------
- One import for everything: `from app.models import Team, Player, ...`
- Ensures Alembic autogenerate sees ALL models (explicit first, then optional/discovered)
- Stable, explicit core ordering → deterministic migrations
- Optional models + auto-discovery kept, but sandboxed and low-noise
"""
from __future__ import annotations

import importlib
import inspect
import logging
import os
import pkgutil
from types import ModuleType
from typing import Any, Iterable, List, Optional, Tuple, Type
from .shoutout import Shoutout  # ✅ NEW

from app.extensions import db  # re-exported

logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────────────────────────────────────
# Mixins (safe, lightweight)
# ───────────────────────────────────────────────────────────────────────────────
from .mixins import TimestampMixin, SoftDeleteMixin  # noqa: F401

# ───────────────────────────────────────────────────────────────────────────────
# Core models (explicit imports → clear errors + stable ordering)
#   NOTE: keep these as the source of truth for Alembic ordering.
# ───────────────────────────────────────────────────────────────────────────────
from .team import Team  # noqa: F401
from .player import Player  # noqa: F401
from .sponsor import Sponsor  # noqa: F401
from .transaction import Transaction  # noqa: F401
from .campaign_goal import CampaignGoal  # noqa: F401
from .sponsor_click import SponsorClick  # noqa: F401
from .newsletter import NewsletterSignup  # ✅ NEW core model
from .shoutout import Shoutout  # ✅ promote to core (and export)

_CORE_NAMES: tuple[str, ...] = (
    "Team",
    "Player",
    "Sponsor",
    "Transaction",
    "CampaignGoal",
    "SponsorClick",
    "NewsletterSignup",
    "Shoutout",
)

# ───────────────────────────────────────────────────────────────────────────────
# Optional models that may or may not exist in a given deployment
# (module_name, class_name)
# ───────────────────────────────────────────────────────────────────────────────
OPTIONAL_MODELS: List[Tuple[str, str]] = [
    ("example", "Example"),
    ("sms_log", "SMSLog"),
    ("user", "User"),
]

_loaded_optional: List[str] = []


def _iter_candidates(x: str | Iterable[str]) -> list[str]:
    if isinstance(x, str):
        return [p.strip() for p in x.split("|")] if "|" in x else [x]
    return [str(p) for p in x]


def _try_import_optional() -> None:
    for module_name, class_name in OPTIONAL_MODELS:
        modpath = f"app.models.{module_name}"
        try:
            module: ModuleType = importlib.import_module(modpath)
            model_cls = getattr(module, class_name)
            globals()[class_name] = model_cls  # export into this package
            _loaded_optional.append(class_name)
            logger.debug("✅ Loaded optional model: %s from '%s'", class_name, module_name)
        except (ImportError, AttributeError) as e:
            logger.info("ℹ️ Optional model '%s' not loaded: %s", class_name, e)


_try_import_optional()

# ───────────────────────────────────────────────────────────────────────────────
# Optional: directory auto-discovery
# - Scans app/models/ for modules that define SQLAlchemy models and imports them.
# - Skips known non-model files and all explicit core modules.
# - Controlled by env flag: MODELS_AUTODISCOVER (default: True)
# ───────────────────────────────────────────────────────────────────────────────
_AUTODISCOVER = os.getenv("MODELS_AUTODISCOVER", "true").lower() not in {"0", "false", "no"}
_DISCOVERY_SKIP = {
    "__init__", "mixins", "base", "enums", "types", "typing", "tests", "test", "conftest",
    # explicitly-loaded core files (avoid double-work)
    "team", "player", "sponsor", "transaction", "campaign_goal", "sponsor_click",
    "newsletter", "shoutout",
    # known optionals already handled
    *{m for m, _ in OPTIONAL_MODELS},
}


def _is_sqla_model(obj: Any) -> bool:
    """Best-effort: object is a subclass of db.Model (but not the base class)."""
    try:
        return inspect.isclass(obj) and issubclass(obj, db.Model) and obj is not db.Model
    except Exception:
        return False


def _discover_models(package_name: str = "app.models") -> List[str]:
    if not _AUTODISCOVER:
        logger.debug("Model discovery disabled via MODELS_AUTODISCOVER=0")
        return []

    loaded: List[str] = []
    try:
        pkg = importlib.import_module(package_name)
        pkg_path = getattr(pkg, "__path__", None)
        if not pkg_path:
            return []

        for _finder, modname, ispkg in pkgutil.iter_modules(pkg_path):
            if ispkg or modname in _DISCOVERY_SKIP or modname.startswith(("_", ".")):
                continue
            try:
                module = importlib.import_module(f"{package_name}.{modname}")
                exported = 0
                for name, obj in inspect.getmembers(module, _is_sqla_model):
                    if name not in globals():
                        globals()[name] = obj
                    loaded.append(name)
                    exported += 1
                if exported:
                    logger.debug(
                        "🔎 Discovered %d model(s) in '%s': %s",
                        exported, modname, ", ".join(n for n in loaded if n in globals())
                    )
            except Exception as e:
                logger.info("ℹ️ Skipped auto-import of '%s' due to: %s", modname, e)
                continue
    except Exception as e:
        logger.info("ℹ️ Model discovery unavailable: %s", e)

    return loaded


_loaded_discovered = _discover_models()

# ───────────────────────────────────────────────────────────────────────────────
# Public API
# ───────────────────────────────────────────────────────────────────────────────
__all__ = [
    # db + mixins
    "db", "TimestampMixin", "SoftDeleteMixin",
    # core (explicit, ordered)
    *_CORE_NAMES,
    # optionals (if present)
    *_loaded_optional,
    # discovered (if any)
    *_loaded_discovered,
]

# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────
def iter_models() -> List[Any]:
    """
    Returns all exported names in __all__ that look like classes (TitleCase).
    Useful for admin registries, seed generators, etc.
    """
    out: List[Any] = []
    for name in __all__:
        obj = globals().get(name)
        if inspect.isclass(obj) and name[:1].isupper():
            out.append(obj)
    return out


def iter_sqla_models() -> List[Type[db.Model]]:
    """Returns only SQLAlchemy model classes (subclasses of db.Model)."""
    return [m for m in iter_models() if _is_sqla_model(m)]


def get_model(name: str) -> Optional[Type[Any]]:
    """Lookup a model class by exported name, case-sensitive."""
    return globals().get(name)


# Debug summary (only in dev)
if os.getenv("FLASK_DEBUG", "1").lower() not in {"0", "false", "no"}:
    try:
        _cnt = len(iter_sqla_models())
        logger.debug(
            "📦 models loaded: %d (core=%d, optional=%d, discovered=%d)",
            _cnt, len(_CORE_NAMES), len(_loaded_optional), len(_loaded_discovered),
        )
    except Exception:
        pass

