#!/usr/bin/env python3
"""
    🏆 FundChamps Flask SaaS Entrypoint — 2025 Ultra Pro Edition
    ─────────────────────────────────────────────────────────────
    ✨ Fastest way to launch your next-gen Flask + Socket.IO SaaS with real DX magic.
    • Colorful banners, structured logs, runtime diagnostics, and cloud/local savvy.
    • Designed for FundChamps: the most inspiring platform in youth sports.
"""

import os
import sys
import signal
import logging
import time
from datetime import datetime
from dotenv import load_dotenv

try:
    from flask_socketio import SocketIO
except ImportError:
    SocketIO = None

try:
    import eventlet
except ImportError:
    eventlet = None

# ──────────────────────────────────────────────────────────────
# 🛑 Graceful & Stylish Shutdown Handler
# ──────────────────────────────────────────────────────────────
def handle_shutdown(signum, frame):
    print("\033[1;33m🛑 FundChamps shutting down — signal received. Saving game and exiting gracefully!\033[0m")
    sys.exit(0)

# ──────────────────────────────────────────────────────────────
# 🏗️ Dynamic Config Path (env, prod, test, dev)
# ──────────────────────────────────────────────────────────────
def get_config_path():
    flask_config = os.getenv("FLASK_CONFIG")
    if flask_config:
        return flask_config
    env = os.getenv("FLASK_ENV", "production").lower()
    return {
        "development": "app.config.DevelopmentConfig",
        "testing":     "app.config.TestingConfig",
        "production":  "app.config.ProductionConfig",
    }.get(env, "app.config.ProductionConfig")

# ──────────────────────────────────────────────────────────────
# 🎨 Pro Logging: Color, Emoji, Format, Handler
# ──────────────────────────────────────────────────────────────
class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG':    '\033[1;34m',
        'INFO':     '\033[1;32m',
        'WARNING':  '\033[1;33m',
        'ERROR':    '\033[1;31m',
        'CRITICAL': '\033[1;41m',
        'RESET':    '\033[0m',
    }
    def format(self, record):
        level = record.levelname
        msg = super().format(record)
        return f"{self.COLORS.get(level, '')}{msg}{self.COLORS['RESET']}"

def setup_logging(debug):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColorFormatter("[%(asctime)s] %(levelname)s %(message)s"))
    logging.root.handlers = []
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.DEBUG if debug else logging.INFO)

# ──────────────────────────────────────────────────────────────
# 🚀 Main Entrypoint
# ──────────────────────────────────────────────────────────────
def main():
    load_dotenv()
    config_path = get_config_path()
    debug_flag = os.getenv("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "0.0.0.0")
    reloader = debug_flag
    setup_logging(debug_flag)

    # Graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    banner = f"""
\033[1;34m
╭─────────────────────────────────────────────────────────────╮
│           🏆  FundChamps Flask SaaS Launcher  🏀           │
╰─────────────────────────────────────────────────────────────╯
\033[0m"""
    print(banner)
    print(f"\033[1;33m✨ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Bootstrapping FundChamps platform...\033[0m")
    print("🔎 ENV:         ", os.getenv("FLASK_ENV", "production"))
    print("⚙️  CONFIG:      ", config_path)
    print(f"🌎 Host:Port:   {host}:{port}")
    print(f"🐍 Python:      {sys.version.split()[0]}")
    print(f"🧑‍💻 User:        {os.getenv('USER') or os.getenv('USERNAME')}")
    print(f"🕰️  Started at:  {time.strftime('%H:%M:%S')}")
    print("─────────────────────────────────────────────────────────────")

    # Show clickable URL for devs
    if host in ("127.0.0.1", "0.0.0.0", "localhost"):
        print(f"\033[1;36m💻 Local Dev:   http://127.0.0.1:{port}\033[0m")

    sys.stdout.flush()
    try:
        from app import create_app
        app = create_app(config_path)

        # Extra: Print blueprints and routes (elite DX for Flask devs)
        if debug_flag:
            print("\n\033[1;35m📦 Registered Blueprints:\033[0m", list(app.blueprints.keys()))
            print("\033[1;32m🔗 Routes:\033[0m")
            for rule in app.url_map.iter_rules():
                print(f"  \033[1;34m{rule}\033[0m → {rule.endpoint}")

        # --- SocketIO/WS ---
        if SocketIO:
            async_mode = 'eventlet' if eventlet else 'threading'
            socketio = SocketIO(app, async_mode=async_mode)
            socketio.run(
                app,
                host=host,
                port=port,
                debug=debug_flag,
                use_reloader=reloader,
                allow_unsafe_werkzeug=True,
            )
        else:
            app.run(
                host=host,
                port=port,
                debug=debug_flag,
                use_reloader=reloader,
            )

    except Exception as e:
        logging.error(f"❌ Failed to launch FundChamps app: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()

