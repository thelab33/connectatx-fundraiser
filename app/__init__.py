# app/__init__.py
from __future__ import annotations

import json
import logging
import os
import re
import secrets
import time
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Iterable, Type
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request, url_for
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.routing import BuildError

# Core extensions (provided by your app.extensions)
from app.extensions import babel, cors, csrf, db, login_manager, mail, socketio

# Optional extras (tolerant)
try:
    from flask_compress import Compress
except Exception:  # pragma: no cover
    Compress = None
try:
    from flask_talisman import Talisman
except Exception:  # pragma: no cover
    Talisman = None
try:
    from flask_wtf.csrf import generate_csrf
except Exception:  # pragma: no cover
    generate_csrf = None

# Sentry (optional)
try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
except Exception:  # pragma: no cover
    sentry_sdk = None  # type: ignore

# Flask-Migrate
from flask_migrate import Migrate

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

ConfigLike = str | Type[Any]

# ───────────────────────────── Helpers ───────────────────────────── #

def _resolve_config(target: ConfigLike | None) -> ConfigLike:
    """Resolve a config class path or object; allow legacy env fixup."""
    if target is None:
        target = os.getenv("FLASK_CONFIG", "app.config.DevelopmentConfig")
    if isinstance(target, str) and target == "app.config.config.DevelopmentConfig":
        return "app.config.DevelopmentConfig"
    return target


def _json_error(message: str, status: int, **extra: Any):
    return jsonify({"status": "error", "message": message, **extra}), status


def _mtime_or_now(path: Path) -> int:
    try:
        return int(path.stat().st_mtime)
    except Exception:
        return int(datetime.now(timezone.utc).timestamp())


class _RequestIDFilter(logging.Filter):
    """Inject g.request_id into all records as 'request_id'."""
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            rid = getattr(g, "request_id", "-")
        except Exception:
            rid = "-"
        setattr(record, "request_id", rid)
        return True


def _configure_logging(app: Flask) -> None:
    fmt = "%(asctime)s [%(levelname)s] %(name)s [rid=%(request_id)s]: %(message)s"
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt))
        handler.addFilter(_RequestIDFilter())
        root.addHandler(handler)
    else:
        for h in root.handlers:
            h.addFilter(_RequestIDFilter())
            if not isinstance(h.formatter, logging.Formatter) or "%(request_id)s" not in getattr(h.formatter, "_fmt", ""):
                h.setFormatter(logging.Formatter(fmt))
    root.setLevel(app.config.get("LOG_LEVEL", "INFO"))
    logging.getLogger("werkzeug").setLevel(app.config.get("WERKZEUG_LOG_LEVEL", "WARNING"))

    app.logger.info("Loaded config: %s | DEBUG=%s", app.config.get("ENV", "?"), app.debug)
    app.logger.info("DB: %s", app.config.get("SQLALCHEMY_DATABASE_URI", "<unset>"))


def _parse_cors_origins(env: str) -> str | list[str]:
    default_prod = os.getenv("PRIMARY_ORIGIN", "https://connect-atx-elite.com")
    raw = os.getenv("CORS_ORIGINS", "*" if env != "production" else default_prod)
    if isinstance(raw, str) and raw not in {"*", ""} and "," in raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return raw


def _iter_candidates(x: str | Iterable[str]) -> list[str]:
    if isinstance(x, str) and "|" in x:
        return [p.strip() for p in x.split("|") if p.strip()]
    if isinstance(x, str):
        return [x]
    return list(x)


def _safe_register(app: Flask, dotted: str, attr: str | Iterable[str], url_prefix: str | None) -> bool:
    """Import a module and register a blueprint by attribute name(s)."""
    disable = {p.strip().lower() for p in os.getenv("DISABLE_BPS", "").split(",") if p.strip()}
    mod_key = dotted.split(".")[-1].lower()
    if mod_key in disable:
        app.logger.info("⏭️  Disabled module: %s", dotted)
        return False

    try:
        mod = import_module(dotted)
    except Exception as e:
        app.logger.warning("⚠️  Import failed: %s → %s", dotted, e)
        return False

    from flask import Blueprint as _BP  # local to avoid cycles
    wanted = _iter_candidates(attr) + ["bp", "api_bp", "main_bp", "admin_bp"]
    bp = None
    for name in wanted:
        cand = getattr(mod, name, None)
        if cand and isinstance(cand, _BP):
            bp = cand
            break

    if not bp:
        app.logger.warning("⚠️  No blueprint attr found in %s (tried: %s)", dotted, ", ".join(wanted))
        return False

    if bp.name in app.blueprints:
        app.logger.info("⏭️  Already registered: %s", bp.name)
        return False

    try:
        app.register_blueprint(bp, url_prefix=url_prefix or getattr(bp, "url_prefix", None))
        app.logger.info("🧩 Registered: %-20s → %s", bp.name, url_prefix or "/")
        # Ensure shoutouts is available if shipped but not yet registered
        try:
            from app.routes import shoutouts
            if "shoutouts" not in app.blueprints:
                app.register_blueprint(shoutouts.bp)
        except Exception:
            pass
        return True
    except Exception as exc:
        app.logger.error("❌ Failed to register %s:%s: %s", dotted, bp.name, exc, exc_info=True)
        return False


# Regex for optional auto-nonce injection on stray tags
_SCRIPT_TAG = re.compile(r"(<script\b(?![^>]*\bnonce=)[^>]*>)", re.IGNORECASE)
_STYLE_TAG  = re.compile(r"(<style\b(?![^>]*\bnonce=)[^>]*>)", re.IGNORECASE)

# ───────────── Static URL helper (Jinja globals) ───────────── #

try:
    from flask import url_for as _url_for  # noqa: N812
except Exception:  # pragma: no cover
    _url_for = None  # type: ignore

def static_url(path: str) -> str:
    """Return a /static path; works with or without Flask's url_for."""
    p = (path or "").strip()
    if not p:
        return "/static/"
    if "://" in p or p.startswith("//"):
        return p
    try:
        if _url_for is not None:
            return _url_for("static", filename=p.lstrip("/"))
    except Exception:
        pass
    return f"/static/{p.lstrip('/')}"

# ───────────── Asset manifest (SRI + version) → Jinja globals ───────────── #

def _load_asset_manifest(app: Flask) -> None:
    """
    Reads app/static/asset-manifest.json.
    Expected shape:
      {
        "assets": { "js/bundle.min.js": {"sri":{"sha384":"..."}}, ... },
        "sri":    { "css/app.min.css": "sha384-..." },
        "version": { "git":"abcd", "builtAt":"2025-02-09T..." }
      }
    """
    try:
        p = Path(app.root_path) / "static" / "asset-manifest.json"
        if not p.exists():
            return
        data = json.loads(p.read_text())
        sri_map = data.get("sri") or {
            k: v.get("sri", {}).get("sha384")
            for k, v in (data.get("assets") or {}).items()
            if v.get("sri", {}).get("sha384")
        }
        app.jinja_env.globals["SRI"] = sri_map or {}
        app.jinja_env.globals["ASSET_VER"] = (
            data.get("version", {}).get("git")
            or data.get("version", {}).get("builtAt")
            or ""
        )
    except Exception as e:
        app.logger.warning("Asset manifest load failed: %s", e)


# ───────────────────────────── App Factory ───────────────────────────── #

def create_app(config_class: ConfigLike | None = None) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(BASE_DIR / "app/static"),
        template_folder=str(BASE_DIR / "app/templates"),
    )

    # Jinja helpers (keep simple + CSP-safe)
    app.jinja_env.globals.setdefault("static_url", static_url)
    app.jinja_env.globals.setdefault("asset_url", static_url)

    # Config
    cfg = _resolve_config(config_class)
    try:
        app.config.from_object(cfg)
    except Exception as exc:
        fallback = "app.config.DevelopmentConfig"
        if isinstance(cfg, str) and cfg != fallback:
            app.config.from_object(fallback)
        else:
            raise RuntimeError(f"❌ Invalid FLASK_CONFIG '{cfg}': {exc}") from exc

    # Sensible defaults
    app.url_map.strict_slashes = False
    app.config.setdefault("JSON_SORT_KEYS", False)
    app.config.setdefault("JSON_AS_ASCII", False)
    app.config.setdefault("PROPAGATE_EXCEPTIONS", False)
    app.config.setdefault("AUTO_NONCE_HTML", True)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SECURE", app.config.get("ENV") == "production")

    _configure_logging(app)

    # Sentry
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if dsn and sentry_sdk:
        try:
            sentry_sdk.init(
                dsn=dsn,
                integrations=[
                    FlaskIntegration(),
                    LoggingIntegration(level=logging.INFO, event_level=logging.ERROR),
                    SqlalchemyIntegration(),
                ],
                traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
                profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.0")),
                send_default_pii=False,
                environment=app.config.get("ENV", "development"),
                release=os.getenv("GIT_COMMIT"),
            )
            app.logger.info("🪶 Sentry initialized")
        except Exception as e:
            app.logger.warning("Sentry init failed: %s", e)

    # CORS
    cors_origins = _parse_cors_origins(app.config.get("ENV", "development"))
    if cors:
        cors.init_app(
            app,
            supports_credentials=True,
            resources={r"/api/*": {"origins": cors_origins}},
            expose_headers=["X-Request-ID"],
            allow_headers=["Content-Type", "Authorization"],
            methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        )

    # Security headers / CSP (Talisman optional; we also set headers manually below)
    if app.config.get("ENV") == "production" and Talisman:
        Talisman(app, content_security_policy=None)

    # Extensions
    if csrf:
        csrf.init_app(app)
    db.init_app(app)
    # DEV convenience: auto-create tables when using SQLite
    if app.config.get("SQLALCHEMY_DATABASE_URI", "").startswith("sqlite"):
        try:
            with app.app_context():
                from app.extensions import db as _db
                _db.create_all()
        except Exception:
            pass  # non-fatal for prod
    Migrate(app, db, compare_type=True, render_as_batch=True)

    # Socket.IO (exposed on app for convenience)
    app.socketio = socketio
    socketio.init_app(app, cors_allowed_origins=cors_origins if cors_origins else "*")

    # Mail + compression
    mail.init_app(app)
    if Compress:
        Compress(app)

    # CLI (optional)
    try:
        from app.cli.db_tools import dbcli
        app.cli.add_command(dbcli)
    except Exception as e:
        app.logger.warning("⚠️ dbcli not available: %s", e)

    # Per-request bootstrap (nonce, request id, timing)
    @app.before_request
    def _gen_nonce():
        g.csp_nonce = secrets.token_urlsafe(16)
        g.request_id = request.headers.get("X-Request-ID", uuid4().hex)
        g._start_ts = time.perf_counter()
        # Sentry tagging
        try:
            if sentry_sdk:
                with sentry_sdk.configure_scope() as scope:
                    scope.set_tag("request_id", g.request_id)
                    scope.set_tag("endpoint", request.endpoint or "")
                    scope.set_user({"ip_address": (request.access_route[0] if request.access_route else request.remote_addr)})
        except Exception:
            pass

    # Jinja: nonce shortcut + manifest (SRI/ASSET_VER)
    @app.context_processor
    def inject_csp_and_manifest():
        return {"csp_nonce": lambda: getattr(g, "csp_nonce", ""), "NONCE": getattr(g, "csp_nonce", "")}

    _load_asset_manifest(app)

    # Security headers (CSP + others)
    @app.after_request
    def _std_headers(resp):
        nonce = getattr(g, "csp_nonce", "")

        stripe_js = "https://js.stripe.com"
        stripe_api = "https://api.stripe.com"
        paypal_core = "https://www.paypal.com"
        paypal_all = "https://*.paypal.com"
        paypal_api_live = "https://api-m.paypal.com"
        paypal_api_sbx = "https://api-m.sandbox.paypal.com"
        socketio_cdn = "https://cdn.socket.io"

        csp = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}' 'strict-dynamic' {stripe_js} {paypal_core} {paypal_all} {socketio_cdn}; "
            f"connect-src 'self' {stripe_api} {paypal_api_live} {paypal_api_sbx} wss:; "
            "img-src 'self' data: blob: https:; "
            f"style-src 'self' 'nonce-{nonce}' 'unsafe-inline'; "
            "font-src 'self' https: data:; "
            f"frame-src 'self' {stripe_js} https://checkout.stripe.com {paypal_core} {paypal_all}; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "object-src 'none'; "
            "form-action 'self' https://checkout.stripe.com https://www.paypal.com;"
        )
        resp.headers.setdefault("Content-Security-Policy", csp)
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Permissions-Policy", "camera=(), geolocation=(), microphone=(), payment=()")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Request-ID", g.request_id)

        # HSTS
        if request.is_secure or app.config.get("PREFERRED_URL_SCHEME") == "https":
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")

        # Server-Timing
        try:
            dur_ms = (time.perf_counter() - g._start_ts) * 1000.0
            resp.headers.setdefault("Server-Timing", f"app;dur={dur_ms:.1f}")
        except Exception:
            pass

        # Optional: auto-inject nonce into stray <script>/<style> in HTML bodies
        try:
            if app.config.get("AUTO_NONCE_HTML", True) and nonce and resp.mimetype == "text/html" and not resp.direct_passthrough:
                text = resp.get_data(as_text=True)
                if "<script" in text or "<style" in text:
                    def _add_nonce(m):
                        tag = m.group(1)
                        return tag[:-1] + f' nonce="{nonce}">'
                    text = _SCRIPT_TAG.sub(_add_nonce, text)
                    text = _STYLE_TAG.sub(_add_nonce, text)
                    resp.set_data(text)
        except Exception:
            pass

        return resp

    # Login
    if login_manager:
        login_manager.init_app(app)
        login_manager.login_view = "main.home"
        try:
            from app.models.user import User  # optional
        except Exception:
            User = None  # type: ignore

        @login_manager.user_loader
        def load_user(uid: str):
            return User.query.get(int(uid)) if User else None

    if babel:
        babel.init_app(app)

    # Base context (never breaks templates)
    @app.context_processor
    def _base_ctx():
        def has_endpoint(name: str) -> bool:
            return name in app.view_functions

        def safe_url_for(endpoint: str, **values: Any) -> str:
            try:
                return url_for(endpoint, **values)
            except (BuildError, Exception):
                return ""

        # If manifest provided ASSET_VER, prefer it; else mtime fallback
        static_root = Path(app.static_folder)
        css = static_root / "css" / "app.min.css"
        js  = static_root / "js"  / "bundle.min.js"
        asset_ver = app.jinja_env.globals.get("ASSET_VER") or str(max(_mtime_or_now(css), _mtime_or_now(js)))

        class _Obj(dict):
            __getattr__ = dict.get

        team_default = _Obj(team_name="Connect ATX Elite", theme_color="#facc15")
        return {
            "app_env": app.config.get("ENV"),
            "app_config": app.config,
            "now": lambda: datetime.now(timezone.utc),
            "has_endpoint": has_endpoint,
            "safe_url_for": safe_url_for,
            "ASSET_VER": asset_ver,
            "SRI": app.jinja_env.globals.get("SRI", {}),
            "team": team_default,  # override in views as needed
        }

    # JSON errors (API-friendly)
    def _wants_json() -> bool:
        accept = (request.headers.get("Accept") or "").lower()
        return "application/json" in accept or request.path.startswith("/api") or request.is_json

    @app.errorhandler(HTTPException)
    def _http_err(err):
        return (_json_error(err.description or err.name, err.code, request_id=g.request_id) if _wants_json() else err)

    @app.errorhandler(Exception)
    def _uncaught(err):
        app.logger.exception("Unhandled error: %s", err)
        return (_json_error("Internal Server Error", 500, request_id=g.request_id) if _wants_json() else InternalServerError())

    # Blueprints (schema-safe auto-registration)
    blueprints = [
        ("app.routes.main",           "main_bp|bp", "/"),
        ("app.routes.api",            "bp|api_bp",  "/api"),
        ("app.admin.routes",          "bp|admin_bp","/admin"),
        ("app.blueprints.fc_payments","bp",         "/payments"),
        ("app.blueprints.fc_metrics", "bp",         "/metrics"),
        ("app.routes.newsletter",     "bp",         "/newsletter"),
        ("app.routes.sms",            "sms_bp|bp",  "/sms"),   # ✅ keeps SMS
    ]
    for dotted, attr, prefix in blueprints:
        _safe_register(app, dotted, attr, prefix)

    # Health & Version
    @app.get("/healthz")
    def _healthz():
        return {"status": "ok", "message": "FundChamps Flask live!", "request_id": g.request_id}

    @app.get("/version")
    def _version():
        return {"version": os.getenv("GIT_COMMIT", "dev"), "env": app.config.get("ENV")}

    # CSRF cookie (if flask-wtf installed)
    if csrf and generate_csrf:
        @app.after_request
        def inject_csrf_cookie(resp):
            try:
                resp.set_cookie(
                    "csrf_token",
                    generate_csrf(),
                    samesite="Lax",
                    secure=(app.config.get("ENV") == "production"),
                )
            except Exception:
                pass
            return resp

    # Launch banner
    stripe_ok = bool(os.getenv("STRIPE_SECRET_KEY"))
    paypal_ok = bool(os.getenv("PAYPAL_CLIENT_ID") and os.getenv("PAYPAL_SECRET"))
    print(
        "┌────────────────────────────────────────────┐\n"
        "│  🌟 FundChamps Flask: Ready to Launch       │\n"
        f"│  ENV = {app.config.get('ENV','unknown'):<12}   DEBUG = {str(app.debug):<5}   │\n"
        f"│  Stripe={'ON ' if stripe_ok else 'OFF'}  PayPal={'ON ' if paypal_ok else 'OFF'}          │\n"
        f"│  Blueprints: {len(app.blueprints):<3}                         │\n"
        "└────────────────────────────────────────────┘"
    )
    return app

