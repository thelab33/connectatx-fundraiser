from __future__ import annotations

"""
FundChamps / Starforge — Blueprint Loader (hardened)
- Safely loads & registers blueprints with env-based overrides
- Multiple attr fallbacks (bp|api_bp|main_bp|admin_bp|custom)
- Prefix overrides via env (BP_PREFIX__ALIAS=/v2), with sanitizer
- DISABLE_BPS=api,sms,fallback
- Optional route summary in DEBUG or ROUTE_SUMMARY=1
- Fallback homepage if 'main' blueprint is missing
"""

import logging
import os
from dataclasses import dataclass
from importlib import import_module
from typing import Iterable, Optional

from flask import Blueprint, Flask

# ─── Optional CLI Group ──────────────────────────────────────────────────────
try:
    from app.cli import starforge  # type: ignore
except Exception:  # pragma: no cover
    starforge = None  # type: ignore

log = logging.getLogger(__name__)


# ─── Blueprint Spec Definition ──────────────────────────────────────────────
@dataclass(frozen=True)
class BlueprintSpec:
    alias: str            # Short name used in env controls/logs
    module: str           # Dotted import path
    attrs: tuple[str, ...]  # Attribute name(s) of Blueprint in module
    prefix: Optional[str]   # Default URL prefix (None = root)


# ─── Helpers ────────────────────────────────────────────────────────────────
def _env_prefix_override(alias: str, default: Optional[str]) -> Optional[str]:
    """Allow URL prefix override via env: BP_PREFIX__API=/v2"""
    return os.getenv(f"BP_PREFIX__{alias.upper()}", default)


def _sanitize_prefix(prefix: Optional[str]) -> Optional[str]:
    """Normalize URL prefixes: ensure leading '/', collapse dup slashes, allow None."""
    if prefix is None or prefix == "":
        return None
    p = prefix.strip()
    if p == "/":
        return None  # treat bare slash as root
    if not p.startswith("/"):
        p = "/" + p
    # collapse duplicates like //v1//x → /v1/x
    while "//" in p:
        p = p.replace("//", "/")
    return p.rstrip("/") or None


def _iter_candidates(attrs: Iterable[str] | str) -> list[str]:
    if isinstance(attrs, str):
        return [a.strip() for a in attrs.split("|") if a.strip()]
    return [a for a in attrs if a]


def _import_bp(module: str, attrs: Iterable[str]) -> Optional[Blueprint]:
    """Import a Blueprint; return None if import fails or attr not a Blueprint."""
    try:
        mod = import_module(module)
    except Exception as exc:
        log.warning("⏭️  Import failed: %s (%s)", module, exc)
        return None

    for name in _iter_candidates(attrs):
        try:
            cand = getattr(mod, name, None)
            if isinstance(cand, Blueprint):
                return cand
        except Exception:
            continue

    log.warning("Module '%s' loaded but none of %s is a Blueprint", module, list(attrs))
    return None


def _parse_disabled_env(env_value: Optional[str]) -> set[str]:
    """Parse DISABLE_BPS into a set of aliases."""
    return {p.strip().lower() for p in (env_value or "").split(",") if p.strip()}


def _safe_register(app: Flask, *, alias: str, bp: Blueprint, prefix: Optional[str]) -> bool:
    """Register a blueprint unless disabled/already present."""
    alias_lc = alias.lower()
    disabled = getattr(app, "_fc_disabled_bps", set())
    if alias_lc in disabled:
        app.logger.info("⏭️  Disabled via env: %s", alias_lc)
        return False
    if bp.name in app.blueprints:
        app.logger.info("⏭️  Already registered: %s", bp.name)
        return False
    # Compute final prefix (env override wins)
    final_prefix = _sanitize_prefix(_env_prefix_override(alias_lc, bp.url_prefix or prefix))
    try:
        app.register_blueprint(bp, url_prefix=final_prefix)
        app.logger.info("🧩 Registered blueprint: %-10s → %s", alias, final_prefix or "/")
        return True
    except Exception as exc:  # pragma: no cover
        app.logger.error("❌ Failed to register '%s': %s", alias, exc, exc_info=True)
        return False


def _route_summary(app: Flask) -> None:
    """Log an overview of routes (debug aid)."""
    want = app.debug or os.getenv("ROUTE_SUMMARY", "0") in {"1", "true", "yes"}
    if not want:
        return
    try:
        bps = ", ".join(sorted(app.blueprints.keys())) or "—"
        app.logger.info("📦 Blueprints: %s", bps)
        lines = []
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: (str(r.rule), r.endpoint)):
            methods = ",".join(sorted(m for m in rule.methods if m in {"GET", "POST", "PUT", "PATCH", "DELETE"}))
            lines.append(f"{rule.rule:<42} {methods:<12} → {rule.endpoint}")
        if lines:
            app.logger.info("🔗 Routes:\n%s", "\n".join(lines))
    except Exception:  # pragma: no cover
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
      DISABLE_BPS=api,sms,fallback
      BP_PREFIX__API=/v2
      ROUTE_SUMMARY=1
    """
    # Cache disabled aliases on the app (used by _safe_register)
    app._fc_disabled_bps = _parse_disabled_env(os.getenv("DISABLE_BPS"))

    # CLI group
    if starforge:
        try:
            app.cli.add_command(starforge)
            app.logger.info("🛠️  Registered CLI group: starforge")
        except Exception as exc:  # pragma: no cover
            app.logger.warning("⚠️  Could not register CLI group 'starforge': %s", exc)

    # Specs: order matters (closest to core first). Provide multiple attr fallbacks.
    specs: list[BlueprintSpec] = [
        BlueprintSpec("main",       "app.routes.main",            ("main_bp", "bp"),                         None),
        BlueprintSpec("api",        "app.routes.api",             ("api_bp", "bp"),                          "/api"),
        BlueprintSpec("sms",        "app.routes.sms",             ("sms_bp", "bp"),                          "/sms"),
        BlueprintSpec("stripe",     "app.routes.stripe_routes",   ("stripe_bp", "bp"),                       "/stripe"),
        BlueprintSpec("webhooks",   "app.routes.webhooks",        ("webhook_bp", "bp"),                      "/webhooks"),
        # Donations: try new package first, then legacy location
        BlueprintSpec("donations",  "app.blueprints.donations",   ("bp", "donations_bp"),                    "/donations"),
        BlueprintSpec("donations",  "app.routes.donations",       ("bp", "donations_bp"),                    "/donations"),
    ]

    registered_aliases: set[str] = set()
    found_main = False

    for spec in specs:
        # Prevent registering the same alias twice if an earlier spec succeeded
        if spec.alias.lower() in registered_aliases:
            continue

        bp = _import_bp(spec.module, spec.attrs)
        if not bp:
            continue

        if _safe_register(app, alias=spec.alias, bp=bp, prefix=spec.prefix):
            registered_aliases.add(spec.alias.lower())
            if spec.alias == "main":
                found_main = True

    # Fallback if 'main' not present (unless explicitly disabled)
    if not found_main and "fallback" not in getattr(app, "_fc_disabled_bps", set()):
        _safe_register(app, alias="fallback", bp=fallback_bp, prefix=None)

    _route_summary(app)
    app.logger.info("✅ Blueprint registration complete. (%d total)", len(app.blueprints))

