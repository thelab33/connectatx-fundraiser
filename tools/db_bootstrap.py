# tools/db_bootstrap.py
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))  # <-- add this

from app import create_app
from app.extensions import db
from sqlalchemy.exc import OperationalError

def bootstrap():
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
        except OperationalError as e:
            msg = str(e).lower()
            if "ix_donations_email" in msg and "already exists" in msg:
                with db.engine.begin() as conn:
                    conn.exec_driver_sql("DROP INDEX IF EXISTS ix_donations_email;")
                db.create_all()
            else:
                raise
        print("✅ DB bootstrap complete")

if __name__ == "__main__":
    bootstrap()

