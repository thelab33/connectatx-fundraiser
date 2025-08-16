# app/__init__.py
from __future__ import annotations
import logging, os, time, secrets, re
from datetime import datetime, timezone
from importlib import import_module
from pathlib import Path
from typing import Any, Type
from uuid import uuid4

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request, url_for
from werkzeug.exceptions import HTTPException, InternalServerError
from werkzeug.routing import BuildError

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent

from app.extensions import db, migrate, socketio, mail, csrf, cors, login_manager, babel

try:
    from flask_compress import Compress
except Exception:
    Compress = None
try:
    from flask_talisman import Talisman
except Exception:
    Talisman = None
try:
    from flask_wtf.csrf import generate_csrf
except Exception:
    generate_csrf = None

ConfigLike = str | Type[Any]

def _resolve_config(target: ConfigLike | None) -> ConfigLike:
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

def _safe_register(app: Flask, dotted: str, attr: str, url_prefix: str | None) -> bool:
    disable = {p.strip().lower() for p in os.getenv("DISABLE_BPS", "").split(",") if p.strip()}
    key = f"{dotted}:{attr}".lower()
    if dotted.split(".")[-1] in disable or key in disable:
        app.logger.info(f"⏭️  Disabled: {dotted}")
        return False
    try:
        mod = import_module(dotted)
        bp = getattr(mod, attr, None)
    except Exception as e:
        app.logger.warning(f"⚠️  Import failed: {dotted} → {e}")
        return False
    if not bp:
        app.logger.warning(f"⚠️  Missing attr '{attr}' in {dotted}")
        return False
    if bp.name in app.blueprints:
        app.logger.info(f"⏭️  Already registered: {bp.name}")
        return False
    try:
        app.register_blueprint(bp, url_prefix=url_prefix or getattr(bp, "url_prefix", None))
        app.logger.info(f"🧩 Registered: {bp.name:<20} → {url_prefix or '/'}")
        return True
    except Exception as exc:
        app.logger.error(f"❌ Failed to register {dotted}: {exc}", exc_info=True)
        return False

SCRIPT_TAG = re.compile(r'(<script\b(?![^>]*\bnonce=)[^>]*>)', re.IGNORECASE)
STYLE_TAG  = re.compile(r'(<style\b(?![^>]*\bnonce=)[^>]*>)', re.IGNORECASE)

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
    app.config.setdefault("JSON_SORT_KEYS", False)

    # Prod-grade defaults
    app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
    app.config.setdefault("SESSION_COOKIE_SECURE", app.config.get("ENV") == "production")

    _configure_logging(app)

    cors_origins = _parse_cors_origins(app.config.get("ENV", "development"))
    if cors:
        cors.init_app(app, supports_credentials=True,
                      resources={r"/api/*": {"origins": cors_origins}},
                      expose_headers=["X-Request-ID"],
                      allow_headers=["Content-Type", "Authorization"],
                      methods=["GET","POST","PUT","PATCH","DELETE","OPTIONS"])

    # Security headers / CSP (talisman optional; we set headers ourselves)
    if app.config.get("ENV") == "production" and Talisman:
        Talisman(app, content_security_policy=None)

    # Extensions
    if csrf: csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins=cors_origins)
    mail.init_app(app)
    if Compress: Compress(app)

    # Nonce & headers
    @app.before_request
    def _gen_nonce():
        g.csp_nonce = secrets.token_urlsafe(16)
        g.request_id = request.headers.get("X-Request-ID", uuid4().hex)
        g._start_ts = time.perf_counter()

    @app.context_processor
    def inject_csp():
        return {
            "csp_nonce": lambda: getattr(g, "csp_nonce", ""),
            "NONCE": getattr(g, "csp_nonce", "")
        }

    @app.after_request
    def _std_headers(resp):
        nonce = getattr(g, "csp_nonce", "")
        csp = (
          "default-src 'self'; "
          f"script-src 'self' 'nonce-{nonce}' 'strict-dynamic'; "
          "connect-src 'self' https://api.stripe.com wss:; "
          "img-src 'self' data: https:; "
          "style-src 'self' 'unsafe-inline'; "
          "font-src 'self' data:; "
          "frame-ancestors 'none'; base-uri 'self'; "
          "form-action 'self' https://checkout.stripe.com;"
        )
        resp.headers.setdefault("Content-Security-Policy", csp)
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        resp.headers.setdefault("Permissions-Policy", "camera=(), geolocation=(), microphone=(), payment=()")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Request-ID", g.request_id)
        # HSTS only when HTTPS
        if request.is_secure or app.config.get("PREFERRED_URL_SCHEME") == "https":
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")
        # Server-Timing
        try:
            dur_ms = (time.perf_counter() - g._start_ts) * 1000.0
            resp.headers.setdefault("Server-Timing", f"app;dur={dur_ms:.1f}")
        except Exception:
            pass
        return resp

    # Patch Jinja render to auto-inject nonce on stray style/script (defensive)
    from flask import render_template as _flask_render
    def _render(*args, **kwargs):
        html = _flask_render(*args, **kwargs)
        nonce = getattr(g, "csp_nonce", "")
        if nonce:
            html = SCRIPT_TAG.sub(rf'<script nonce="{nonce}"', html)
            html = STYLE_TAG.sub(rf'<style nonce="{nonce}"', html)
        return html
    app.jinja_env.globals['render_template'] = _render

    # Login
    if login_manager:
        login_manager.init_app(app)
        login_manager.login_view = "main_bp.home"
        try:
            from app.models.user import User  # optional
        except Exception:
            User = None
        @login_manager.user_loader
        def load_user(uid: str):
            return User.query.get(int(uid)) if User else None

    if babel:
        babel.init_app(app)

    # Base context
    @app.context_processor
    def _base_ctx():
        def has_endpoint(name: str) -> bool:
            return name in app.view_functions
        def safe_url_for(endpoint: str, **values: Any) -> str:
            try: return url_for(endpoint, **values)
            except (BuildError, Exception): return ""
        static_root = Path(app.static_folder)
        css = static_root / "css" / "app.css"
        js  = static_root / "js" / "main.js"
        asset_version = max(_mtime_or_now(css), _mtime_or_now(js))
        # minimal team default (so templates never break)
        class _Obj(dict): __getattr__ = dict.get
        team_default = _Obj(team_name="Connect ATX Elite", theme_color="#facc15")
        return {
            "app_env": app.config.get("ENV"),
            "app_config": app.config,
            "now": lambda: datetime.now(timezone.utc),
            "has_endpoint": has_endpoint,
            "safe_url_for": safe_url_for,
            "asset_version": asset_version,
            "team": team_default
        }

    # Errors → JSON for /api or Accept: application/json
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

    # Blueprints
    blueprints = [
        ("app.routes.main",  "main_bp", "/"),
        ("app.routes.api",   "bp",      "/api"),
        ("app.admin.routes", "bp",      "/admin"),
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
                    secure=(app.config.get("ENV") == "production")
                )
            except Exception:
                pass
            return resp

    # Launch banner
    stripe_ok = bool(os.getenv("STRIPE_SECRET_KEY"))
    paypal_ok = bool(os.getenv("PAYPAL_CLIENT_ID") and os.getenv("PAYPAL_SECRET"))
    print(
        f"┌────────────────────────────────────────────┐\n"
        f"│  🌟 FundChamps Flask: Ready to Launch       │\n"
        f"│  ENV = {app.config.get('ENV','unknown'):<12}   DEBUG = {str(app.debug):<5}   │\n"
        f"│  Stripe={'ON ' if stripe_ok else 'OFF'}  PayPal={'ON ' if paypal_ok else 'OFF'}          │\n"
        f"│  Blueprints: {len(app.blueprints):<3}                         │\n"
        f"└────────────────────────────────────────────┘"
    )
    return app

