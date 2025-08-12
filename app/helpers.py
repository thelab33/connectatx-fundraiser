# app/helpers.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import math

# ─────────────────────────────────────────────────────────────
# Small utility helpers
# ─────────────────────────────────────────────────────────────

def _num(v: Any, default: float = 0.0) -> float:
    """Parse numbers from int/float/str like '10k'/'1.2m', else default."""
    if v is None:
        return default
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip().replace(',', '')
    mult = 1.0
    if s.lower().endswith('k'):
        mult, s = 1_000.0, s[:-1]
    elif s.lower().endswith('m'):
        mult, s = 1_000_000.0, s[:-1]
    try:
        return float(s) * mult
    except Exception:
        return default

def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))

def _pct(n: float, d: float) -> float:
    return round((n / d * 100.0), 1) if d else 0.0

def _money_i(n: float) -> int:
    """Whole-dollar int for display math (server-side formatting happens in templates)."""
    return int(round(float(n or 0.0)))

def _as_players(lst: Any) -> List[Dict[str, str]]:
    out: List[Dict[str, str]] = []
    for it in (lst or []):
        if isinstance(it, dict) and it.get("name"):
            out.append({"name": str(it["name"]), "role": str(it.get("role", ""))})
        elif isinstance(it, str) and it.strip():
            out.append({"name": it.strip(), "role": ""})
    return out

def _normalize_stats(stats: Any) -> List[Dict[str, Any]]:
    """Ensure each stat is {'label': str, 'value': number|str}."""
    norm: List[Dict[str, Any]] = []
    for s in (stats or []):
        if not isinstance(s, dict):
            continue
        label = str(s.get("label", "") or "").strip()
        if not label:
            continue
        value = s.get("value", 0)
        norm.append({"label": label, "value": value})
    return norm

# ─────────────────────────────────────────────────────────────
# Public helpers used by views/templates
# (kept names for backwards-compatibility)
# ─────────────────────────────────────────────────────────────

def _generate_about_section(team: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the About section with safe fallbacks.
    Accepts optional:
      - team['about_heading'], team['about_text'] or team['about'] (list[str])
      - team['players'] -> [{'name','role'}, ...]
      - team['cta_label']
    """
    team_name = team.get("team_name", "Our Team")
    about_list = team.get("about") or []
    about_text = team.get("about_text") or " ".join([p for p in about_list if isinstance(p, str)]) or \
                 "We are a community-powered youth program building character on and off the court."

    return {
        "heading": team.get("about_heading", f"About {team_name}"),
        "text": about_text,
        "players": _as_players(team.get("players")),
        "cta": team.get("cta_label", "Join Us"),
    }

def _generate_impact_stats(team: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Return normalized impact stats, with a solid default if missing.
    """
    stats = _normalize_stats(team.get("impact_stats"))
    return stats or [{"label": "Players Enrolled", "value": 16}]

def _generate_challenge_section(team: Dict[str, Any], impact_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Build a succinct challenge section. Re-uses impact stats as 'metrics'.
    """
    return {
        "heading": team.get("challenge_heading", "The Challenge"),
        "text": team.get("challenge_text", "Gym time, travel costs, and gear add up fast for volunteer families."),
        "metrics": impact_stats[:4],
    }

def _generate_mission_section(team: Dict[str, Any], impact_stats: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Mission copy with optional stats accompaniment.
    """
    team_name = team.get("team_name", "Our Team")
    return {
        "heading": team.get("mission_heading", "Our Mission"),
        "text": team.get("mission_text",
                         f"{team_name} builds teamwork, respect, and championship character—"
                         "in the classroom and on the court."),
        "stats": impact_stats[:4],
    }

def _prepare_stats(team: Dict[str, Any], raised: float, goal: Optional[float], percent_raised: float) -> Dict[str, Any]:
    """
    Normalize fundraiser metrics and add derived values for templates.
    """
    r = _num(raised)
    g = _num(goal or team.get("fundraising_goal", 0))
    p = percent_raised if percent_raised is not None else _pct(r, g)
    remaining = max(0, g - r)

    return {
        "raised": r,
        "goal": g,
        "percent": _clamp(p, 0, 100),
        "remaining": remaining,
        "raised_int": _money_i(r),
        "goal_int": _money_i(g),
        "remaining_int": _money_i(remaining),
    }

# ─────────────────────────────────────────────────────────────
# Impact Lockers (Buckets) — smarter allocator
# ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Bucket:
    key: str
    label: str
    details: str
    total: float
    allocated: float
    percent: float
    next_gap: float              # $ to lock the next milestone (or remaining total if none)
    next_label: str              # label of the upcoming milestone
    milestones: List[Dict[str, Any]]
    emoji: str
    locked: bool

def _calc_next_milestone_gap(total: float, allocated: float, milestones: List[Dict[str, Any]]) -> Tuple[float, str]:
    """
    Given a total and list of milestone 'cost' items, compute:
      - the minimal $ gap to reach the next cumulative milestone
      - the milestone label
    Falls back to remaining total if milestones are missing/exhausted.
    """
    remaining = max(0.0, total - allocated)
    if total <= 0 or remaining <= 0:
        return 0.0, "Fully funded"

    # Build cumulative checkpoints: [{"label":..., "cum":...}, ...]
    cum = 0.0
    checkpoints: List[Tuple[float, str]] = []
    for m in milestones or []:
        cost = _num(m.get("cost"), 0.0)
        if cost <= 0:
            continue
        cum += cost
        checkpoints.append((cum, str(m.get("label") or "Milestone")))

    # If we have no checkpoints, the next gap is simply the remaining total.
    if not checkpoints:
        return remaining, "Goal"

    # Find the first cumulative target above allocated.
    for cum_target, label in checkpoints:
        if allocated < cum_target:
            return max(0.0, cum_target - allocated), label

    # Past all milestones: use the remaining total.
    return remaining, "Goal"

def _apply_allocation_strategy(raised: float, total: float, hint: float) -> float:
    """
    Simple allocator: scale raised by weight 'hint', capped to bucket total.
    """
    return min(total, max(0.0, raised * max(0.0, hint)))

def build_impact_buckets(raised: float, sponsors_total: float, team_cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Build Impact Locker buckets for the UI.

    Allocation strategy:
      1) If team_cfg['impact_allocations'] provides explicit amounts per key, use those (capped by total).
      2) Else if team_cfg['impact_weights'] provides weights (sum ~1.0), use them.
      3) Else use default weights [0.40, 0.30, 0.20, 0.10] for
         ['gym_month','tournament_travel','uniforms','unity_day'].

    Returns a list of plain dicts (safe for JSON/Jinja).
    """
    costs = (team_cfg or {}).get("impact_costs", {}) or {}
    keys = ["gym_month", "tournament_travel", "uniforms", "unity_day"]

    # 1) Explicit $ allocations?
    alloc_map = {}
    if isinstance(team_cfg.get("impact_allocations"), dict):
        for k, v in team_cfg["impact_allocations"].items():
            alloc_map[k] = max(0.0, _num(v))

    # 2) Weights?
    weights = []
    if not alloc_map:
        if isinstance(team_cfg.get("impact_weights"), (list, tuple)):
            weights = [max(0.0, float(w)) for w in team_cfg["impact_weights"]]
        else:
            weights = [0.40, 0.30, 0.20, 0.10]

    buckets: List[Bucket] = []
    for i, key in enumerate(keys):
        spec = costs.get(key, {})
        total = _num(spec.get("total_cost"), 0.0)
        if total <= 0:
            # Skip invisible/disabled buckets
            continue

        if alloc_map:
            allocated = min(total, alloc_map.get(key, 0.0))
        else:
            weight = weights[i] if i < len(weights) else 0.0
            allocated = _apply_allocation_strategy(_num(raised), total, weight)

        percent = _clamp(_pct(allocated, total), 0, 100)
        next_gap, next_label = _calc_next_milestone_gap(total, allocated, spec.get("milestones") or [])
        locked = percent >= 100.0

        buckets.append(Bucket(
            key=key,
            label=str(spec.get("label", key)),
            details=str(spec.get("details", "")),
            total=total,
            allocated=round(allocated, 2),
            percent=percent,
            next_gap=round(next_gap, 2),
            next_label=next_label,
            milestones=list(spec.get("milestones") or []),
            emoji={"gym_month": "🏀", "tournament_travel": "🚌", "uniforms": "🎽", "unity_day": "🤝"}.get(key, "⭐"),
            locked=locked,
        ))

    # Maintain intended order (gym → travel → uniforms → unity)
    out: List[Dict[str, Any]] = []
    for k in keys:
        for b in buckets:
            if b.key == k:
                out.append({
                    "key": b.key,
                    "emoji": b.emoji,
                    "label": b.label,
                    "details": b.details,
                    "total": b.total,
                    "allocated": b.allocated,
                    "percent": b.percent,
                    "next_gap": b.next_gap,
                    "next_label": b.next_label,
                    "milestones": b.milestones,
                    "locked": b.locked,
                })
                break

    return out

