#!/usr/bin/env python3
from __future__ import annotations

"""
FundChamps Launcher — SV-Elite “No-Dupes” Edition
- Loads dotenv early
- Canonicalizes FLASK_CONFIG → app.config.(Development|Testing|Production)Config
- Accepts aliases: dev/test/prod + legacy 'app.config.config.*'
- Safe logging (color or JSON)
- Port guard, PID file, optional browser open
- Optional Sentry + ProxyFix
- Socket.IO aware (default: threading; override --async-mode)
- Minimal, idempotent autopatch (nonce-inject only; gated)
"""

import os
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
from typing import Optional, Tuple

from dotenv import load_dotenv

# ── Optional deps
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

# Default Socket.IO mode
os.environ.setdefault("SOCKETIO_ASYNC_MODE", "threading")

# ───────────────────────── Autopatch (minimal, gated) ─────────────────────────
def autopatch() -> None:
    """
    Minimal, safe preflight:
      - inject NONCE on <script> missing it (partials only), idempotent
      - ensure static/css/input.css exists -> tailwind.min.css
    Enable with --autopatch or FC_AUTOPATCH=1
    """
    print("\033[1;36m🔧 FundChamps Preflight Autopatcher...\033[0m")
    base = Path("app/templates/partials")
    if base.exists():
        for html in base.rglob("*.html"):
            try:
                txt = html.read_text(encoding="utf-8")
                if "<script" in txt and 'nonce="{{ NONCE }}"' not in txt:
                    patched = txt.replace("<script>", '<script nonce="{{ NONCE }}">')
                    if patched != txt:
                        html.write_text(patched, encoding="utf-8")
                        print(f"✅ NONCE injected → {html}")
            except Exception as e:
                print(f"⚠️  Skipped {html}: {e}")

    css_dir = Path("app/static/css")
    if css_dir.exists():
        g = css_dir / "input.css"
        t = css_dir / "tailwind.min.css"
        if not g.exists() and t.exists():
            try:
                g.symlink_to(t); print("✅ Symlinked input.css → tailwind.min.css")
            except Exception:
                try:
                    g.write_text(t.read_text(encoding="utf-8"), encoding="utf-8")
                    print("✅ Copied tailwind.min.css → input.css")
                except Exception as e:
                    print(f"⚠️  Could not create input.css: {e}")

    print("\033[1;32m✨ Autopatch complete.\033[0m")

# ───────────────────────── Config normalize ─────────────────────────
def _config_dupes_warning() -> None:
    # If both app/config.py AND app/config/config.py exist, warn (we always import 'app.config')
    mod_file = Path("app/config.py")
    pkg_file = Path("app/config/config.py")
    if mod_file.exists() and pkg_file.exists():
        print(
            "\033[1;33m⚠️  Detected BOTH app/config.py and app/config/config.py.\n"
            "   Canonical path is \033[1mapp.config.*\033[0m. "
            "We will prefer the package (app/config/...). "
            "Consider removing \033[1mapp/config.py\033[0m to avoid ambiguity.\033[0m"
        )

def normalize_config_path(value: Optional[str]) -> str:
    """
    Returns canonical 'app.config.*' path.
    Accepts:
      - None (uses FLASK_CONFIG or ENV alias)
      - 'app.config.config.DevelopmentConfig' (legacy) → 'app.config.DevelopmentConfig'
      - aliases: dev|test|prod|development|testing|production
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
    if v.startswith("app.config.config."):  # collapse nested package
        v = v.replace("app.config.config.", "app.config.")
    lower = v.lower()
    alias = {
        "dev": "app.config.DevelopmentConfig",
        "development": "app.config.DevelopmentConfig",
        "test": "app.config.TestingConfig",
        "testing": "app.config.TestingConfig",
        "prod": "app.config.ProductionConfig",
        "production": "app.config.ProductionConfig",
    }
    return alias.get(lower, v)

# ───────────────────────── Logging ─────────────────────────
class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[1;34m",
        "INFO": "\033[1;32m",
        "WARNING": "\033[1;33m",
        "ERROR": "\033[1;31m",
        "CRITICAL": "\033[1;41m",
        "RESET": "\033[0m",
    }
    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        return f"{self.COLORS.get(record.levelname, '')}{msg}{self.COLORS['RESET']}"

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

def setup_logging(debug: bool, json_mode: bool) -> None:
    handler = logging.StreamHandler(sys.stdout)
    fmt = "[%(asctime)s] %(levelname)s %(message)s"
    handler.setFormatter(JsonFormatter() if json_mode else ColorFormatter(fmt))
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
    log_json: bool
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
    p.add_argument("--log-json", action="store_true")
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
    args = parse_args()
    cfg_path = normalize_config_path(args.config or os.getenv("FLASK_CONFIG"))
    return RunnerConfig(
        host=str(args.host),
        port=int(args.port),
        debug=bool(getattr(args, "debug", False)),
        use_reloader=(bool(getattr(args, "debug", False)) and not args.no_reload),
        open_browser=bool(args.open_browser),
        log_json=bool(args.log_json),
        pidfile=args.pidfile,
        routes_out=args.routes_out,
        force_run=bool(args.force_run),
        async_mode=str(args.async_mode or "threading"),
        config_path=cfg_path,
        do_autopatch=bool(args.autopatch or os.getenv("FC_AUTOPATCH", "0").lower() in {"1","true","yes"}),
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
    print("""
\033[1;34m
╭─────────────────────────────────────────────────────────────╮
│           🏆  FundChamps Flask SaaS Launcher  🏀           │
╰─────────────────────────────────────────────────────────────╯
\033[0m""")
    print(f"\033[1;33m✨ {datetime.now():%Y-%m-%d %H:%M:%S}: Bootstrapping FundChamps...\033[0m")
    print(f"🔎 ENV:        {os.getenv('FLASK_ENV', os.getenv('ENV', 'development'))}")
    print(f"⚙️  CONFIG:     {cfg.config_path}")
    print(f"🌎 Host:Port:  {cfg.host}:{cfg.port}")
    print(f"🐍 Python:     {sys.version.split()[0]}")
    if cfg.host in {"127.0.0.1", "0.0.0.0", "localhost"}:
        print(f"\033[1;36m💻 Local:      http://127.0.0.1:{cfg.port}\033[0m")

def print_routes(app, debug: bool, routes_out: Optional[Path] = None) -> None:
    rows = [
        {"rule": str(rule), "endpoint": rule.endpoint,
         "methods": sorted((rule.methods or set()) - {"HEAD", "OPTIONS"})}
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
            print(f"  \033[1;34m{r['rule']}\033[0m → {r['endpoint']} ({','.join(r['methods'])})")

# ───────────────────────── Env shims (Stripe keys, etc.) ─────────────────────
def _shim_env_aliases() -> None:
    # Secret key: STRIPE_API_KEY → STRIPE_SECRET_KEY (if needed)
    if not os.getenv("STRIPE_SECRET_KEY") and os.getenv("STRIPE_API_KEY"):
        os.environ["STRIPE_SECRET_KEY"] = os.getenv("STRIPE_API_KEY", "")
    # Publishable key: STRIPE_PUBLISHABLE_KEY → STRIPE_PUBLIC_KEY (if needed)
    if not os.getenv("STRIPE_PUBLIC_KEY") and os.getenv("STRIPE_PUBLISHABLE_KEY"):
        os.environ["STRIPE_PUBLIC_KEY"] = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

# ───────────────────────── Main ─────────────────────────
def main() -> None:
    load_dotenv()
    _config_dupes_warning()
    _shim_env_aliases()

    cfg = make_runner_config()
    os.environ["SOCKETIO_ASYNC_MODE"] = cfg.async_mode
    setup_logging(cfg.debug, cfg.log_json)

    # Signals
    for sig in ("SIGINT", "SIGTERM"):
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), lambda *_: sys.exit(0))

    # Autopatch (off by default)
    if cfg.do_autopatch:
        autopatch()

    # Sentry (optional)
    dsn = os.getenv("SENTRY_DSN")
    if dsn and sentry_sdk and FlaskIntegration:
        sentry_sdk.init(dsn=dsn, integrations=[FlaskIntegration()],
                        traces_sample_rate=float(os.getenv("SENTRY_TRACES", "0.0")))
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

        if ProxyFix and os.getenv("TRUST_PROXY", "0").lower() in {"1", "true", "yes"}:
            flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

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

