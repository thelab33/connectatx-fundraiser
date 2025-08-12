# app/jinja_filters.py
from __future__ import annotations

import re
from typing import Any, Iterable, List, Optional, Dict, Callable
from flask import Flask

__all__ = [
    "unique_by", "unique_by_name", "unique_sponsors", "unique_events",
    "dedupe", "commafy", "money", "slugify", "register_jinja_filters"
]

# ── helpers ──────────────────────────────────────────────────────────────────
def _get(item: Any, path: str) -> Any:
    """Safely fetch attr/key via dotted path (dicts or objects)."""
    cur = item
    for part in path.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            cur = getattr(cur, part, None)
    return cur

def _norm_str(v: Any) -> str:
    return str(v or "").strip().lower()

def _norm_time(t: Optional[str]) -> str:
    """
    Normalize time strings like '5 PM' -> '5:00 PM' (case-insensitive).
    Leaves full times (e.g., '5:15 PM') unchanged.
    """
    s = (t or "").strip()
    m = re.match(r"^(\d{1,2})\s*([ap]m)$", s, flags=re.I)
    return f"{m.group(1)}:00 {m.group(2).upper()}" if m else s

# ── core filters ─────────────────────────────────────────────────────────────
def unique_by(seq: Iterable[Any], attr: Optional[str] = None) -> List[Any]:
    """
    Stable de-dupe by a key/attribute (case-insensitive for strings).
    If attr is None, uses the item itself as the key.
    """
    seen = set()
    out: List[Any] = []
    for it in seq or []:
        key = it if attr is None else _get(it, attr)
        key = _norm_str(key) if isinstance(key, str) else key
        if key in seen:
            continue
        seen.add(key)
        out.append(it)
    return out

def unique_by_name(seq: Iterable[Any]) -> List[Any]:
    """Shortcut: de-dupe by 'name'."""
    return unique_by(seq, "name")

def unique_sponsors(seq: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """De-dupe sponsors by name (case-insensitive)."""
    return unique_by(seq, "name")

def unique_events(seq: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    De-dupe events by (date | time | name/opponent | location).
    Time is normalized so '5 PM' equals '5:00 PM'.
    """
    seen = set()
    out: List[Dict[str, Any]] = []
    for e in seq or []:
        date = _norm_str(_get(e, "date"))
        time = _norm_str(_norm_time(_get(e, "time")))
        name = _norm_str(_get(e, "name") or _get(e, "opponent"))
        loc  = _norm_str(_get(e, "location"))
        key = "|".join((date, time, name, loc))
        if key in seen:
            continue
        seen.add(key)
        out.append(e)
    return out

def dedupe(items: Iterable[Any]) -> List[Any]:
    """De-dupe simple lists; case-insensitive if items are strings."""
    seen = set()
    out: List[Any] = []
    for v in items or []:
        sig = v.lower() if isinstance(v, str) else v
        if sig in seen:
            continue
        seen.add(sig)
        out.append(v)
    return out

def commafy(val: Any) -> str:
    """Comma-format numbers; passthrough on non-numerics."""
    try:
        return f"{int(float(val)):,}"
    except Exception:
        return str(val or "")

def money(val: Any, currency: str = "USD") -> str:
    """Format as money (USD style)."""
    try:
        n = float(val or 0)
        return f"${n:,.0f}" if n.is_integer() else f"${n:,.2f}"
    except Exception:
        return "$0"

def slugify(s: Any) -> str:
    """URL-friendly slug."""
    s = str(s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

# ── registrar ────────────────────────────────────────────────────────────────
def register_jinja_filters(app: Flask) -> None:
    """
    Idempotently register filters. Existing filters aren’t overwritten.
    """
    env = app.jinja_env
    mapping: Dict[str, Callable[..., Any]] = {
        "unique_by": unique_by,
        "unique_by_name": unique_by_name,
        "unique_sponsors": unique_sponsors,
        "unique_events": unique_events,
        "dedupe": dedupe,
        "commafy": commafy,
        "money": money,
        "slugify": slugify,
        # friendly alias
        "comma": commafy,
    }
    for name, fn in mapping.items():
        env.filters.setdefault(name, fn)

