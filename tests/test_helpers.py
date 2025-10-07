# app/helpers.py
import re
from typing import Any, List, Dict, Optional

# internal sequence counter for emit_funds_update
_seq_counter = 0


# ───────────────────────────────────────────────
# Numeric parsing
# ───────────────────────────────────────────────
def _num(value: Any) -> float:
    """
    Parse flexible human-friendly numeric formats into float.
    Examples:
      123        → 123.0
      "1,200"    → 1200.0
      "$1_200"   → 1200.0
      "USD 1,200"→ 1200.0
      "(123.45)" → -123.45
      "10k"      → 10000.0
      "1.2m"     → 1200000.0
      "2b"       → 2000000000.0
      ""/None    → 0.0
    """
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)

    s = str(value).strip().lower()
    if not s:
        return 0.0

    # remove $, commas, underscores
    s = s.replace(",", "").replace("_", "").replace("$", "")
    if s.startswith("usd "):
        s = s[4:].strip()

    # handle parentheses as negative
    if s.startswith("(") and s.endswith(")"):
        try:
            return -float(s[1:-1])
        except ValueError:
            return 0.0

    # handle multipliers (k, m, b)
    multipliers = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}
    match = re.match(r"^([0-9.]+)([kmb])$", s)
    if match:
        num, suffix = match.groups()
        try:
            return float(num) * multipliers[suffix]
        except Exception:
            return 0.0

    # default float conversion
    try:
        return float(s)
    except ValueError:
        return 0.0


# ───────────────────────────────────────────────
# Percentage calculation
# ───────────────────────────────────────────────
def _pct(n: Any, d: Any) -> float:
    """
    Safe percentage calculation with 3-decimal precision.
    Returns 0.0 if denominator is zero or invalid.
    """
    n_val = _num(n)
    d_val = _num(d)
    if d_val == 0:
        return 0.0
    return round((n_val / d_val) * 100.0, 3)


# ───────────────────────────────────────────────
# Milestone gap calculation
# ───────────────────────────────────────────────
def _calc_next_milestone_gap(
    goal: Any, raised: Any, milestones: Optional[List[Dict[str, Any]]] = None
):
    """
    Given a fundraising goal, amount raised, and milestones,
    return the gap (float) and label (str) for the next target.

    - If fully funded, returns (0.0, "Fully funded").
    - If past all milestones but under goal, returns (gap, "Goal").
    """
    g = _num(goal)
    r = _num(raised)
    milestones = milestones or []

    # check milestones in order
    for m in milestones:
        cost = _num(m.get("cost"))
        if r < cost:
            return cost - r, m.get("label", "Goal")

    # fully funded?
    if r >= g:
        return 0.0, "Fully funded"

    return g - r, "Goal"


# ───────────────────────────────────────────────
# Emit funds update
# ───────────────────────────────────────────────
def emit_funds_update(
    raised: Any,
    goal: Any,
    sponsor_name: Optional[str] = None,
    socketio: Optional[Any] = None,
    seq: Optional[int] = None,
    fallback: Optional[callable] = None,
):
    """
    Emit a fundraising progress update via SocketIO (if provided).
    Falls back to a callback if given.

    - raised, goal: amounts
    - sponsor_name: optional sponsor label
    - seq: optional sequence override
    - socketio: a SocketIO instance with .emit(event, payload, broadcast=...)
    - fallback: function(r, g, s, seq) for non-socket testing
    """
    global _seq_counter
    if seq is None:
        _seq_counter += 1
        seq = _seq_counter

    payload = {
        "raised": _num(raised),
        "goal": _num(goal),
        "sponsor": sponsor_name,
        "seq": seq,
    }

    if socketio:
        socketio.emit("funds:update", payload, broadcast=True)
    elif fallback:
        fallback(payload["raised"], payload["goal"], sponsor_name, seq)

    return payload

