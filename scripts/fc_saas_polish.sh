#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"

# --- 1) Models: Example (ctor, timestamps, soft-delete) ---
mkdir -p "$root/app/models"
cat > "$root/app/models/example.py" <<'PY'
from datetime import datetime
from app.extensions import db

class Example(db.Model):
    __tablename__ = "examples"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True, index=True)

    def __init__(self, name: str, description: str | None = None, **_):
        self.name = name
        self.description = description

    def soft_delete(self): self.deleted_at = datetime.utcnow()
    def restore(self): self.deleted_at = None
    @property
    def is_deleted(self) -> bool: return self.deleted_at is not None
PY

# --- 2) Helpers: milestone gap + emitter ---
cat > "$root/app/helpers.py" <<'PY'
from __future__ import annotations
from typing import Iterable, Tuple, Any

def _parse_money(v: Any) -> float:
    if v is None: return 0.0
    if isinstance(v, (int, float)): return float(v)
    s = str(v).strip().lower().replace(",", "").replace("_", "")
    k = 1.0
    if s.endswith("k"): k, s = 1000.0, s[:-1]
    if s.startswith("$"): s = s[1:]
    try: return float(s) * k
    except Exception: return 0.0

def _calc_next_milestone_gap(total: float, allocated: float, milestones: Iterable[dict]) -> Tuple[float, str]:
    total = _parse_money(total); allocated = _parse_money(allocated)
    ordered = [(_parse_money(m.get("cost", 0)), m.get("label", "")) for m in milestones]
    ordered.sort(key=lambda x: x[0])
    for cost, label in ordered:
        if allocated < cost:
            return (max(0.0, cost - allocated), label or "")
    if total > 0:
        return (max(0.0, total - allocated), "Goal")
    return (0.0, "Goal")

_seq_counter = 0
def emit_funds_update(*, raised, goal, sponsor_name=None, seq=None, socketio=None, fallback=None):
    global _seq_counter
    r = _parse_money(raised); g = max(0.0, _parse_money(goal))
    pct = (r / g * 100.0) if g else 0.0
    if seq is None:
        _seq_counter += 1; seq = _seq_counter
    payload = {"total": r, "goal": g, "percent": pct, "sponsor": sponsor_name or None, "seq": seq}
    if socketio is not None:
        try: socketio.emit("funds_update", payload, namespace="/"); return
        except Exception: pass
    if callable(fallback): return fallback(r, g, sponsor_name, seq)
PY

# --- 3) Payments service: map expected keys ---
mkdir -p "$root/app/services"
cat > "$root/app/services/payments.py" <<'PY'
import requests

class PaymentService:
    @staticmethod
    def create_paypal_order(data: dict) -> dict:
        resp = requests.post("https://api.paypal.com/v2/checkout/orders", json=data)
        resp.raise_for_status(); j = resp.json() or {}
        return {"order_id": j.get("id")}

    @staticmethod
    def capture_paypal_order(order_id: str) -> dict:
        resp = requests.post(f"https://api.paypal.com/v2/checkout/orders/{order_id}/capture")
        resp.raise_for_status(); j = resp.json() or {}
        status = j.get("status"); amount = None
        try:
            caps = j["purchase_units"][0]["payments"]["captures"][0]
            amount = float(caps["amount"]["value"])
        except Exception:
            pass
        out = {"status": status}
        if amount is not None: out["amount"] = amount
        return out
PY

# --- 4) CSP nonces: add {{ nonce_attr() }} to inline scripts (idempotent) ---
find "$root/app/templates" -type f -name "*.html" -print0 \
| xargs -0 sed -i 's/<script>/<script {{ nonce_attr() }}>/g'

# --- 5) A tiny a11y hint for the D hotkey (hero donate) ---
# Safe, only affects if found
sed -i '/id="hero-donate"/a <span id="donate-hotkey-hint" class="sr-only">Tip: press the D key to open Donate. This hotkey is disabled while typing.<\/span>' \
  "$root/app/templates/partials/hero_and_fundraiser.html" 2>/dev/null || true

# --- 6) Optional: PurgeCSS pass if available ---
if command -v npx >/dev/null 2>&1; then
  css="$root/app/static/css/app.min.css"
  [ -f "$css" ] && npx --yes purgecss \
    --css "$css" \
    --content "$root/app/templates/**/*.html" "$root/app/static/js/**/*.js" \
    --output "$root/app/static/css/" || true
fi

echo "✅ SAAS polish applied. Run: pytest -q"

