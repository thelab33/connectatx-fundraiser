# app/extensions.py
from __future__ import annotations

"""
App extensions and utilities (singletons + helpers)

- Core Flask extensions: db, migrate, mail, socketio, csrf, cors, login_manager, babel
- Background task utilities with clean shutdown
- Safe DB helpers (commit + retry decorator)
- Email helper with optional Jinja templates, attachments, retries, async send
- Lightweight pub/sub (Blinker) + safe socket emit
"""

import atexit
import logging
import os
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

from flask_mail import Mail, Message
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy

# ── Optional deps (import-if-present) ─────────────────────────
def _try_import(name: str, attr: str) -> Any:
    try:
        return __import__(name, fromlist=[attr]).__getattribute__(attr)
    except Exception:
        return None

LoginManager = _try_import("flask_login", "LoginManager")
Babel        = _try_import("flask_babel", "Babel")
CSRFProtect  = _try_import("flask_wtf.csrf", "CSRFProtect")
CORS         = _try_import("flask_cors", "CORS")
SignalNS     = _try_import("blinker", "Namespace")
JinjaEnv     = _try_import("jinja2", "Environment")
FSLoader     = _try_import("jinja2", "FileSystemLoader")
AutoEscape   = _try_import("jinja2", "select_autoescape")

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Core singletons (init via create_app / init_all_extensions)
# ─────────────────────────────────────────────────────────────
db: SQLAlchemy       = SQLAlchemy()
migrate: Migrate     = Migrate()
mail: Mail           = Mail()
socketio: SocketIO   = SocketIO(async_mode=os.getenv("SOCKET_ASYNC_MODE", "threading"))

login_manager: Optional["LoginManager"] = LoginManager() if LoginManager else None
babel: Optional["Babel"]                = Babel() if Babel else None
csrf: Optional["CSRFProtect"]           = CSRFProtect() if CSRFProtect else None
cors: Optional["CORS"]                   = CORS() if CORS else None

# ─────────────────────────────────────────────────────────────
# (1) Background tasks + clean shutdown
# ─────────────────────────────────────────────────────────────
_BG_MAX_WORKERS = int(os.getenv("BG_MAX_WORKERS", "8"))
_EXECUTOR = ThreadPoolExecutor(max_workers=_BG_MAX_WORKERS)

def run_bg(func: Callable[..., Any], *args, **kwargs) -> Future:
    """Run a callable in the shared thread pool."""
    return _EXECUTOR.submit(func, *args, **kwargs)

def run_later(delay_sec: float, func: Callable[..., Any], *args, **kwargs) -> Future:
    """Schedule a callable to run after a delay."""
    def _wrapper():
        time.sleep(max(0.0, delay_sec))
        return func(*args, **kwargs)
    return run_bg(_wrapper)

@atexit.register
def _shutdown_executor() -> None:
    try:
        _EXECUTOR.shutdown(wait=False, cancel_futures=True)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────
# (2) Safe DB helpers
# ─────────────────────────────────────────────────────────────
def safe_commit() -> bool:
    """Commit current session; rollback on failure."""
    try:
        db.session.commit()
        return True
    except Exception as e:
        log.error("DB commit failed: %s", e, exc_info=True)
        db.session.rollback()
        return False

def with_db_retry(retries: int = 2, backoff: float = 0.2):
    """Retry a DB function on transient failures; rollback between attempts."""
    def _wrap(fn: Callable[..., Any]) -> Callable[..., Any]:
        def _inner(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    db.session.rollback()
                    attempt += 1
                    if attempt > retries:
                        raise
                    time.sleep(backoff * attempt)
        return _inner
    return _wrap

# ─────────────────────────────────────────────────────────────
# (3) Email helper
# ─────────────────────────────────────────────────────────────
@dataclass
class EmailAttachment:
    filename: str
    content: bytes
    mimetype: str = "application/octet-stream"

def _attach(msg: Message, attachments: Iterable[EmailAttachment] | None) -> None:
    if not attachments:
        return
    for a in attachments:
        maintype, _, subtype = a.mimetype.partition("/")
        part = MIMEBase(maintype or "application", subtype or "octet-stream")
        part.set_payload(a.content)
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment", filename=a.filename)
        msg.attach(part)

def _render_template(env: Optional["JinjaEnv"], tpl: str, **ctx) -> str:
    if env is None:
        return tpl.format(**ctx) if ctx else tpl
    return env.get_template(tpl).render(**ctx)

def get_mail_env(templates_dir: str = "app/templates/emails") -> Optional["JinjaEnv"]:
    if not JinjaEnv or not FSLoader:
        return None
    loader = FSLoader(templates_dir)
    return JinjaEnv(loader=loader, autoescape=AutoEscape(["html", "xml"]))

def send_email_async(
    app,
    subject: str,
    recipients: list[str],
    *,
    html_template: str | None = None,
    text_template: str | None = None,
    context: dict[str, Any] | None = None,
    attachments: Iterable[EmailAttachment] | None = None,
    sender: str | None = None,
    max_retries: int = 2,
    retry_backoff: float = 0.5,
) -> Future:
    """Render (optionally) and send an email in the background with retries."""
    ctx = context or {}
    env = get_mail_env()

    def _job():
        from flask import current_app
        with app.app_context():
            try:
                html = _render_template(env, html_template, **ctx) if html_template else None
                body = _render_template(env, text_template, **ctx) if text_template else None
                msg = Message(
                    subject=subject,
                    recipients=recipients,
                    sender=sender or app.config.get("DEFAULT_MAIL_SENDER"),
                    html=html,
                    body=body,
                )
                _attach(msg, attachments)
                attempts = 0
                while True:
                    try:
                        mail.send(msg)
                        return True
                    except Exception as e:
                        attempts += 1
                        if attempts > max_retries:
                            raise
                        (current_app.logger if current_app else log).warning(
                            "Mail send failed (attempt %s/%s): %s",
                            attempts, max_retries, e
                        )
                        time.sleep(retry_backoff * attempts)
            except Exception as e:
                (current_app.logger if current_app else log).error(
                    "Email send permanently failed: %s", e, exc_info=True
                )
                return False

    return run_bg(_job)

# ─────────────────────────────────────────────────────────────
# (4) Lightweight signals + safe socket emit
# ─────────────────────────────────────────────────────────────
if SignalNS:
    _signals = SignalNS()
    app_event = _signals.signal("app-event")
else:
    app_event = None  # type: ignore

def emit_socket(event: str, data: dict[str, Any] | None = None, room: str | None = None) -> bool:
    """Safe Socket.IO emit wrapper — won’t raise if server not initialized yet."""
    try:
        socketio.emit(event, data or {}, to=room)
        return True
    except Exception as e:
        log.warning("socket emit failed: %s", e)
        return False

# ─────────────────────────────────────────────────────────────
# (5) Convenience init function
# ─────────────────────────────────────────────────────────────
def init_all_extensions(app, *, cors_origins: Any = "*") -> None:
    """One-liner to init everything (if present)."""
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    if csrf:
        csrf.init_app(app)
    if cors and cors_origins is not None:
        cors.init_app(app, resources={r"/*": {"origins": cors_origins}}, supports_credentials=True)
    if login_manager:
        login_manager.init_app(app)

    socketio.init_app(app, cors_allowed_origins=cors_origins)

__all__ = [
    "db", "migrate", "mail", "socketio", "login_manager", "babel", "csrf", "cors",
    "run_bg", "run_later", "safe_commit", "with_db_retry",
    "EmailAttachment", "send_email_async", "emit_socket",
    "init_all_extensions", "app_event",
]


socketio = SocketIO(async_mode="threading", cors_allowed_origins="*")
