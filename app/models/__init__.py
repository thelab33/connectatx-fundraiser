"""
Autoload all models and mixins for Starforge SaaS.
──────────────────────────────────────────────────────
Benefits:
- Centralized imports for easy access:
    from app.models import Team, Player, Sponsor
- Ensures Alembic autogeneration sees all models without scattered imports
- Handles optional/experimental models gracefully with logging
"""

from __future__ import annotations
import logging
from types import ModuleType
from typing import TYPE_CHECKING, Any, List, Tuple

from app.extensions import db  # Expose db for all mixins/models

logger = logging.getLogger(__name__)

# ─── Mixins ─────────────────────────────────────────────────────
from .mixins import TimestampMixin, SoftDeleteMixin

# ─── Core Models (always present) ───────────────────────────────
from .campaign_goal import CampaignGoal
from .player import Player
from .sponsor import Sponsor
from .team import Team
from .transaction import Transaction

# ─── Optional Models (import if available) ──────────────────────
OPTIONAL_MODELS: List[Tuple[str, str]] = [
    ("example", "Example"),
    ("sms_log", "SMSLog"),
    ("user", "User"),
]

_loaded_optional_models: List[str] = []

for module_name, class_name in OPTIONAL_MODELS:
    try:
        module: ModuleType = __import__(f"app.models.{module_name}", fromlist=[class_name])
        model_cls = getattr(module, class_name)
        globals()[class_name] = model_cls
        _loaded_optional_models.append(class_name)
        logger.debug(f"✅ Loaded optional model: {class_name} from '{module_name}'")
    except (ImportError, AttributeError) as e:
        logger.info(f"ℹ️ Optional model '{class_name}' not loaded: {e}")

# ─── Public API ─────────────────────────────────────────────────
__all__ = [
    "db",
    "TimestampMixin",
    "SoftDeleteMixin",
    "CampaignGoal",
    "Player",
    "Sponsor",
    "Team",
    "Transaction",
    *_loaded_optional_models,  # Inject any that loaded successfully
]

# ─── Utility Helpers ────────────────────────────────────────────
def iter_models() -> List[Any]:
    """
    Return a list of all loaded model classes.
    Useful for:
      - Auto-registering with admin UIs
      - Generating seeds
      - Introspecting for Alembic or API schemas
    """
    return [globals()[name] for name in __all__ if name[0].isupper()]


if TYPE_CHECKING:
    # Type hints for IDEs & static analysis
    from .example import Example  # noqa
    from .sms_log import SMSLog  # noqa
    from .user import User  # noqa

