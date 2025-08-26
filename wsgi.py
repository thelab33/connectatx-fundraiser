# wsgi.py
import os
from app import create_app

cfg_path = os.getenv("FLASK_CONFIG", "config.ProductionConfig")
app = create_app(cfg_path)

if __name__ == "__main__":
    app.run()

