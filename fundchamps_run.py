#!/usr/bin/env python3
from __future__ import annotations
"""
FundChamps Launcher
- Loads env early (dotenv)
- Safe logging (color or JSON)
- Port guard, PID file, optional browser open
- Optional Sentry/ProxyFix
- Socket.IO aware (threading default; override via --async-mode or env)
"""

import os
os.environ.setdefault("SOCKETIO_ASYNC_MODE", "threading")  # safe default

import argparse
import atexit
import json
import logging
import signal
import socket
import sys
import time
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from dotenv import load_dotenv

# ── Optional deps (loaded lazily) ─────────────────────────────────────────────
try:
    from werkzeug.middleware.proxy_fix import ProxyFix  # type: ignore
except Exception:
    ProxyFix = None  # type: ignore

try:
    import sentry_sdk  # type: ignore
    from sentry_sdk.integrations.flask import FlaskIntegration  # type: ignore
except Exception:
    sentry_sdk = None  # type: ignore
    FlaskIntegration = None  # type: ignore


# ── Config model ──────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class RunnerConfig:
    host: str
    port: int
    debug: bool
    config_path: str
    use_reloader: bool
    log_json: bool
    open_browser: bool
    pidfile: Optional[Path]
    routes_out: Optional[Path]
    force_run: bool
    async_mode: str  # "threading" | "eventlet" | "gevent" | "gevent_uwsgi"


# ── Logging setup ─────────────────────────────────────────────────────────────
class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[1;34m",
        "INFO": "\033[1;32m",
        "WARNING": "\033[1;33m",
        "ERROR": "\033[1;31m",
        "CRITICAL": "\033[1;41m",
        "RESET": "\033[0m",
    }
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        msg = super().format(record)
        color = self.COLORS.get(record.levelname, "")
        reset = self.COLORS["RESET"]
        return f"{color}{msg}{reset}"

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        payload = {
            "ts": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)

def setup_logging(debug: bool, json_mode: bool) -> None:
    handler = logging.StreamHandler(sys.stdout)
    if json_mode:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(ColorFormatter("[%(asctime)s] %(levelname)s %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if debug else logging.INFO)


# ── Helpers ───────────────────────────────────────────────────────────────────
def resolve_config_path() -> str:
    env_cfg = os.getenv("FLASK_CONFIG")
    if env_cfg:
        return env_cfg
    env = (os.getenv("FLASK_ENV") or os.getenv("ENV") or "production").lower()
    return {
        "development": "app.config.DevelopmentConfig",
        "testing": "app.config.TestingConfig",
        "production": "app.config.ProductionConfig",
    }.get(env, "app.config.ProductionConfig")

def _ssl_ctx_from_env() -> Optional[Tuple[str, str]]:
    cert = os.getenv("SSL_CERTFILE")
    key = os.getenv("SSL_KEYFILE")
    return (cert, key) if cert and key else None

def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex((host, port)) == 0

def _write_pidfile(pidfile: Path) -> None:
    pidfile.write_text(str(os.getpid()), encoding="utf-8")
    atexit.register(lambda: pidfile.exists() and pidfile.unlink(missing_ok=True))

def _open_browser_later(url: str, delay: float = 0.6) -> None:
    import threading
    def _go():
        try:
            webbrowser.open_new_tab(url)
        except Exception:
            pass
    t = threading.Timer(delay, _go)
    t.daemon = True
    t.start()

def banner(cfg: RunnerConfig) -> None:
    art = """
\033[1;34m
╭─────────────────────────────────────────────────────────────╮
│           🏆  FundChamps Flask SaaS Launcher  🏀           │
╰─────────────────────────────────────────────────────────────╯
\033[0m"""
    print(art)
    print(f"\033[1;33m✨ {datetime.now():%Y-%m-%d %H:%M:%S}: Bootstrapping FundChamps platform...\033[0m")
    print("🔎 ENV:          ", os.getenv("FLASK_ENV", os.getenv("ENV", "production")))
    print("⚙️  CONFIG:       ", cfg.config_path)
    print(f"🌎 Host:Port:    {cfg.host}:{cfg.port}")
    print(f"🐍 Python:       {sys.version.split()[0]}")
    print(f"🧑‍💻 User:         {os.getenv('USER') or os.getenv('USERNAME')}")
    print(f"🕰️  Started at:   {time.strftime('%H:%M:%S')}")
    print("─────────────────────────────────────────────────────────────")
    if cfg.host in {"127.0.0.1", "0.0.0.0", "localhost"}:
        print(f"\033[1;36m💻 Local Dev:    http://127.0.0.1:{cfg.port}\033[0m")

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run the FundChamps Flask app.")
    p.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    p.add_argument("--port", type=int, default=int(os.getenv("PORT", "5000")))
    debug_env = os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"}
    try:
        action = argparse.BooleanOptionalAction  # py3.9+
    except AttributeError:
        action = None
    if action:
        p.add_argument("--debug", default=debug_env, action=action, help="Enable/disable debug mode.")
    else:
        p.add_argument("--debug", action="store_true", default=debug_env, help="Enable debug mode.")
    p.add_argument("--no-reload", action="store_true", help="Disable auto-reloader even in debug.")
    p.add_argument("--log-json", action="store_true", help="Emit structured JSON logs.")
    p.add_argument("--open-browser", action="store_true", help="Open default browser to the app URL.")
    p.add_argument("--pidfile", type=Path, default=None, help="Write the current PID to this file.")
    p.add_argument("--routes-out", type=Path, default=None, help="Dump discovered routes to this file then continue.")
    p.add_argument("--force", dest="force_run", action="store_true", help="Run even if the port looks in use.")
    p.add_argument(
        "--async-mode",
        default=os.getenv("SOCKETIO_ASYNC_MODE", "threading"),
        choices=["threading", "eventlet", "gevent", "gevent_uwsgi"],
        help="Socket.IO async mode (default: threading).",
    )
    return p.parse_args()

def make_runner_config() -> RunnerConfig:
    args = parse_args()
    cfg_path = resolve_config_path()
    debug = bool(getattr(args, "debug", False))
    return RunnerConfig(
        host=args.host,
        port=args.port,
        debug=debug,
        config_path=cfg_path,
        use_reloader=(debug and not args.no_reload),
        log_json=bool(args.log_json),
        open_browser=bool(args.open_browser),
        pidfile=args.pidfile,
        routes_out=args.routes_out,
        force_run=bool(args.force_run),
        async_mode=str(args.async_mode or "threading"),
    )

def graceful_exit(signum, frame) -> None:  # type: ignore[no-untyped-def]
    print("\033[1;33m🛑 FundChamps shutting down — signal received. Exiting gracefully.\033[0m")
    sys.exit(0)

def print_routes(app, debug: bool, routes_out: Optional[Path] = None) -> None:
    rows = []
    for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r)):
        rows.append({"rule": str(rule), "endpoint": rule.endpoint, "methods": sorted(rule.methods or [])})
    if routes_out:
        try:
            routes_out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
            print(f"\n\033[1;35m📝 Routes written to:\033[0m {routes_out}")
        except Exception as e:
            logging.getLogger(__name__).warning("Failed to write routes file: %s", e)
    if debug:
        print("\n\033[1;35m📦 Registered Blueprints:\033[0m", list(app.blueprints.keys()))
        print("\033[1;32m🔗 Routes:\033[0m")
        for r in rows:
            methods = ",".join(r["methods"])
            print(f"  \033[1;34m{r['rule']}\033[0m → {r['endpoint']}  ({methods})")


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    load_dotenv()

    cfg = make_runner_config()

    # Respect CLI async mode for Flask-SocketIO before we import app/extensions
    os.environ["SOCKETIO_ASYNC_MODE"] = cfg.async_mode

    setup_logging(cfg.debug, cfg.log_json)

    # Signals
    for sig in ("SIGINT", "SIGTERM"):
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), graceful_exit)

    # Sentry (optional)
    dsn = os.getenv("SENTRY_DSN")
    if dsn and sentry_sdk and FlaskIntegration:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=float(os.getenv("SENTRY_TRACES", "0.0")),
        )
        logging.getLogger(__name__).info("Sentry initialized")

    # PID file
    if cfg.pidfile:
        try:
            _write_pidfile(cfg.pidfile)
        except Exception as e:
            logging.getLogger(__name__).warning("Could not write pidfile: %s", e)

    # Port guard
    if not cfg.force_run and _port_in_use(cfg.host, cfg.port):
        logging.getLogger(__name__).error("Port %s is already in use on %s. Use --force to ignore.", cfg.port, cfg.host)
        sys.exit(2)

    banner(cfg)
    sys.stdout.flush()

    try:
        # Import after env + logging are set
        from app import create_app
        app = create_app(cfg.config_path)

        # Trust reverse proxy if requested
        if ProxyFix and os.getenv("TRUST_PROXY", "0").lower() in {"1", "true", "yes"}:
            app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)  # type: ignore

        logging.getLogger(__name__).info("Health endpoint available at /healthz")
        print_routes(app, cfg.debug, cfg.routes_out)

        # Socket.IO singleton configured in extensions
        try:
            from app.extensions import socketio  # type: ignore
        except Exception:
            socketio = None  # type: ignore

        if cfg.open_browser and cfg.host in {"127.0.0.1", "0.0.0.0", "localhost"}:
            _open_browser_later(f"http://127.0.0.1:{cfg.port}")

        ssl_ctx = _ssl_ctx_from_env()

        if socketio is not None:
            mode = getattr(socketio, "async_mode", os.getenv("SOCKETIO_ASYNC_MODE", "threading"))
            logging.getLogger(__name__).info("Socket.IO async mode: %s", mode)
            socketio.run(
                app,
                host=cfg.host,
                port=cfg.port,
                debug=cfg.debug,
                use_reloader=cfg.use_reloader,
                allow_unsafe_werkzeug=cfg.debug,
                ssl_context=ssl_ctx,
            )
        else:
            app.run(
                host=cfg.host,
                port=cfg.port,
                debug=cfg.debug,
                use_reloader=cfg.use_reloader,
                ssl_context=ssl_ctx,
            )

    except Exception as exc:
        logging.error("❌ Failed to launch FundChamps app: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

