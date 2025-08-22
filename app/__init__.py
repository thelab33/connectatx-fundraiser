from __future__ import annotations  # For forward compatibility with type annotations
import logging
import os
from typing import Any, Optional, Type
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from importlib import import_module
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from flask_wtf.csrf import CSRFProtect

# Load environment variables from .env
load_dotenv()

# Project root directory (connectatx-fundraiser/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Core extensions (must exist)
from app.extensions import db, migrate, socketio, mail

# Optional extensions setup
USE_LOGIN = USE_BABEL = USE_CLI = False

# ─────────────────────────────────────────────────────────────
# Optional Extension Configurations
# ─────────────────────────────────────────────────────────────

try:
    from flask_login import LoginManager, current_user
    login_manager: Optional[LoginManager] = LoginManager()
    USE_LOGIN = True
except ImportError:
    login_manager = None

try:
    from flask_babel import Babel, _ as _t
    USE_BABEL = True
except ImportError:
    Babel = None
    _t = lambda s: s

try:
    from app.cli import starforge
    USE_CLI = True
except ImportError:
    starforge = None

# ─────────────────────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────────────────────

def _resolve_config(target: str | Type[Any]) -> str | Type[Any]:
    """Resolve a dotted path or config class to be used by Flask."""
    if isinstance(target, str):
        if target == "app.config.config.DevelopmentConfig":
            return "app.config.DevelopmentConfig"
        return target
    return target

def _json_error(message: str, status: int, **extra: Any):
    """Return a structured JSON error response."""
    payload = {"status": "error", "message": message, **extra}
    return jsonify(payload), status

def _file_mtime_version(path: Path) -> int:
    """Return the file's last modified timestamp."""
    try:
        return int(path.stat().st_mtime)
    except Exception:
        return int(datetime.utcnow().timestamp())

def _configure_logging(app: Flask) -> None:
    """Configure logging for the app."""
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=app.config.get("LOG_LEVEL", "INFO"),
            format="%(asctime)s [%(levelname)s] %(message)s",
        )
    logging.getLogger("werkzeug").setLevel(app.config.get("WERKZEUG_LOG_LEVEL", "WARNING"))
    logging.info("Loaded configuration: %s | DEBUG=%s", app.config.get("ENV", "unknown"), app.debug)
    logging.info("DB: %s", app.config.get("SQLALCHEMY_DATABASE_URI", "<unset>"))

# ─────────────────────────────────────────────────────────────
# Flask Application Factory
# ─────────────────────────────────────────────────────────────

def create_app(config_class: str | Type[Any] | None = None) -> Flask:
    """Create and configure the Starforge Flask app."""
    app = Flask(
        __name__,
        static_folder=str(BASE_DIR / "app/static"),
        template_folder=str(BASE_DIR / "app/templates"),
    )

    # Initialize CSRFProtection after the app is created
    csrf = CSRFProtect()
    csrf.init_app(app)  # Initialize CSRFProtect here

    # 1) Config Loading
    default_cfg = os.getenv("FLASK_CONFIG", "app.config.DevelopmentConfig")
    target_cfg = _resolve_config(config_class or default_cfg)
    try:
        app.config.from_object(target_cfg)
    except (ImportError, AttributeError, ModuleNotFoundError) as exc:
        legacy = "app.config.config.DevelopmentConfig"
        if isinstance(target_cfg, str) and target_cfg != legacy:
            try:
                app.config.from_object(legacy)
            except Exception:
                raise RuntimeError(f"❌ Invalid FLASK_CONFIG '{target_cfg}': {exc}") from exc
        else:
            raise RuntimeError(f"❌ Invalid FLASK_CONFIG '{target_cfg}': {exc}") from exc

    # 2) Logging Configuration
    _configure_logging(app)

    # 3) CORS Setup
    default_origin = "*" if app.config.get("ENV") != "production" else os.getenv(
        "PRIMARY_ORIGIN", "https://connect-atx-elite.com"
    )
    cors_origins = os.getenv("CORS_ORIGINS", default_origin)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": cors_origins}})

    # 4) Security headers / CSP (optional)
    if app.config.get("ENV") == "production":
        try:
            from flask_talisman import Talisman
            Talisman(app, content_security_policy=None)
        except ImportError:
            logging.warning("⚠️ flask-talisman not installed – skipping CSP setup")

    # 5) Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins=cors_origins)
    mail.init_app(app)

    # 6) Request ID middleware
    @app.before_request
    def _assign_request_id() -> None:
        g.request_id = request.headers.get("X-Request-ID", uuid4().hex)

    @app.after_request
    def _inject_request_id(resp):
        resp.headers.setdefault("X-Request-ID", getattr(g, "request_id", uuid4().hex))
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return resp

    # 7) Login (optional)
    if USE_LOGIN and login_manager:
        login_manager.init_app(app)
        try:
            from app.models.user import User
        except Exception as exc:
            logging.warning("Login enabled but User model import failed: %s", exc)
            User = None

        @login_manager.user_loader
        def load_user(user_id: str):
            if not User:
                return None
            try:
                return User.query.get(int(user_id))
            except Exception:
                return None

        @app.context_processor
        def _inject_user() -> dict[str, Any]:
            return {"current_user": current_user}
    else:
        @app.context_processor
        def _inject_user() -> dict[str, Any]:
            class _Anon:
                is_authenticated = False
                def __bool__(self) -> bool:
                    return False
            return {"current_user": _Anon()}

    # 8) Babel (optional)
    if USE_BABEL and Babel:
        babel = Babel(app)

        @app.context_processor
        def _inject_babel() -> dict[str, Any]:
            return {"_": _t}
    else:
        @app.context_processor
        def _inject_noop() -> dict[str, Any]:
            return {"_": (lambda s: s)}

    # 9) CLI Commands (optional)
    if USE_CLI and starforge:
        app.cli.add_command(starforge)

    # 10) Template Context: env, now, team, asset_version
    @app.context_processor
    def _inject_env() -> dict[str, Any]:
        return {"app_env": app.config.get("ENV"), "app_config": app.config}

    @app.context_processor
    def _inject_now() -> dict[str, Any]:
        return {"now": datetime.utcnow}

    @app.context_processor
    def _inject_team() -> dict[str, Any]:
        class _Empty:
            def __getattr__(self, _):  
                return None
            def __str__(self) -> str:
                return ""
        return {"team": _Empty()}

    @app.context_processor
    def _inject_asset_versions() -> dict[str, Any]:
        css = Path(app.static_folder or "app/static") / "css" / "tailwind.min.css"
        js = Path(app.static_folder or "app/static") / "js" / "main.js"
        return {"asset_version": max(_file_mtime_version(css), _file_mtime_version(js))}

    # 11) Jinja Filters
    def _comma_like(val: Any) -> Any:
        try:
            return f"{int(val):,}"
        except (ValueError, TypeError):
            try:
                return f"{float(val):,}"
            except (ValueError, TypeError):
                return val

    app.add_template_filter(_comma_like, "comma")

    try:
        from .filters import commafy  
        app.jinja_env.filters["commafy"] = commafy
    except Exception:
        app.jinja_env.filters["commafy"] = _comma_like  

    # 12) Error Handling
    def _wants_json() -> bool:
        return "application/json" in request.headers.get("Accept", "") or request.path.startswith("/api")

    @app.errorhandler(HTTPException)
    def _handle_http_exc(err: HTTPException):
        if _wants_json():
            return _json_error(err.description or err.name, err.code or 500)
        return err

    @app.errorhandler(Exception)
    def _handle_uncaught(err: Exception):
        logging.exception("Unhandled error: %s", err)
        if _wants_json():
            return _json_error("Internal Server Error", 500, request_id=getattr(g, "request_id", None))
        return err

    # 13) Register Blueprints After Configuration to Prevent Circular Imports
    from app.routes.main import main_bp  # Ensure correct import of main_bp
    app.register_blueprint(main_bp)

    # Register other optional blueprints dynamically
    for dotted, prefix in (("app.api", "/api"), ("app.sms", "/sms")):
        try:
            mod = import_module(dotted)
            bp = getattr(mod, "api_bp", None) or getattr(mod, "bp", None)
            if not bp:
                raise AttributeError("No blueprint named 'api_bp' or 'bp'")
            app.register_blueprint(bp, url_prefix=prefix)
        except (ModuleNotFoundError, AttributeError) as exc:
            logging.warning("⚠️ Blueprint %s not registered: %s", dotted, exc)

    try:
        admin_bp = import_module("app.admin.routes").admin
        app.register_blueprint(admin_bp, url_prefix="/admin")
    except (ModuleNotFoundError, AttributeError) as exc:
        logging.info("Admin dashboard not found – skipping (%s)", exc)

    # 14) Health & Version Endpoints
    @app.get("/healthz")
    def _healthz():
        return {
            "status": "ok",
            "message": "Starforge Flask live!",
            "request_id": getattr(g, "request_id", None),
        }

    @app.get("/version")
    def _version():
        return {
            "version": os.getenv("GIT_COMMIT", "dev"),
            "env": app.config.get("ENV"),
        }

    # 15) Launch Banner
    print(
        "\n".join(
            (
                "┌────────────────────────────────────────────┐",
                "│  🌟 Starforge SaaS: Flask Ready to Launch  │",
                f"│  ENV = {app.config.get('ENV', 'unknown'):<12}   DEBUG = {str(app.debug):<5}   │",
                "└────────────────────────────────────────────┘",
            )
        )
    )

    return app

# Export the create_app function for use
__all__ = ["create_app"]

