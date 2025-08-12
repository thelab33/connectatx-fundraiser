# app/__init__.py
from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Optional, Type
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request, url_for
from flask_cors import CORS
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.routing import BuildError

# ── env & paths ──────────────────────────────────────────────────────────────
load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# Core extensions (singletons)
from app.extensions import db, migrate, socketio, mail, csrf  # noqa: E402

# Optional deps (kept lazy/guarded)
USE_LOGIN = USE_BABEL = USE_CLI = False
try:
    from flask_login import LoginManager  # type: ignore
    login_manager: Optional[LoginManager] = LoginManager()
    USE_LOGIN = True
except ImportError:  # pragma: no cover
    login_manager = None  # type: ignore

try:
    from flask_babel import Babel, _ as _t  # type: ignore
    USE_BABEL = True
except ImportError:  # pragma: no cover
    Babel = None  # type: ignore

    def _t(s: str) -> str:
        return s

try:
    from app.cli import starforge  # type: ignore
    USE_CLI = True
except ImportError:  # pragma: no cover
    starforge = None  # type: ignore

# Optional gzip (if installed)
try:
    from flask_compress import Compress  # type: ignore
except ImportError:  # pragma: no cover
    Compress = None  # type: ignore


# ── helpers ──────────────────────────────────────────────────────────────────
ConfigLike = str | Type[Any]


def _resolve_config(target: ConfigLike | None) -> ConfigLike:
    """Accept dotted path or class; preserve legacy dotted path once."""
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


def _configure_logging(app: Flask) -> None:
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=app.config.get("LOG_LEVEL", "INFO"),
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )
    logging.getLogger("werkzeug").setLevel(app.config.get("WERKZEUG_LOG_LEVEL", "WARNING"))
    app.logger.info("Loaded configuration: %s | DEBUG=%s", app.config.get("ENV", "?"), app.debug)
    app.logger.info("DB: %s", app.config.get("SQLALCHEMY_DATABASE_URI", "<unset>"))


def _parse_cors_origins(env: str) -> str | list[str]:
    """Support CORS_ORIGINS env as '*' or comma list; default safe prod origin."""
    default_prod = os.getenv("PRIMARY_ORIGIN", "https://connect-atx-elite.com")
    raw = os.getenv("CORS_ORIGINS", "*" if env != "production" else default_prod)
    if isinstance(raw, str) and raw not in {"*", ""} and "," in raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    return raw


# ── blueprint import helpers (robust, de-duped) ─────────────────────────────
def _import_bp(dotted: str, attr: str):
    """Import a blueprint by module path + attribute name, or return None."""
    try:
        mod = import_module(dotted)
        return getattr(mod, attr, None)
    except Exception:
        return None


def _safe_register(app: Flask, dotted: str, attr: str, url_prefix: str | None) -> bool:
    """Register a blueprint if available and not disabled."""
    disable = {p.strip().lower() for p in os.getenv("DISABLE_BPS", "").split(",") if p.strip()}
    key = f"{dotted}:{attr}".lower()
    if dotted.split(".")[-1] in disable or key in disable:
        app.logger.info("⏭️  Disabled via env: %s", dotted)
        return False

    bp = _import_bp(dotted, attr)
    if not bp:
        app.logger.info("⏭️  %s not found; skipping.", dotted)
        return False

    name = getattr(bp, "name", attr)
    if name in app.blueprints:
        app.logger.info("⏭️  Already registered: %s", name)
        return False

    prefix = url_prefix if url_prefix is not None else getattr(bp, "url_prefix", None)
    try:
        app.register_blueprint(bp, url_prefix=prefix)
        app.logger.info("🧩 Registered blueprint: %-24s → %s", f"{dotted}.{attr}", prefix or "/")
        # API error handlers hook (optional)
        for candidate in ("register_error_handlers", "register_errors"):
            try:
                fn = getattr(import_module(dotted), candidate, None)
                if callable(fn):
                    fn(app)
            except Exception:
                app.logger.debug("Error handlers in %s failed", dotted, exc_info=True)
        return True
    except Exception as exc:
        app.logger.warning("⚠️  Failed to register %s: %s", dotted, exc, exc_info=True)
        return False


# ── app factory ──────────────────────────────────────────────────────────────
def create_app(config_class: ConfigLike | None = None) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(BASE_DIR / "app/static"),
        template_folder=str(BASE_DIR / "app/templates"),
    )

    # 1) Config
    cfg = _resolve_config(config_class)
    try:
        app.config.from_object(cfg)
    except Exception as exc:
        legacy = "app.config.config.DevelopmentConfig"
        if isinstance(cfg, str) and cfg != legacy:
            try:
                app.config.from_object(legacy)
            except Exception:
                raise RuntimeError(f"❌ Invalid FLASK_CONFIG '{cfg}': {exc}") from exc
        else:
            raise RuntimeError(f"❌ Invalid FLASK_CONFIG '{cfg}': {exc}") from exc

    # Sensible JSON defaults
    app.config.setdefault("JSON_SORT_KEYS", False)
    app.config.setdefault("JSONIFY_PRETTYPRINT_REGULAR", False)

    # 2) Logging
    _configure_logging(app)

    # 3) CORS (lock to API paths; allow auth header + expose request id)
    cors_origins = _parse_cors_origins(app.config.get("ENV", "development"))
    CORS(
        app,
        supports_credentials=True,
        resources={r"/api/*": {"origins": cors_origins}},
        expose_headers=["X-Request-ID"],
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # 4) Optional security headers (CSP via Talisman in prod if present)
    if app.config.get("ENV") == "production":
        try:
            from flask_talisman import Talisman  # type: ignore
            Talisman(app, content_security_policy=None)
        except ImportError:
            app.logger.warning("⚠️ flask-talisman not installed – skipping CSP setup")

    # 5) CSRF (initialize globally; JSON API is exempted inside its module)
    if csrf:
        csrf.init_app(app)

    # 6) Core extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins=cors_origins)
    mail.init_app(app)
    if Compress:
        try:
            Compress(app)
            app.logger.info("🗜️  Compression enabled")
        except Exception:
            app.logger.debug("Compress init failed", exc_info=True)

    # 7) Request meta + headers
    @app.before_request
    def _req_meta() -> None:
        g.request_id = request.headers.get("X-Request-ID", uuid4().hex)
        g._start_ts = time.perf_counter()

    @app.after_request
    def _std_headers(resp):
        resp.headers.setdefault("X-Request-ID", getattr(g, "request_id", uuid4().hex))
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        try:
            dur_ms = (time.perf_counter() - g._start_ts) * 1000.0
            resp.headers.setdefault("Server-Timing", f"app;dur={dur_ms:.1f}")
        except Exception:
            pass
        return resp

    # 8) Optional: Login
    if USE_LOGIN and login_manager:
        login_manager.init_app(app)
        login_manager.login_view = "admin.dashboard"
        try:
            from app.models.user import User  # type: ignore
        except Exception as exc:
            User = None  # type: ignore
            app.logger.warning("Login enabled but User model import failed: %s", exc)

        @login_manager.user_loader
        def load_user(user_id: str):
            if not User:
                return None
            try:
                return User.query.get(int(user_id))  # type: ignore[arg-type]
            except Exception:
                return None

    # 9) (Babel or noop) + consolidated context injection
    app.babel = Babel(app)  # attach to app so you can access later
    @app.context_processor
    def _base_ctx() -> dict[str, Any]:
        def has_endpoint(name: str) -> bool:
            return name in app.view_functions

        def safe_url_for(endpoint: str, **values: Any) -> str:
            try:
                return url_for(endpoint, **values)
            except (BuildError, Exception):
                return ""

        static_root = Path(app.static_folder or "app/static")
        css = static_root / "css" / "tailwind.min.css"
        js = static_root / "js" / "main.js"
        asset_version = max(_mtime_or_now(css), _mtime_or_now(js))

        return {
            "app_env": app.config.get("ENV"),
            "app_config": app.config,
            "now": lambda: datetime.now(timezone.utc),
            "_": _t,
            "has_endpoint": has_endpoint,
            "safe_url_for": safe_url_for,
            "asset_version": asset_version,
        }
    # 10) Jinja filters — commas + custom pack (idempotent)
    def _comma(val: Any) -> str:
        """Format numbers with thousands separators; pass through on failure."""
        try:
            f = float(val)
            return f"{int(f):,}" if f.is_integer() else f"{f:,.2f}"
        except (TypeError, ValueError):
            return str(val if val is not None else "")

    # don't clobber if already present
    app.jinja_env.filters.setdefault("comma", _comma)

    try:
        # your file that registers: unique_by, unique_events, money, slugify, etc.
        from .jinja_filters import register_jinja_filters
        register_jinja_filters(app)
        app.logger.info("🧰 Jinja filters registered")
    except Exception:
        app.logger.warning("⚠️ Could not register custom Jinja filters", exc_info=True)

    # 11) Error handling (content-negotiated)
    def _wants_json() -> bool:
        accept = (request.headers.get("Accept") or "").lower()
        wants = "application/json" in accept or request.path.startswith("/api")
        # prefer explicit JSON requests as well
        return wants or request.is_json

    @app.errorhandler(HTTPException)
    def _http_err(err: HTTPException):
        if _wants_json():
            return _json_error(
                err.description or err.name, err.code or 500,
                request_id=getattr(g, "request_id", None),
            )
        return err

    @app.errorhandler(Exception)
    def _uncaught(err: Exception):
        app.logger.exception("Unhandled error: %s", err)
        if _wants_json():
            status = err.code if isinstance(err, HTTPException) else 500  # type: ignore[attr-defined]
            return _json_error("Internal Server Error", status, request_id=getattr(g, "request_id", None))
        return InternalServerError()

    # 12) Blueprints
    _safe_register(app, "app.routes.main",          "main_bp",    "/")
    _safe_register(app, "app.routes.api",           "api_bp",     "/api")
    _safe_register(app, "app.routes.sms",           "sms_bp",     "/sms")
    _safe_register(app, "app.routes.stripe_routes", "stripe_bp",  "/stripe")
    _safe_register(app, "app.routes.webhooks",      "webhook_bp", "/webhooks")
    _safe_register(app, "app.admin.routes",         "admin",      "/admin")

    # 13) CLI
    if USE_CLI and starforge:
        try:
            app.cli.add_command(starforge)
            app.logger.info("🛠️  Registered CLI group: starforge")
        except Exception:
            app.logger.debug("CLI registration failed", exc_info=True)

    # 14) Health & version
    @app.get("/healthz")
    def _healthz():
        return {
            "status": "ok",
            "message": "FundChamps Flask live!",
            "request_id": getattr(g, "request_id", None),
        }

    @app.get("/version")
    def _version():
        return {"version": os.getenv("GIT_COMMIT", "dev"), "env": app.config.get("ENV")}

    # 14.1) Template globals (avoid using current_app in Jinja)
    env = app.jinja_env
    env.globals.setdefault("url_for", url_for)  # ensure available even in partials
    env.globals.setdefault("has_endpoint", lambda n: n in app.view_functions)
    env.globals.setdefault(
        "safe_url_for",
        lambda ep, **kw: (url_for(ep, **kw) if ep in app.view_functions else "/" + ep.split(".")[-1]),
    )
    env.globals.setdefault("app_config", app.config)
    env.globals.setdefault("app_env", app.config.get("ENV"))

    # 15) Launch banner + payment key hints
    stripe_ok = bool(os.getenv("STRIPE_SECRET_KEY"))
    paypal_ok = bool(os.getenv("PAYPAL_CLIENT_ID") and os.getenv("PAYPAL_SECRET"))
    app.logger.info(
        "Payments config: Stripe=%s, PayPal=%s",
        "✅" if stripe_ok else "❌",
        "✅" if paypal_ok else "❌",
    )
    print(
        "\n".join((
            "┌────────────────────────────────────────────┐",
            "│  🌟 FundChamps Flask: Ready to Launch       │",
            f"│  ENV = {app.config.get('ENV','unknown'):<12}   DEBUG = {str(app.debug):<5}   │",
            f"│  Stripe={'ON ' if stripe_ok else 'OFF'}  PayPal={'ON ' if paypal_ok else 'OFF'}          │",
            "└────────────────────────────────────────────┘",
        ))
    )

    from app.blueprints.donations import bp as donations_bp

    app.register_blueprint(donations_bp)

    # ---- CSRF cookie (auto-injected for JS/AJAX) ----
    @app.after_request
    def inject_csrf_cookie(resp):
        try:
            resp.set_cookie("csrf_token", generate_csrf(), samesite="Lax", secure=False)
        except Exception:
            pass
        return resp

    # ---- Global safe team defaults (so base.html never explodes) ----
    @app.context_processor
    def _fc_inject_team_defaults():
        cfg = app.config.get("TEAM_CONFIG", {}) if hasattr(app, "config") else {}
        # prefer lower-case keys, fall back to upper-case, then hard defaults
        tn = cfg.get("team_name") or cfg.get("TEAM_NAME") or "Connect ATX Elite"
        tc = cfg.get("theme_color") or cfg.get("THEME_COLOR") or "#facc15"
        class _Obj(dict):
            __getattr__ = dict.get
        return {"team": _Obj(team_name=tn, theme_color=tc)}

    # ---- Global safe team defaults (so base.html never explodes) ----
    @app.context_processor
    def _fc_inject_team_defaults():
        cfg = app.config.get("TEAM_CONFIG", {}) if hasattr(app, "config") else {}
        # prefer lower-case keys, fall back to upper-case, then hard defaults
        tn = cfg.get("team_name") or cfg.get("TEAM_NAME") or "Connect ATX Elite"
        tc = cfg.get("theme_color") or cfg.get("THEME_COLOR") or "#facc15"
        class _Obj(dict):
            __getattr__ = dict.get
        return {"team": _Obj(team_name=tn, theme_color=tc)}

    return app

from flask_wtf.csrf import CSRFProtect, generate_csrf
csrf = CSRFProtect()
