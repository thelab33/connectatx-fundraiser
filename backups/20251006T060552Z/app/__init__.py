# app/__init__.py
from __future__ import annotations

import json
import logging
import os
import re
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

# Core extensions (defined in app/extensions.py)
from app.extensions import babel, cors, csrf, db, login_manager, mail, socketio

# Optional extras (loaded if present)
try:
    from flask_compress import Compress  # type: ignore
except Exception:  # pragma: no cover
    Compress = None

try:
    from flask_talisman import Talisman  # type: ignore
except Exception:  # pragma: no cover
    Talisman = None

try:
    from flask_wtf.csrf import generate_csrf  # type: ignore
except Exception:  # pragma: no cover
    generate_csrf = None

# Optional Sentry
try:
    import sentry_sdk  # type: ignore
    from sentry_sdk.integrations.flask import FlaskIntegration  # type: ignore
    from sentry_sdk.integrations.logging import LoggingIntegration  # type: ignore
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration  # type: ignore
except Exception:  # pragma: no cover
    sentry_sdk = None  # type: ignore

from flask_migrate import Migrate

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
ConfigLike = str | Type[Any]

# ───────────────────────────── Helpers ───────────────────────────── #

def _resolve_config(target: ConfigLike | None) -> ConfigLike:
    """Resolve a config path/class; honor a legacy env value."""
    if target is None:
        target = os.getenv("FLASK_CONFIG", "app.config.DevelopmentConfig")
    if isinstance(target, str) and target == "app.config.config.DevelopmentConfig":
        return "app.config.DevelopmentConfig"
    return target


def _json_error(message: str, status: int, **extra: Any):
    payload = {"ok": False, "error": {"code": status, "message": message}}
    rid = extra.pop("request_id", None)
    if rid:
        payload["error"]["request_id"] = rid
    if extra:
        payload["error"].update(extra)
    resp = jsonify(payload)
    resp.status_code = status
    return resp


def _mtime_or_now(path: Path) -> int:
    try:
        return int(path.stat().st_mtime)
    except Exception:
        return int(datetime.now(timezone.utc).timestamp())


class _RequestIDFilter(logging.Filter):
    """Inject g.request_id into log records as %(request_id)s."""
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            rid = getattr(g, "request_id", "-")
        except Exception:
            rid = "-"
        record.request_id = rid
        return True


def _configure_logging(app: Flask) -> None:
    fmt = "%(asctime)s [%(levelname)s] %(name)s [rid=%(request_id)s]: %(message)s"
    root = logging.getLogger()

    if not root.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter(fmt))
        h.addFilter(_RequestIDFilter())
        root.addHandler(h)
    else:
        for h in root.handlers:
            h.addFilter(_RequestIDFilter())
            if not getattr(h, "formatter", None) or "%(request_id)s" not in getattr(h.formatter, "_fmt", ""):
                h.setFormatter(logging.Formatter(fmt))

    root.setLevel(app.config.get("LOG_LEVEL", "INFO"))
    logging.getLogger("werkzeug").setLevel(app.config.get("WERKZEUG_LOG_LEVEL", "WARNING"))

    app.logger.info("Loaded config: %s | DEBUG=%s", app.config.get("ENV", "?"), app.debug)
    app.logger.info("DB: %s", app.config.get("SQLALCHEMY_DATABASE_URI", "<unset>"))


def _parse_cors_origins(env: str) -> str | list[str]:
    """Return '*' in dev; narrow to PRIMARY_ORIGIN in prod unless CORS_ORIGINS is set."""
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
    """
    Import a module and register a blueprint by attribute name(s).
    Honors DISABLE_BPS=admin,newsletter to skip modules at runtime.
    """
    disabled = {p.strip().lower() for p in os.getenv("DISABLE_BPS", "").split(",") if p.strip()}
    mod_key = dotted.split(".")[-1].lower()
    if mod_key in disabled:
        app.logger.info("⏭️  Disabled module: %s", dotted)
        return False

    try:
        mod = import_module(dotted)
    except Exception as e:
        app.logger.warning("⚠️  Import failed: %s → %s", dotted, e)
        return False

    from flask import Blueprint  # local to avoid cycles
    candidates = _iter_candidates(attr) + ["bp", "api_bp", "main_bp", "admin_bp"]
    bp = None
    for name in candidates:
        cand = getattr(mod, name, None)
        if isinstance(cand, Blueprint):
            bp = cand
            break

    if not bp:
        app.logger.warning("⚠️  No blueprint attr found in %s (tried: %s)", dotted, ", ".join(candidates))
        return False

    if bp.name in app.blueprints:
        app.logger.info("⏭️  Already registered: %s", bp.name)
        return False

    try:
        app.register_blueprint(bp, url_prefix=url_prefix or getattr(bp, "url_prefix", None))
        app.logger.info("🧩 Registered: %-20s → %s", bp.name, url_prefix or "/")
        # opportunistically register shoutouts if present but not active
        try:
            from app.routes import shoutouts as _shoutouts  # type: ignore
            if "shoutouts" not in app.blueprints:
                app.register_blueprint(_shoutouts.bp)
        except Exception:
            pass
        return True
    except Exception as exc:
        app.logger.error("❌ Failed to register %s:%s: %s", dotted, getattr(bp, "name", "?"), exc, exc_info=True)
        return False


# ── Security (CSP/nonce) ───────────────────────────────────────────

_SCRIPT_OPEN = re.compile(r"(<script\b(?![^>]*\bnonce=)[^>]*>)", re.IGNORECASE)
_STYLE_OPEN  = re.compile(r"(<style\b(?![^>]*\bnonce=)[^>]*>)", re.IGNORECASE)

def _build_csp(nonce: str) -> str:
    STRIPE_JS   = "https://js.stripe.com"
    STRIPE_API  = "https://api.stripe.com"
    PAYPAL_CORE = "https://www.paypal.com"
    PAYPAL_ALL  = "https://*.paypal.com"
    PAYPAL_API_LIVE = "https://api-m.paypal.com"
    PAYPAL_API_SBX  = "https://api-m.sandbox.paypal.com"
    SOCKETIO_CDN = "https://cdn.socket.io"
    YT_FRAME = "https://www.youtube-nocookie.com https://www.youtube.com"
    YT_IMG   = "https://i.ytimg.com"

    script_src = (
        f"'self' 'nonce-{nonce}' 'strict-dynamic' "
        f"{STRIPE_JS} {PAYPAL_CORE} {PAYPAL_ALL} {SOCKETIO_CDN}"
    )
    connect_src = f"'self' {STRIPE_API} {PAYPAL_API_LIVE} {PAYPAL_API_SBX} wss:"
    img_src     = f"'self' data: blob: https: {YT_IMG}"
    style_src   = f"'self' 'nonce-{nonce}'"
    font_src    = "'self' https: data:"
    frame_src   = (
        f"'self' {STRIPE_JS} https://checkout.stripe.com "
        f"{PAYPAL_CORE} {PAYPAL_ALL} {YT_FRAME}"
    )
    return (
        "default-src 'self'; "
        f"script-src {script_src}; "
        f"connect-src {connect_src}; "
        f"img-src {img_src}; "
        f"style-src {style_src}; "
        f"font-src {font_src}; "
        f"frame-src {frame_src}; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self' https://checkout.stripe.com https://www.paypal.com; "
        "object-src 'none'"
    )


def init_security(app: Flask) -> None:
    """Nonce in Jinja context + headers (CSP/HSTS/etc)."""

    @app.context_processor
    def _inject_csp_nonce():
        if not hasattr(g, "csp_nonce"):
            from secrets import token_urlsafe
            g.csp_nonce = token_urlsafe(16)
        return {"csp_nonce": g.csp_nonce}

    @app.after_request
    def _apply_security_headers(resp):
        # request id + server timing
        rid = getattr(g, "request_id", None)
        if rid:
            resp.headers.setdefault("X-Request-ID", rid)
        try:
            dur_ms = (time.perf_counter() - getattr(g, "_start_ts", time.perf_counter())) * 1000.0
            resp.headers.setdefault("Server-Timing", f"app;dur={dur_ms:.1f}")
        except Exception:
            pass

        # CSP
        nonce = getattr(g, "csp_nonce", "")
        if app.config.get("AUTO_SET_CSP", True) and nonce:
            resp.headers.setdefault("Content-Security-Policy", _build_csp(nonce))

        # Standard hardening
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Permissions-Policy", "camera=(), geolocation=(), microphone=(), payment=()")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        if request.is_secure or app.config.get("PREFERRED_URL_SCHEME") == "https":
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")

        # Auto-nonce any inline <script>/<style> if allowed
        if (
            app.config.get("AUTO_NONCE_HTML", True)
            and nonce
            and resp.mimetype == "text/html"
            and not resp.direct_passthrough
        ):
            try:
                html = resp.get_data(as_text=True)
                if "<script" in html or "<style" in html:
                    html = _SCRIPT_OPEN.sub(lambda m: m.group(1)[:-1] + f' nonce="{nonce}">', html)
                    html = _STYLE_OPEN.sub(lambda m: m.group(1)[:-1] + f' nonce="{nonce}">', html)
                    resp.set_data(html)
            except Exception:
                pass

        return resp


# ── Static + Asset manifest helpers (Jinja) ─────────────────────────

try:
    from flask import url_for as _url_for  # noqa: N812
except Exception:  # pragma: no cover
    _url_for = None  # type: ignore


def static_url(path: str) -> str:
    """Return a /static URL (works without url_for too)."""
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


def _load_asset_manifest(app: Flask) -> None:
    """
    Reads app/static/asset-manifest.json and exposes:
      - Jinja global SRI: { "css/tailwind.min.css": "sha384-..." }
      - Jinja global ASSET_VER: git sha / built timestamp
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
    """FundChamps Flask App Factory."""
    app = Flask(
        __name__,
        static_folder=str(BASE_DIR / "app/static"),
        template_folder=str(BASE_DIR / "app/templates"),
    )

    # Jinja filters & globals
    def usd(value):
        try:
            return "${:,.0f}".format(float(value))
        except Exception:
            return "$0"
    app.jinja_env.filters["usd"] = usd
    app.jinja_env.globals.setdefault("static_url", static_url)
    app.jinja_env.globals.setdefault("asset_url", static_url)

    def sri_attr(path: str) -> str:
        try:
            sri = (app.jinja_env.globals.get("SRI") or {}).get(path)
            return f' integrity="{sri}" crossorigin="anonymous"' if sri else ""
        except Exception:
            return ""
    app.jinja_env.globals.setdefault("sri_attr", sri_attr)

    # Config (with legacy value support)
    cfg = _resolve_config(config_class)
    try:
        app.config.from_object(cfg)
    except Exception as exc:
        fallback = "app.config.DevelopmentConfig"
        if isinstance(cfg, str) and cfg != fallback:
            app.config.from_object(fallback)
        else:
            raise RuntimeError(f"❌ Invalid FLASK_CONFIG '{cfg}': {exc}") from exc

    # Defaults
    app.url_map.strict_slashes = False
    app.config.setdefault("JSON_SORT_KEYS", False)
    app.config.setdefault("JSON_AS_ASCII", False)
    app.config.setdefault("PROPAGATE_EXCEPTIONS", False)
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SECURE", app.config.get("ENV") == "production")
    app.config.setdefault("AUTO_NONCE_HTML", True)
    app.config.setdefault("AUTO_SET_CSP", True)

    _configure_logging(app)
    _load_asset_manifest(app)

    # Sentry (optional)
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

    # Talisman (optional) — we set CSP in init_security
    if app.config.get("ENV") == "production" and Talisman:
        Talisman(app, content_security_policy=None)

    # Security headers + nonce
    init_security(app)

    # Core extensions
    if csrf:
        csrf.init_app(app)
    db.init_app(app)
    if app.config.get("SQLALCHEMY_DATABASE_URI", "").startswith("sqlite"):
        try:
            with app.app_context():
                db.create_all()
        except Exception:
            pass
    Migrate(app, db, compare_type=True, render_as_batch=True)

    mail.init_app(app)
    if Compress:
        Compress(app)

    # Socket.IO
    app.socketio = socketio
    socketio.init_app(app, cors_allowed_origins=cors_origins if cors_origins else "*")

    # Request bootstrap (rid/nonce/timing + Sentry tags)
    @app.before_request
    def _bootstrap_request():
        from secrets import token_urlsafe
        g.csp_nonce = getattr(g, "csp_nonce", token_urlsafe(16))
        g.request_id = request.headers.get("X-Request-ID") or uuid4().hex
        g._start_ts = time.perf_counter()
        try:
            if sentry_sdk:
                with sentry_sdk.configure_scope() as scope:
                    scope.set_tag("request_id", g.request_id)
                    scope.set_tag("endpoint", request.endpoint or "")
                    scope.set_user({"ip_address": (request.access_route[0] if request.access_route else request.remote_addr)})
        except Exception:
            pass

    # Login manager
    if login_manager:
        login_manager.init_app(app)
        login_manager.login_view = "main.home"
        try:
            from app.models.user import User  # type: ignore
        except Exception:
            User = None

        @login_manager.user_loader
        def load_user(uid: str):
            return User.query.get(int(uid)) if User else None

    if babel:
        babel.init_app(app)

    # Base context for templates
    @app.context_processor
    def _base_ctx():
        def has_endpoint(name: str) -> bool:
            return name in app.view_functions

        def safe_url_for(endpoint: str, **values: Any) -> str:
            try:
                return url_for(endpoint, **values)
            except (BuildError, Exception):
                return ""

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
            "team": team_default,  # views override as needed
        }

    # Error handling (API JSON vs HTML)
    def _wants_json() -> bool:
        accept = (request.headers.get("Accept") or "").lower()
        return "application/json" in accept or request.path.startswith("/api") or request.is_json

    @app.errorhandler(HTTPException)
    def _http_err(err: HTTPException):
        rid = getattr(g, "request_id", None)
        return _json_error(err.description or err.name, err.code or 500, request_id=rid) if _wants_json() else err

    @app.errorhandler(Exception)
    def _uncaught(err: Exception):
        app.logger.exception("Unhandled error")
        rid = getattr(g, "request_id", None)
        return _json_error("Internal Server Error", 500, request_id=rid) if _wants_json() else InternalServerError()

    # Blueprints
    blueprints = [
        ("app.routes.main",           "main_bp|bp", "/"),
        ("app.routes.api",            "bp|api_bp",  "/api"),
        ("app.admin.routes",          "bp|admin_bp","/admin"),
        ("app.blueprints.fc_payments","bp",         "/payments"),
        ("app.blueprints.fc_metrics", "bp",         "/metrics"),
        ("app.routes.newsletter",     "bp",         "/newsletter"),
        ("app.routes.sms",            "sms_bp|bp",  "/sms"),
    ]
    for dotted, attr, prefix in blueprints:
        _safe_register(app, dotted, attr, prefix)

    # Health/version
    @app.get("/healthz")
    def _healthz():
        return {"status": "ok", "message": "FundChamps Flask live!", "request_id": getattr(g, "request_id", None)}

    @app.get("/version")
    def _version():
        return {"version": os.getenv("GIT_COMMIT", "dev"), "env": app.config.get("ENV")}

    # CSRF cookie
    if csrf and generate_csrf:
        @app.after_request
        def _inject_csrf_cookie(resp):
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

