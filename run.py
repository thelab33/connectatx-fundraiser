#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

"""
FundChamps Launcher — Agency Elite (SV-Canonical)

Highlights
- Early dotenv load, config normalization (aliases: dev/test/prod)
- Clean logging (color | json | plain), safe for prod
- Port guard, PID file, optional browser open
- Optional Sentry + ProxyFix
- Socket.IO-aware (defaults to threading; flag/ENV override)
- Idempotent autopatch: injects Jinja NONCE into partials (regex-safe)
- Routes export for quick inspection / CI artifacts
"""

import os
import re
import sys
import json
import atexit
import socket
import signal
import logging
import argparse
import webbrowser
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, Iterable

from dotenv import load_dotenv

# ───────────────────────── Optional deps ─────────────────────────
try:
    from werkzeug.middleware.proxy_fix import ProxyFix  # type: ignore
except Exception:
    ProxyFix = None

try:
    import sentry_sdk  # type: ignore
    from sentry_sdk.integrations.flask import FlaskIntegration  # type: ignore
except Exception:
    sentry_sdk = None
    FlaskIntegration = None

# Default Socket.IO mode (app.extensions.socketio may override at runtime)
os.environ.setdefault("SOCKETIO_ASYNC_MODE", "threading")


# ───────────────────────── Autopatch (idempotent) ─────────────────────────
def autopatch(dirs: Iterable[Path] | None = None) -> None:
    """
    Safe preflight:
      • Inject nonce="{{ NONCE }}" into <script ...> that lack a nonce (Jinja partials)
      • Ensure app/static/css/input.css exists (use tailwind.min.css if present)

    Enable with --autopatch or FC_AUTOPATCH=1
    """
    print("\033[1;36m🔧 FundChamps Preflight Autopatcher...\033[0m")

    # where to scan for partials; overridable
    scan_dirs = list(dirs or [])
    if not scan_dirs:
        for d in ("app/templates/partials", "app/templates/embed"):
            p = Path(d)
            if p.exists():
                scan_dirs.append(p)

    # Regex: match <script ...> that does NOT already have nonce=
    script_rx = re.compile(r"<script(?![^>]*\bnonce=)([^>]*)>", re.IGNORECASE)

    def _inject_nonce(txt: str) -> str:
        return script_rx.sub(r'<script nonce="{{ NONCE }}"\1>', txt)

    for base in scan_dirs:
        for html in base.rglob("*.html"):
            try:
                raw = html.read_text(encoding="utf-8")
                patched = _inject_nonce(raw)
                if patched != raw:
                    html.write_text(patched, encoding="utf-8")
                    print(f"  ✅ NONCE injected → {html}")
            except Exception as e:
                print(f"  ⚠️  Skip {html}: {e}")

    css_dir = Path("app/static/css")
    if css_dir.exists():
        input_css = css_dir / "input.css"
        tw_min = css_dir / "tailwind.min.css"
        if not input_css.exists() and tw_min.exists():
            try:
                input_css.write_text(tw_min.read_text(encoding="utf-8"), encoding="utf-8")
                print("  ✅ Created input.css from tailwind.min.css")
            except Exception as e:
                print(f"  ⚠️  Could not create input.css: {e}")

    print("\033[1;32m✨ Autopatch complete.\033[0m")
    
    # inside autopatch() in run.py
import subprocess, sys
try:
    subprocess.run([sys.executable, "tools/patch_nonce_attrs.py", "--write"], check=True)
    print("✅ Normalized nonce attributes across templates")
except Exception as e:
    print(f"⚠️ Nonce patch skipped: {e}")


# ───────────────────────── Config normalize ─────────────────────────
def _config_dupes_warning() -> None:
    if Path("app/config.py").exists() and Path("app/config/config.py").exists():
        print(
            "\033[1;33m⚠️  Detected BOTH app/config.py and app/config/config.py.\n"
            "   Canonical path is \033[1mapp.config.*\033[0m. "
            "We will prefer the package (app/config/...). "
            "Consider removing \033[1mapp/config.py\033[0m to avoid ambiguity.\033[0m"
        )


def normalize_config_path(value: Optional[str]) -> str:
    """
    Returns canonical 'app.config.*' path.
    Accepts aliases: dev|test|prod|development|testing|production
    Also collapses 'app.config.config.*' → 'app.config.*' and 'config.*' → 'app.config.*'
    """
    if not value or not str(value).strip():
        value = os.getenv("FLASK_CONFIG") or ""

    if not value:
        env = (os.getenv("FLASK_ENV") or os.getenv("ENV") or "development").lower()
        alias = {
            "dev": "app.config.DevelopmentConfig",
            "development": "app.config.DevelopmentConfig",
            "test": "app.config.TestingConfig",
            "testing": "app.config.TestingConfig",
            "prod": "app.config.ProductionConfig",
            "production": "app.config.ProductionConfig",
        }
        return alias.get(env, "app.config.DevelopmentConfig")

    v = value.strip()
    if v.startswith("app.config.config."):
        v = v.replace("app.config.config.", "app.config.", 1)
    if v.startswith("config."):
        v = v.replace("config.", "app.config.", 1)

    key = v.lower()
    alias = {
        "dev": "app.config.DevelopmentConfig",
        "development": "app.config.DevelopmentConfig",
        "test": "app.config.TestingConfig",
        "testing": "app.config.TestingConfig",
        "prod": "app.config.ProductionConfig",
        "production": "app.config.ProductionConfig",
    }
    return alias.get(key, v)


# ───────────────────────── Logging ─────────────────────────
class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[1;41m",
        "RESET": "\033[0m",
    }

    def __init__(self, fmt: str = "%(asctime)s %(levelname)s %(message)s"):
        super().__init__(fmt=fmt, datefmt="%H:%M:%S")

    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        color = self.COLORS.get(record.levelname, "")
        return f"{color}{base}{self.COLORS['RESET']}"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging(debug: bool, style: str = "color") -> None:
    """
    style: 'color' | 'json' | 'plain'
    env override: LOG_STYLE
    """
    style = (os.getenv("LOG_STYLE") or style or "color").lower()
    handler = logging.StreamHandler(sys.stdout)

    if style == "json":
        handler.setFormatter(JsonFormatter())
    elif style == "plain":
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S"))
    else:
        # auto fallback to plain if stdout isn't a TTY
        if not sys.stdout.isatty():
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S"))
        else:
            handler.setFormatter(ColorFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if debug else logging.INFO)


# ───────────────────────── CLI model ─────────────────────────
@dataclass(frozen=True)
class RunnerConfig:
    host: str
    port: int
    debug: bool
    use_reloader: bool
    open_browser: bool
    log_style: str
    pidfile: Optional[Path]
    routes_out: Optional[Path]
    force_run: bool
    async_mode: str
    config_path: str
    do_autopatch: bool


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run the FundChamps Flask app.")
    p.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    p.add_argument("--port", type=int, default=int(os.getenv("PORT", "5000")))
    try:
        BoolOpt = argparse.BooleanOptionalAction  # py3.9+
    except Exception:
        BoolOpt = None
    debug_env = os.getenv("FLASK_DEBUG", "0").lower() in {"1", "true", "yes"}
    p.add_argument("--debug", default=debug_env, action=BoolOpt or "store_true")
    p.add_argument("--no-reload", action="store_true")
    p.add_argument("--log-style", choices=["color", "json", "plain"], default=os.getenv("LOG_STYLE", "color"))
    p.add_argument("--open-browser", action="store_true")
    p.add_argument("--pidfile", type=Path)
    p.add_argument("--routes-out", type=Path)
    p.add_argument("--force", dest="force_run", action="store_true")
    p.add_argument("--async-mode",
                  default=os.getenv("SOCKETIO_ASYNC_MODE", "threading"),
                  choices=["threading", "eventlet", "gevent", "gevent_uwsgi"])
    p.add_argument("--config", help="Explicit FLASK_CONFIG path or alias")
    p.add_argument("--autopatch", action="store_true",
                  help="Run safe preflight autopatcher (also FC_AUTOPATCH=1)")
    return p.parse_args()


def make_runner_config() -> RunnerConfig:
    a = parse_args()
    cfg_path = normalize_config_path(a.config or os.getenv("FLASK_CONFIG"))
    return RunnerConfig(
        host=str(a.host),
        port=int(a.port),
        debug=bool(getattr(a, "debug", False)),
        use_reloader=(bool(getattr(a, "debug", False)) and not a.no_reload),
        open_browser=bool(a.open_browser),
        log_style=str(a.log_style or "color"),
        pidfile=a.pidfile,
        routes_out=a.routes_out,
        force_run=bool(a.force_run),
        async_mode=str(a.async_mode or "threading"),
        config_path=cfg_path,
        do_autopatch=bool(a.autopatch or os.getenv("FC_AUTOPATCH", "0").lower() in {"1", "true", "yes"}),
    )


# ───────────────────────── Helpers ─────────────────────────
def _ssl_ctx_from_env() -> Optional[Tuple[str, str]]:
    cert, key = os.getenv("SSL_CERTFILE"), os.getenv("SSL_KEYFILE")
    return (cert, key) if cert and key else None


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.35)
        return s.connect_ex((host, port)) == 0


def _write_pidfile(pidfile: Path) -> None:
    pidfile.write_text(str(os.getpid()), encoding="utf-8")
    atexit.register(lambda: pidfile.exists() and pidfile.unlink(missing_ok=True))


def _open_browser_later(url: str, delay: float = 0.6) -> None:
    import threading
    threading.Timer(delay, lambda: webbrowser.open_new_tab(url)).start()


def banner(cfg: RunnerConfig) -> None:
    print(
        "\n\033[1;34m╭─────────────────────────────────────────────────────────────╮\n"
        "│           🏆  FundChamps Flask SaaS Launcher  🏀           │\n"
        "╰─────────────────────────────────────────────────────────────╯\033[0m"
    )
    print(f"\033[1;33m✨ {datetime.now():%Y-%m-%d %H:%M:%S}: Bootstrapping FundChamps...\033[0m")
    print(f"🔎 ENV:        {os.getenv('FLASK_ENV', os.getenv('ENV', 'development'))}")
    print(f"⚙️  CONFIG:     {cfg.config_path}")
    print(f"🌎 Host:Port:  {cfg.host}:{cfg.port}")
    print(f"🐍 Python:     {sys.version.split()[0]}")
    if cfg.host in {"127.0.0.1", "0.0.0.0", "localhost"}:
        print(f"\033[1;36m💻 Local:      http://127.0.0.1:{cfg.port}\033[0m")


def print_routes(app, debug: bool, routes_out: Optional[Path] = None) -> None:
    rows = [
        {
            "rule": str(rule),
            "endpoint": rule.endpoint,
            "methods": sorted((rule.methods or set()) - {"HEAD", "OPTIONS"}),
        }
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r))
    ]
    if routes_out:
        try:
            routes_out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
            print(f"\n\033[1;35m📝 Routes written to:\033[0m {routes_out}")
        except Exception as e:
            logging.warning("Failed to write routes file: %s", e)

    if debug:
        print("\n\033[1;32m🔗 Routes:\033[0m")
        for r in rows:
            methods = ",".join(r["methods"])
            print(f"  \033[1;34m{r['rule']}\033[0m → {r['endpoint']} ({methods})")


# ───────────────────────── Env shims (Stripe keys, etc.) ─────────────────────
def _shim_env_aliases() -> None:
    if not os.getenv("STRIPE_SECRET_KEY") and os.getenv("STRIPE_API_KEY"):
        os.environ["STRIPE_SECRET_KEY"] = os.getenv("STRIPE_API_KEY", "")
    if not os.getenv("STRIPE_PUBLIC_KEY") and os.getenv("STRIPE_PUBLISHABLE_KEY"):
        os.environ["STRIPE_PUBLIC_KEY"] = os.getenv("STRIPE_PUBLISHABLE_KEY", "")


# ───────────────────────── Build app for Flask CLI (optional) ─────────────────
def build_app():
    """Allows: `flask --app run:build_app routes`."""
    from app import create_app  # defer import until after dotenv/env
    return create_app(normalize_config_path(os.getenv("FLASK_CONFIG")))


# Export `app` for `flask --app run:app run` convenience (guarded)
_app_should_export = os.getenv("FC_EXPORT_APP", "1").lower() in {"1", "true", "yes"}
if _app_should_export:
    try:
        load_dotenv()
        app = build_app()  # noqa: F401
    except Exception:
        app = None  # type: ignore


# ───────────────────────── Main ─────────────────────────
def main() -> None:
    load_dotenv()
    _config_dupes_warning()
    _shim_env_aliases()

    cfg = make_runner_config()
    os.environ["SOCKETIO_ASYNC_MODE"] = cfg.async_mode
    setup_logging(cfg.debug, cfg.log_style)

    # Signals (graceful exit)
    for sig in ("SIGINT", "SIGTERM"):
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), lambda *_: sys.exit(0))

    # Autopatch (opt-in)
    if cfg.do_autopatch:
        autopatch()

    # Sentry (optional)
    dsn = os.getenv("SENTRY_DSN")
    if dsn and sentry_sdk and FlaskIntegration:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration()],
            traces_sample_rate=float(os.getenv("SENTRY_TRACES", "0.0")),
        )
        logging.info("Sentry initialized")

    if cfg.pidfile:
        try:
            _write_pidfile(cfg.pidfile)
        except Exception as e:
            logging.warning("Could not write pidfile: %s", e)

    if not cfg.force_run and _port_in_use(cfg.host, cfg.port):
        logging.error("Port %s already in use on %s. Use --force to ignore.", cfg.port, cfg.host)
        sys.exit(2)

    banner(cfg)
    sys.stdout.flush()

    try:
        from app import create_app
        flask_app = create_app(cfg.config_path)

        # Respect proxied headers if enabled
        if ProxyFix and os.getenv("TRUST_PROXY", "0").lower() in {"1", "true", "yes"}:
            flask_app.wsgi_app = ProxyFix(  # type: ignore[assignment]
                flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1
            )

        if cfg.open_browser and cfg.host in {"127.0.0.1", "0.0.0.0", "localhost"}:
            _open_browser_later(f"http://127.0.0.1:{cfg.port}")

        print_routes(flask_app, cfg.debug, cfg.routes_out)

        # Prefer Socket.IO if available
        try:
            from app.extensions import socketio  # type: ignore
        except Exception:
            socketio = None  # type: ignore

        ssl_ctx = _ssl_ctx_from_env()
        run_kwargs = dict(host=cfg.host, port=cfg.port, debug=cfg.debug,
                          use_reloader=cfg.use_reloader, ssl_context=ssl_ctx)

        if socketio:
            logging.info("Socket.IO async mode: %s", getattr(socketio, "async_mode", cfg.async_mode))
            socketio.run(flask_app, allow_unsafe_werkzeug=cfg.debug, **run_kwargs)
        else:
            flask_app.run(**run_kwargs)

    except Exception as exc:
        logging.error("❌ Failed to launch FundChamps app: %s", exc, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

