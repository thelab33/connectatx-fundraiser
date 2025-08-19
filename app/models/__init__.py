# app/models/__init__.py
"""
Autoload all models and mixins for Starforge/FundChamps SaaS.

Benefits
--------
- Centralized imports for: `from app.models import Team, Player, Sponsor, ...`
- Ensures Alembic autogeneration sees all models (explicit + optional + discovery)
- Handles optional/experimental models gracefully with logging
- Utilities to introspect loaded models (for admin, seeds, etc.)
"""
from __future__ import annotations

import importlib
import inspect
import logging
import os
import pkgutil
from types import ModuleType
from typing import Any, List, Optional, Tuple, Type

from app.extensions import db  # expose db everywhere

logger = logging.getLogger(__name__)

# ───────────────────────────────────────────────────────────────────────────────
# Mixins (safe, lightweight)
# ───────────────────────────────────────────────────────────────────────────────
from .mixins import TimestampMixin, SoftDeleteMixin  # noqa: F401

# ───────────────────────────────────────────────────────────────────────────────
# Core models (explicit = clearer errors + stable ordering)
# ───────────────────────────────────────────────────────────────────────────────
from .team import Team  # noqa: F401
from .player import Player  # noqa: F401
from .sponsor import Sponsor  # noqa: F401
from .transaction import Transaction  # noqa: F401
from .campaign_goal import CampaignGoal  # noqa: F401
from .sponsor_click import SponsorClick  # noqa: F401  # analytics beacons table

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
            # keep noise low in production; INFO is fine
            logger.info("ℹ️ Optional model '%s' not loaded: %s", class_name, e)


_try_import_optional()

# ───────────────────────────────────────────────────────────────────────────────
# Optional: directory auto-discovery
# - Scans app/models/ for modules that define SQLAlchemy models and imports them.
# - Skips known non-model files.
# - Controlled by env flag: MODELS_AUTODISCOVER (default: True)
#   Set to False if you want to only rely on explicit imports above.
# ───────────────────────────────────────────────────────────────────────────────
_AUTODISCOVER = os.getenv("MODELS_AUTODISCOVER", "true").lower() not in {"0", "false", "no"}
_DISCOVERY_SKIP = {
    "__init__", "mixins", "base", "enums", "types", "typing", "tests", "test", "conftest",
    # explicitly-loaded core files (avoid double-work)
    "team", "player", "sponsor", "transaction", "campaign_goal", "sponsor_click",
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
                # pull any db.Model subclasses into globals() so Alembic sees them
                for name, obj in inspect.getmembers(module, _is_sqla_model):
                    if name not in globals():
                        globals()[name] = obj
                    loaded.append(name)
                    exported += 1
                if exported:
                    logger.debug("🔎 Discovered %d model(s) in '%s': %s", exported, modname, ", ".join(n for n in loaded if n in globals()))
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
    # core
    "Team", "Player", "Sponsor", "Transaction", "CampaignGoal", "SponsorClick",
    # optionals
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
    Useful for admin registries, seed generators, etc. (framework-agnostic).
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


# Eager check (debug only): helps catch typos while developing
if os.getenv("FLASK_DEBUG", "1").lower() not in {"0", "false", "no"}:
    try:
        _cnt = len(iter_sqla_models())
        logger.debug(
            "📦 models loaded: %d (core=%d, optional=%d, discovered=%d)",
            _cnt, 6, len(_loaded_optional), len(_loaded_discovered),
        )
    except Exception:
        pass

