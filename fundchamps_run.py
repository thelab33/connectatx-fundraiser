#!/usr/bin/env python3
from __future__ import annotations

"""
FundChamps Launcher
──────────────────────────────────────────────────────────────
- Loads env early (dotenv)
- Safe logging (color or JSON)
- Port guard, PID file, optional browser open
- Optional Sentry + ProxyFix
- Socket.IO aware (default: threading; override with --async-mode)
"""

import os
import sys
import json
import time
import socket
import signal
import atexit
import logging
import webbrowser
import argparse
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple

from dotenv import load_dotenv
# ── FundChamps Preflight Autopatcher ─────────────────────────────────────────
import re

def autopatch() -> None:
    print("\033[1;36m🔧 Running FundChamps Preflight Autopatcher...\033[0m")

    # 1. Fix inline Jinja comment in index.html
    idx = Path("app/templates/index.html")
    if idx.exists():
        txt = idx.read_text(encoding="utf-8")
        patched = re.sub(r'"newsletter":\s*true,.*$', '"newsletter":       true,', txt, flags=re.M)
        if txt != patched:
            idx.write_text(patched, encoding="utf-8")
            print("✅ Fixed inline Jinja comment in index.html")

    # 2. Deduplicate IDs (fc-*) by suffixing team.id
    for html in Path("app/templates").rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        patched = re.sub(r'id="(fc-[a-z0-9-]+)"', r'id="\1-{{ team.id|default(\"X\") }}"', text)
        if text != patched:
            html.write_text(patched, encoding="utf-8")
            print(f"✅ Patched duplicate IDs in {html}")

    # 3. Add CSP nonces to <script> tags
    for html in Path("app/templates/partials").rglob("*.html"):
        text = html.read_text(encoding="utf-8")
        if "<script>" in text and 'nonce="{{ NONCE }}"' not in text:
            patched = text.replace("<script>", '<script nonce="{{ NONCE }}">')
            html.write_text(patched, encoding="utf-8")
            print(f"✅ Injected NONCE in {html}")

    # 4. Ensure Stripe key fallback
    env_path = Path(".env")
    if env_path.exists():
        env_txt = env_path.read_text()
    else:
        env_txt = ""
    if "STRIPE_API_KEY" not in env_txt:
        with env_path.open("a") as f:
            f.write("\nSTRIPE_API_KEY=sk_test_dummy\n")
        print("✅ Added dummy STRIPE_API_KEY to .env")

    # 5. Symlink or copy globals.css if missing
    css_dir = Path("app/static/css")
    if css_dir.exists():
        g = css_dir / "globals.css"
        t = css_dir / "tailwind.min.css"
        if not g.exists() and t.exists():
            try:
                g.symlink_to(t)
                print("✅ Symlinked globals.css → tailwind.min.css")
            except Exception:
                g.write_text(t.read_text())
                print("✅ Copied tailwind.min.css → globals.css")

    print("\033[1;32m✨ Autopatch complete.\033[0m")

# ── Defaults ──────────────────────────────────────────────────────────────────
os.environ.setdefault("SOCKETIO_ASYNC_MODE", "threading")

# Optional dependencies
try:
    from werkzeug.middleware.proxy_fix import ProxyFix  # type: ignore
except ImportError:
    ProxyFix = None

try:
    import sentry_sdk  # type: ignore
    from sentry_sdk.integrations.flask import FlaskIntegration  # type: ignore
except ImportError:
    sentry_sdk = None
    FlaskIntegration = None

# ── Config Model ──────────────────────────────────────────────────────────────
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
    async_mode: str

# ── Logging Setup ─────────────────────────────────────────────────────────────
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
    handler.setFormatter(JsonFormatter() if json_mode else ColorFormatter("[%(asctime)s] %(levelname)s %(message)s"))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if debug else logging.INFO)

# ── Helpers ───────────────────────────────────────────────────────────────────
def resolve_config_path() -> str:
    if env_cfg := os.getenv("FLASK_CONFIG"):
        return env_cfg
    env = (os.getenv("FLASK_ENV") or os.getenv("ENV") or "production").lower()
    return {
        "development": "app.config.DevelopmentConfig",
        "testing": "app.config.TestingConfig",
        "production": "app.config.ProductionConfig",
    }.get(env, "app.config.ProductionConfig")

def _ssl_ctx_from_env() -> Optional[Tuple[str, str]]:
    cert, key = os.getenv("SSL_CERTFILE"), os.getenv("SSL_KEYFILE")
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
    threading.Timer(delay, lambda: webbrowser.open_new_tab(url)).start()

def banner(cfg: RunnerConfig) -> None:
    print("""
\033[1;34m
╭─────────────────────────────────────────────────────────────╮
│           🏆  FundChamps Flask SaaS Launcher  🏀           │
╰─────────────────────────────────────────────────────────────╯
\033[0m""")
    print(f"\033[1;33m✨ {datetime.now():%Y-%m-%d %H:%M:%S}: Bootstrapping FundChamps platform...\033[0m")
    print(f"🔎 ENV:           {os.getenv('FLASK_ENV', os.getenv('ENV', 'production'))}")
    print(f"⚙️  CONFIG:        {cfg.config_path}")
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
        action = argparse.BooleanOptionalAction
    except AttributeError:
        action = None
    p.add_argument("--debug", default=debug_env, action=action or "store_true")
    p.add_argument("--no-reload", action="store_true")
    p.add_argument("--log-json", action="store_true")
    p.add_argument("--open-browser", action="store_true")
    p.add_argument("--pidfile", type=Path)
    p.add_argument("--routes-out", type=Path)
    p.add_argument("--force", dest="force_run", action="store_true")
    p.add_argument("--async-mode", default=os.getenv("SOCKETIO_ASYNC_MODE", "threading"),
                   choices=["threading", "eventlet", "gevent", "gevent_uwsgi"])
    return p.parse_args()

def make_runner_config() -> RunnerConfig:
    args = parse_args()
    return RunnerConfig(
        host=args.host,
        port=args.port,
        debug=bool(getattr(args, "debug", False)),
        config_path=resolve_config_path(),
        use_reloader=(bool(getattr(args, "debug", False)) and not args.no_reload),
        log_json=bool(args.log_json),
        open_browser=bool(args.open_browser),
        pidfile=args.pidfile,
        routes_out=args.routes_out,
        force_run=bool(args.force_run),
        async_mode=str(args.async_mode or "threading"),
    )

def graceful_exit(signum, frame) -> None:
    print("\033[1;33m🛑 FundChamps shutting down — signal received.\033[0m")
    sys.exit(0)

def print_routes(app, debug: bool, routes_out: Optional[Path] = None) -> None:
    rows = [{"rule": str(rule), "endpoint": rule.endpoint, "methods": sorted(rule.methods or [])}
            for rule in sorted(app.url_map.iter_rules(), key=lambda r: str(r))]
    if routes_out:
        try:
            routes_out.write_text(json.dumps(rows, indent=2), encoding="utf-8")
            print(f"\n\033[1;35m📝 Routes written to:\033[0m {routes_out}")
        except Exception as e:
            logging.warning("Failed to write routes file: %s", e)
    if debug:
        print("\n\033[1;35m📦 Registered Blueprints:\033[0m", list(app.blueprints.keys()))
        print("\033[1;32m🔗 Routes:\033[0m")
        for r in rows:
            print(f"  \033[1;34m{r['rule']}\033[0m → {r['endpoint']}  ({','.join(r['methods'])})")

# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    load_dotenv()
    cfg = make_runner_config()
    os.environ["SOCKETIO_ASYNC_MODE"] = cfg.async_mode
    setup_logging(cfg.debug, cfg.log_json)

    for sig in ("SIGINT", "SIGTERM"):
        if hasattr(signal, sig):
            signal.signal(getattr(signal, sig), graceful_exit)

    if (dsn := os.getenv("SENTRY_DSN")) and sentry_sdk and FlaskIntegration:
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
        app = create_app(cfg.config_path)

        # Early warning if main_bp missing
        if "main_bp" not in app.blueprints:
            logging.warning("⚠️  main_bp blueprint not loaded — '/' will not be available.")

        if ProxyFix and os.getenv("TRUST_PROXY", "0").lower() in {"1", "true", "yes"}:
            app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

        logging.info("Health endpoint available at /healthz")
        print_routes(app, cfg.debug, cfg.routes_out)

        from app.extensions import socketio  # type: ignore
        if cfg.open_browser and cfg.host in {"127.0.0.1", "0.0.0.0", "localhost"}:
            _open_browser_later(f"http://127.0.0.1:{cfg.port}")

        ssl_ctx = _ssl_ctx_from_env()
        run_kwargs = dict(host=cfg.host, port=cfg.port, debug=cfg.debug,
                          use_reloader=cfg.use_reloader, ssl_context=ssl_ctx)

        if socketio:
            logging.info("Socket.IO async mode: %s", getattr(socketio, "async_mode", cfg.async_mode))
            socketio.run(app, allow_unsafe_werkzeug=cfg.debug, **run_kwargs)
        else:
            app.run(**run_kwargs)

    except Exception as exc:
        logging.error("❌ Failed to launch FundChamps app: %s", exc, exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

