#!/usr/bin/env bash
set -euo pipefail
if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "Waiting for database..."
  python - <<'PY'
import os, time, socket
from urllib.parse import urlparse
u=urlparse(os.environ.get("DATABASE_URL",""))
host=u.hostname or "db"; port=u.port or (5432 if "postgres" in (u.scheme or "") else 3306)
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print("DB reachable"); break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit("Database not reachable")
PY
fi
mkdir -p /app/app/data
flask db upgrade || true
exec "$@"
