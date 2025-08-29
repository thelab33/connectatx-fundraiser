# wsgi.py
import os
from app import create_app

# Ensure canonical path (works even if someone left old values)
cfg = os.getenv("FLASK_CONFIG", "")
if cfg.startswith("app.config.config."):
    cfg = cfg.replace("app.config.config.", "app.config.")
os.environ["FLASK_CONFIG"] = cfg or "app.config.ProductionConfig"

application = create_app(os.environ["FLASK_CONFIG"])

