# app/__init__.py
from __future__ import annotations

import logging, os, time, secrets, re
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Type, Iterable
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request, url_for
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.routing import BuildError

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

# Core extensions
from app.extensions import db, migrate, socketio, mail, csrf, cors, login_manager, babel

# Optional extras
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

ConfigLike = str | Type[Any]

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
def _resolve_config(target: ConfigLike | None) -> ConfigLike:
    """Resolve a config class path or object; allow legacy env value fixup."""
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
        app.logger.info(f"⏭️  Disabled module: {dotted}")
        return False

    try:
        mod = import_module(dotted)
    except Exception as e:
        app.logger.warning(f"⚠️  Import failed: {dotted} → {e}")
        return False

    from flask import Blueprint as _BP  # local import to avoid import cycles

    # Try requested attr(s) first, then common fallbacks.
    wanted = _iter_candidates(attr) + ["bp", "api_bp", "main_bp", "admin_bp"]
    bp = None
    for name in wanted:
        cand = getattr(mod, name, None)
        if cand and isinstance(cand, _BP):
            bp = cand
            break

    if not bp:
        app.logger.warning(f"⚠️  No blueprint attr found in {dotted} (tried: {', '.join(wanted)})")
        return False

    if bp.name in app.blueprints:
        app.logger.info(f"⏭️  Already registered: {bp.name}")
        return False

    try:
        app.register_blueprint(bp, url_prefix=url_prefix or getattr(bp, "url_prefix", None))
        app.logger.info(f"🧩 Registered: {bp.name:<20} → {url_prefix or '/'}")
        return True
    except Exception as exc:
        app.logger.error(f"❌ Failed to register {dotted}:{bp.name}: {exc}", exc_info=True)
        return False

# Regex for auto-nonce injection on stray tags (optional, cheap, guarded)
SCRIPT_TAG = re.compile(r"(<script\b(?![^>]*\bnonce=)[^>]*>)", re.IGNORECASE)
STYLE_TAG  = re.compile(r"(<style\b(?![^>]*\bnonce=)[^>]*>)",  re.IGNORECASE)

# ─────────────────────────────────────────────────────────────────────────────
# App Factory
# ─────────────────────────────────────────────────────────────────────────────
def create_app(config_class: ConfigLike | None = None) -> Flask:
    app = Flask(
        __name__,
        static_folder=str(BASE_DIR / "app/static"),
        template_folder=str(BASE_DIR / "app/templates"),
    )

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
    app.config.setdefault("JSON_SORT_KEYS", False)
    app.config.setdefault("JSON_AS_ASCII", False)
    app.config.setdefault("PROPAGATE_EXCEPTIONS", False)
    app.config.setdefault("AUTO_NONCE_HTML", True)  # auto-inject nonce on stray <script>/<style>
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SECURE", app.config.get("ENV") == "production")

    _configure_logging(app)

    # CORS
    cors_origins = _parse_cors_origins(app.config.get("ENV", "development"))
    if cors:
        cors.init_app(
            app,
            supports_credentials=True,
            resources={r"/api/*": {"origins": cors_origins}},
            expose_headers=["X-Request-ID"],
            allow_headers=["Content-Type", "Authorization"],
            methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"],
        )

    # Security headers / CSP (Talisman optional; we still set precise headers below)
    if app.config.get("ENV") == "production" and Talisman:
        # Let us manage CSP ourselves to include PayPal/Stripe/Socket.IO
        Talisman(app, content_security_policy=None)

    # Extensions
    if csrf: csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins=cors_origins if cors_origins else "*")
    mail.init_app(app)
    if Compress: Compress(app)

    # Request bootstrap (nonce, request id, timing)
    @app.before_request
    def _gen_nonce():
        g.csp_nonce = secrets.token_urlsafe(16)
        g.request_id = request.headers.get("X-Request-ID", uuid4().hex)
        g._start_ts = time.perf_counter()

    # Template access to nonce (both csp_nonce() and NONCE)
    @app.context_processor
    def inject_csp():
        return {
            "csp_nonce": lambda: getattr(g, "csp_nonce", ""),
            "NONCE": getattr(g, "csp_nonce", ""),
        }

    # Security headers after each response (incl. CSP)
    @app.after_request
    def _std_headers(resp):
        nonce = getattr(g, "csp_nonce", "")

        # Build CSP with payment + websocket + CDN allowances
        # Stripe + PayPal + Socket.IO (cdn + wss)
        stripe_js = "https://js.stripe.com"
        stripe_api = "https://api.stripe.com"
        paypal_core = "https://www.paypal.com"
        paypal_objs = "https://*.paypalobjects.com"
        paypal_all  = "https://*.paypal.com"
        paypal_api_live = "https://api-m.paypal.com"
        paypal_api_sbx  = "https://api-m.sandbox.paypal.com"
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

        # HSTS (HTTPS only)
        if request.is_secure or app.config.get("PREFERRED_URL_SCHEME") == "https":
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")

        # Server-Timing
        try:
            dur_ms = (time.perf_counter() - g._start_ts) * 1000.0
            resp.headers.setdefault("Server-Timing", f"app;dur={dur_ms:.1f}")
        except Exception:
            pass

        # Optional: auto-inject nonce into stray tags in HTML bodies (defense-in-depth)
        try:
            if (
                app.config.get("AUTO_NONCE_HTML", True)
                and nonce
                and resp.mimetype == "text/html"
                and resp.direct_passthrough is False
            ):
                text = resp.get_data(as_text=True)
                if "<script" in text or "<style" in text:
                    def _add_nonce(m):
                        tag = m.group(1)
                        return tag[:-1] + f' nonce="{nonce}">'
                    text = SCRIPT_TAG.sub(_add_nonce, text)
                    text = STYLE_TAG.sub(_add_nonce, text)
                    resp.set_data(text)
        except Exception:
            # Never fail a response over best-effort HTML post-process
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

    # Base context that never breaks templates
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
        css = static_root / "css" / "tailwind.min.css"
        js  = static_root / "js"  / "bundle.min.js"
        asset_version = max(_mtime_or_now(css), _mtime_or_now(js))

        class _Obj(dict):
            __getattr__ = dict.get

        team_default = _Obj(team_name="Connect ATX Elite", theme_color="#facc15")
        return {
            "app_env": app.config.get("ENV"),
            "app_config": app.config,
            "now": lambda: datetime.now(timezone.utc),
            "has_endpoint": has_endpoint,
            "safe_url_for": safe_url_for,
            "asset_version": asset_version,
            "team": team_default,  # overridden by real team in views when available
        }

    # JSON errors for API requests / JSON Accept header
    def _wants_json() -> bool:
        accept = (request.headers.get("Accept") or "").lower()
        return "application/json" in accept or request.path.startswith("/api") or request.is_json

    @app.errorhandler(HTTPException)
    def _http_err(err):
        return _json_error(err.description or err.name, err.code, request_id=g.request_id) if _wants_json() else err

    @app.errorhandler(Exception)
    def _uncaught(err):
        app.logger.exception("Unhandled error: %s", err)
        return _json_error("Internal Server Error", 500, request_id=g.request_id) if _wants_json() else InternalServerError()

    # Blueprints (attr supports fallbacks: bp|api_bp|main_bp)
    blueprints = [
        ("app.routes.main",  "main_bp|bp", "/"),
        ("app.routes.api",   "bp|api_bp",  "/api"),
        ("app.admin.routes", "bp|admin_bp","/admin"),
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

