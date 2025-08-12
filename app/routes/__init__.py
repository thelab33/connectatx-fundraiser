# app/boot/blueprints.py
from __future__ import annotations

import os
import logging
from dataclasses import dataclass
from importlib import import_module
from typing import Optional, Iterable, Mapping, Dict

from flask import Blueprint, Flask

# Optional CLI group import (fail silently)
try:  # pragma: no cover
    from app.cli import starforge  # type: ignore
except Exception:  # pragma: no cover
    starforge = None  # type: ignore

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class BlueprintSpec:
    """
    Declarative blueprint spec.

    alias: short name used in DISABLE_BPS and logs (e.g., "main", "api").
    module: dotted import path to the module that exposes the attribute.
    attr: attribute name inside the module (the Blueprint instance).
    prefix: desired url_prefix when registering; None = no prefix.
    """
    alias: str
    module: str
    attr: str
    prefix: Optional[str]


def _import_bp(spec: BlueprintSpec) -> Optional[Blueprint]:
    """
    Attempt to import a Blueprint by module and attribute name.
    Returns None if anything goes wrong.
    """
    try:
        mod = import_module(spec.module)
        bp = getattr(mod, spec.attr, None)
        if not isinstance(bp, Blueprint):
            log.warning("Module '%s' loaded but attribute '%s' is not a Blueprint (got %r)",
                        spec.module, spec.attr, type(bp).__name__ if bp is not None else None)
            return None
        return bp
    except Exception:
        # Keep imports resilient; we'll log at INFO and continue gracefully.
        log.info("⏭️  Could not import %s.%s; skipping.", spec.module, spec.attr, exc_info=False)
        return None


def _parse_disabled_env(env_value: Optional[str]) -> set[str]:
    """
    Parse DISABLE_BPS into a normalized set of aliases.
    Example: DISABLE_BPS="api, sms" -> {"api","sms"}.
    """
    if not env_value:
        return set()
    return {part.strip().lower() for part in env_value.split(",") if part.strip()}


def _safe_register(app: Flask, *, alias: str, bp: Blueprint, prefix: Optional[str]) -> bool:
    """
    Register a blueprint if not disabled or already present.
    Returns True if registered, False if skipped.
    """
    disabled = getattr(app, "_fc_disabled_bps", set())  # cached on app
    if alias in disabled:
        app.logger.info("⏭️  Disabled via env: %s", alias)
        return False

    # Already registered?
    if bp.name in app.blueprints:
        app.logger.info("⏭️  Already registered: %s", bp.name)
        return False

    # For "main" we prefer no prefix (root), to avoid accidental '//' URLs.
    url_prefix = None if alias == "main" else (getattr(bp, "url_prefix", None) or prefix)

    try:
        app.register_blueprint(bp, url_prefix=url_prefix)
        app.logger.info("🧩 Registered blueprint: %-10s → %s", alias, url_prefix or "/")
        return True
    except Exception as exc:
        app.logger.warning("⚠️  Failed to register '%s': %s", alias, exc, exc_info=True)
        return False


def _route_summary(app: Flask) -> None:
    """Log a concise route map when DEBUG is on."""
    if not app.debug:
        return
    try:
        bps = ", ".join(sorted(app.blueprints.keys())) or "—"
        app.logger.info("📦 Blueprints: %s", bps)

        lines: list[str] = []
        for rule in sorted(app.url_map.iter_rules(),
                           key=lambda r: (str(r.rule), r.endpoint)):
            methods = ",".join(sorted(
                m for m in rule.methods
                if m in {"GET", "POST", "PUT", "PATCH", "DELETE"}
            ))
            lines.append(f"  {rule.rule:<35} {methods:<18} → {rule.endpoint}")

        if lines:
            app.logger.info("🔗 Routes:\n%s", "\n".join(lines))
    except Exception:
        app.logger.debug("Could not render route summary", exc_info=True)


# Fallback blueprint if "main" is missing
fallback_bp = Blueprint("fallback", __name__)

@fallback_bp.get("/")
def _default_root() -> str:
    return "✅ FundChamps backend is running. (No main homepage registered yet.)"


def register_blueprints(app: Flask) -> None:
    """
    Register CLI commands and available blueprints safely.

    Env controls:
      DISABLE_BPS=api,sms       # comma-separated aliases to skip

    Known aliases: main, api, sms, stripe, webhooks, fallback
    """
    # Cache disabled aliases on the app for quick checks
    app._fc_disabled_bps = _parse_disabled_env(os.getenv("DISABLE_BPS"))  # type: ignore[attr-defined]

    # Optional CLI registration
    if starforge:
        try:
            app.cli.add_command(starforge)
            app.logger.info("🛠️  Registered CLI group: starforge")
        except Exception as exc:
            app.logger.warning("⚠️  Could not register CLI group 'starforge': %s", exc)

    # Declarative blueprint registry
    specs: list[BlueprintSpec] = [
        BlueprintSpec(alias="main",     module="app.routes.main",          attr="main_bp",     prefix=None),
        BlueprintSpec(alias="api",      module="app.routes.api",           attr="api_bp",      prefix="/api"),
        BlueprintSpec(alias="sms",      module="app.routes.sms",           attr="sms_bp",      prefix="/sms"),
        BlueprintSpec(alias="stripe",   module="app.routes.stripe_routes", attr="stripe_bp",   prefix="/stripe"),
        BlueprintSpec(alias="webhooks", module="app.routes.webhooks",      attr="webhook_bp",  prefix="/webhooks"),
    ]

    registered_any = False
    found_main = False

    for spec in specs:
        bp = _import_bp(spec)
        if bp is None:
            app.logger.info("⏭️  %s not found; skipping.", spec.alias)
            continue
        ok = _safe_register(app, alias=spec.alias, bp=bp, prefix=spec.prefix)
        registered_any = registered_any or ok
        if spec.alias == "main" and ok:
            found_main = True

    # Ensure fallback if no main blueprint is registered
    if not found_main and "fallback" not in app._fc_disabled_bps:  # type: ignore[attr-defined]
        _safe_register(app, alias="fallback", bp=fallback_bp, prefix=None)

    _route_summary(app)
    app.logger.info("✅ Blueprints & CLI registration complete.")

