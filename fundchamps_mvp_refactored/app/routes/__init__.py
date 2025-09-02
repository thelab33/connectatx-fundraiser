from __future__ import annotations

"""
FundChamps / Starforge — Blueprint Loader
- Safely loads & registers blueprints with env-based overrides
- Falls back to a working homepage if 'main' blueprint is missing
"""

import logging
import os
from dataclasses import dataclass
from importlib import import_module
from typing import Optional

from flask import Blueprint, Flask

# ─── Optional CLI Group ──────────────────────────────────────────────────────
try:
    from app.cli import starforge  # type: ignore
except Exception:
    starforge = None  # type: ignore

log = logging.getLogger(__name__)


# ─── Blueprint Spec Definition ──────────────────────────────────────────────
@dataclass(frozen=True)
class BlueprintSpec:
    alias: str  # Short name used in env controls/logs
    module: str  # Dotted import path
    attr: str  # Attribute name of Blueprint in module
    prefix: Optional[str]  # Default URL prefix (None = root)


# ─── Helpers ────────────────────────────────────────────────────────────────
def _env_prefix_override(alias: str, default: Optional[str]) -> Optional[str]:
    """Allow URL prefix override via env: BP_PREFIX__API=/v2"""
    return os.getenv(f"BP_PREFIX__{alias.upper()}", default)


def _import_bp(spec: BlueprintSpec) -> Optional[Blueprint]:
    """Import a Blueprint; return None if fails or attr not a Blueprint."""
    try:
        mod = import_module(spec.module)
        bp = getattr(mod, spec.attr, None)
        if not isinstance(bp, Blueprint):
            log.warning(
                "Module '%s' loaded but '%s' is not a Blueprint (got %r)",
                spec.module,
                spec.attr,
                type(bp).__name__ if bp else None,
            )
            return None
        return bp
    except Exception as exc:
        log.warning("⏭️  Could not import %s.%s: %s", spec.module, spec.attr, exc)
        return None


def _parse_disabled_env(env_value: Optional[str]) -> set[str]:
    """Parse DISABLE_BPS into a set of aliases."""
    return (
        {p.strip().lower() for p in env_value.split(",") if p.strip()}
        if env_value
        else set()
    )


def _safe_register(
    app: Flask, *, alias: str, bp: Blueprint, prefix: Optional[str]
) -> bool:
    """Register a blueprint unless disabled/already present."""
    if alias in getattr(app, "_fc_disabled_bps", set()):
        app.logger.info("⏭️  Disabled via env: %s", alias)
        return False
    if bp.name in app.blueprints:
        app.logger.info("⏭️  Already registered: %s", bp.name)
        return False

    url_prefix = (
        None
        if alias == "main"
        else _env_prefix_override(alias, bp.url_prefix or prefix)
    )
    try:
        app.register_blueprint(bp, url_prefix=url_prefix)
        app.logger.info("🧩 Registered blueprint: %-10s → %s", alias, url_prefix or "/")
        return True
    except Exception as exc:
        app.logger.error("⚠️  Failed to register '%s': %s", alias, exc, exc_info=True)
        return False


def _route_summary(app: Flask) -> None:
    """Log all routes when DEBUG is enabled."""
    if not app.debug:
        return
    try:
        bps = ", ".join(sorted(app.blueprints.keys())) or "—"
        app.logger.info("📦 Blueprints: %s", bps)
        lines = []
        for rule in sorted(
            app.url_map.iter_rules(), key=lambda r: (str(r.rule), r.endpoint)
        ):
            methods = ",".join(
                sorted(
                    m
                    for m in rule.methods
                    if m in {"GET", "POST", "PUT", "PATCH", "DELETE"}
                )
            )
            lines.append(f"{rule.rule:<40} {methods:<12} → {rule.endpoint}")
        if lines:
            app.logger.info("🔗 Routes:\n%s", "\n".join(lines))
    except Exception:
        app.logger.debug("Could not render route summary", exc_info=True)


# ─── Fallback Blueprint ─────────────────────────────────────────────────────
fallback_bp = Blueprint("fallback", __name__)


@fallback_bp.get("/")
def _default_root() -> str:
    return (
        "✅ FundChamps backend is running.<br>"
        "<strong>Main homepage not registered.</strong>"
    )


# ─── Public API ─────────────────────────────────────────────────────────────
def register_blueprints(app: Flask) -> None:
    """
    Register CLI commands & blueprints with env overrides.
    Env:
      DISABLE_BPS=api,sms
      BP_PREFIX__API=/v2
    """
    # Cache disabled aliases
    app._fc_disabled_bps = _parse_disabled_env(os.getenv("DISABLE_BPS"))

    # CLI group
    if starforge:
        try:
            app.cli.add_command(starforge)
            app.logger.info("🛠️  Registered CLI group: starforge")
        except Exception as exc:
            app.logger.warning("⚠️  Could not register CLI group 'starforge': %s", exc)

    specs: list[BlueprintSpec] = [
        BlueprintSpec("main", "app.routes.main", "main_bp", None),
        BlueprintSpec("api", "app.routes.api", "api_bp", "/api"),
        BlueprintSpec("sms", "app.routes.sms", "sms_bp", "/sms"),
        BlueprintSpec("stripe", "app.routes.stripe_routes", "stripe_bp", "/stripe"),
        BlueprintSpec("webhooks", "app.routes.webhooks", "webhook_bp", "/webhooks"),
        BlueprintSpec("donations", "app.routes.donations", "bp", "/donations"),
        BlueprintSpec("donations", "app.blueprints.donations", "bp", "/donations"),
    ]

    found_main = False
    for spec in specs:
        bp = _import_bp(spec)
        if not bp:
            continue
        if (
            _safe_register(app, alias=spec.alias, bp=bp, prefix=spec.prefix)
            and spec.alias == "main"
        ):
            found_main = True

    if not found_main and "fallback" not in app._fc_disabled_bps:
        _safe_register(app, alias="fallback", bp=fallback_bp, prefix=None)

    _route_summary(app)
    app.logger.info("✅ Blueprint registration complete.")
