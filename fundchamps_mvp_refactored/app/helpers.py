# app/helpers.py
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "_num",
    "_clamp",
    "_pct",
    "_money_i",
    "_as_players",
    "_normalize_stats",
    "_generate_about_section",
    "_generate_impact_stats",
    "_generate_challenge_section",
    "_generate_mission_section",
    "_prepare_stats",
    "build_impact_buckets",
    "Bucket",
]

# ─────────────────────────────────────────────────────────────
# Small utility helpers
# ─────────────────────────────────────────────────────────────


def _num(v: Any, default: float = 0.0) -> float:
    """
    Parse numeric-ish input into a float.
      - Handles int/float directly
      - Strings with commas/underscores/currency symbols: "1,200", "$1_200"
      - Suffix multipliers: 10k, 1.2m, 2b (case-insensitive)
      - Accounting negatives: "(123.45)" -> -123.45
    Returns `default` on failure.
    """
    if v is None:
        return default
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    s = str(v).strip().lower()

    # accounting-style negative e.g. "(123.45)"
    neg = s.startswith("(") and s.endswith(")")
    if neg:
        s = s[1:-1].strip()

    # strip currency & soft noise
    for junk in ("$", "usd", " ", ",", "_"):
        s = s.replace(junk, "")

    mult = 1.0
    if s.endswith(("k", "m", "b")):
        suf = s[-1]
        s = s[:-1]
        mult = {"k": 1_000.0, "m": 1_000_000.0, "b": 1_000_000_000.0}[suf]

    try:
        val = float(s) * mult
        return -val if neg else val
    except Exception:
        return default


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _pct(n: float, d: float) -> float:
    """Stable percentage rounded to 1 decimal; 0 if denominator falsy."""
    if not d:
        return 0.0
    try:
        return round((float(n) / float(d)) * 100.0, 1)
    except Exception:
        return 0.0


def _money_i(n: float) -> int:
    """Whole-dollar int for display math (server-side formatting done in templates)."""
    try:
        return int(round(float(n or 0.0)))
    except Exception:
        return 0


def _as_players(lst: Any) -> List[Dict[str, str]]:
    """
    Normalize player list to [{name:str, role:str}].
    Accepts:
      - [{'name': 'X', 'role': 'Y'}, ...]
      - ['X', 'Y', ...]
    """
    out: List[Dict[str, str]] = []
    if not lst:
        return out
    for it in lst:
        if isinstance(it, dict) and it.get("name"):
            out.append({"name": str(it["name"]), "role": str(it.get("role", ""))})
        elif isinstance(it, str) and it.strip():
            out.append({"name": it.strip(), "role": ""})
    return out


def _normalize_stats(stats: Any) -> List[Dict[str, Any]]:
    """
    Ensure each stat is {'label': str, 'value': number|str}.
    Attempts to parse numeric values via _num; keeps strings if not numeric.
    """
    norm: List[Dict[str, Any]] = []
    for s in stats or []:
        if not isinstance(s, dict):
            continue
        label = str(s.get("label", "") or "").strip()
        if not label:
            continue
        raw = s.get("value", 0)
        parsed = _num(raw, default=float("nan"))
        value: Any = parsed if not math.isnan(parsed) else raw
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
    about_text = (
        team.get("about_text")
        or " ".join([p for p in about_list if isinstance(p, str)])
        or "We are a community-powered youth program building character on and off the court."
    )

    return {
        "heading": team.get("about_heading", f"About {team_name}"),
        "text": about_text,
        "players": _as_players(team.get("players")),
        "cta": team.get("cta_label", "Join Us"),
    }


def _generate_impact_stats(team: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return normalized impact stats, with a solid default if missing."""
    stats = _normalize_stats(team.get("impact_stats"))
    return stats or [{"label": "Players Enrolled", "value": 16}]


def _generate_challenge_section(
    team: Dict[str, Any], impact_stats: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Build a succinct challenge section. Re-uses impact stats as 'metrics'."""
    return {
        "heading": team.get("challenge_heading", "The Challenge"),
        "text": team.get(
            "challenge_text",
            "Gym time, travel costs, and gear add up fast for volunteer families.",
        ),
        "metrics": impact_stats[:4],
    }


def _generate_mission_section(
    team: Dict[str, Any], impact_stats: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Mission copy with optional stats accompaniment."""
    team_name = team.get("team_name", "Our Team")
    return {
        "heading": team.get("mission_heading", "Our Mission"),
        "text": team.get(
            "mission_text",
            f"{team_name} builds teamwork, respect, and championship character—"
            "in the classroom and on the court.",
        ),
        "stats": impact_stats[:4],
    }


def _prepare_stats(
    team: Dict[str, Any],
    raised: float,
    goal: Optional[float],
    percent_raised: Optional[float],
) -> Dict[str, Any]:
    """
    Normalize fundraiser metrics and add derived values for templates.
    - Uses explicit `goal` if provided, else team['fundraising_goal']
    - Computes percent if not provided
    """
    r = _num(raised)
    g = _num(goal if goal is not None else team.get("fundraising_goal", 0))
    p = percent_raised if percent_raised is not None else _pct(r, g)
    remaining = max(0.0, g - r)

    return {
        "raised": r,
        "goal": g,
        "percent": _clamp(p, 0.0, 100.0),
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
    next_gap: float  # $ to lock the next milestone (or remaining total if none)
    next_label: str  # label of the upcoming milestone
    milestones: List[Dict[str, Any]]
    emoji: str
    locked: bool


def _calc_next_milestone_gap(
    total: float,
    allocated: float,
    milestones: List[Dict[str, Any]],
) -> Tuple[float, str]:
    """
    Given a total and list of milestone 'cost' items, compute:
      - the minimal $ gap to reach the next cumulative milestone
      - the milestone label
    Falls back to remaining total if milestones are missing/exhausted.
    """
    remaining = max(0.0, total - allocated)
    if total <= 0 or remaining <= 0:
        return 0.0, "Fully funded"

    # Build cumulative checkpoints: [(cum_amount, label), ...]
    cum = 0.0
    checkpoints: List[Tuple[float, str]] = []
    for m in milestones or []:
        cost = _num(m.get("cost"), 0.0)
        if cost <= 0:
            continue
        cum += cost
        checkpoints.append((cum, str(m.get("label") or "Milestone")))

    # No configured milestones → next gap is the remaining total.
    if not checkpoints:
        return remaining, "Goal"

    # First cumulative target above current allocation.
    for cum_target, label in checkpoints:
        if allocated < cum_target:
            return max(0.0, cum_target - allocated), label

    # Past all milestones → remaining to total.
    return remaining, "Goal"


def _apply_allocation_strategy(raised: float, total: float, weight: float) -> float:
    """Simple allocator: scale raised by weight, capped to bucket total."""
    return min(total, max(0.0, raised * max(0.0, weight)))


def build_impact_buckets(
    raised: float,
    sponsors_total: float,
    team_cfg: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """
    Build Impact Locker buckets for the UI.

    Allocation strategy (in order of precedence):
      1) If team_cfg['impact_allocations'] provides explicit amounts per key, use those (capped by each bucket total).
      2) Else if team_cfg['impact_weights'] provides weights (sum ~1.0), use them.
      3) Else use default weights [0.40, 0.30, 0.20, 0.10] for keys:
         ['gym_month','tournament_travel','uniforms','unity_day'].

    Notes:
      - By default, allocations use only `raised`. To include sponsor money in the pool,
        set `team_cfg['allocate_includes_sponsors'] = True`.
      - Any bucket with `total_cost <= 0` is skipped (invisible/disabled).

    Returns a list of plain dicts (safe for JSON/Jinja) in intended order.
    """
    cfg = team_cfg or {}
    costs = cfg.get("impact_costs", {}) or {}
    keys = ["gym_month", "tournament_travel", "uniforms", "unity_day"]

    # Decide what "pool" is used for allocation
    pool = _num(raised)
    if cfg.get("allocate_includes_sponsors") is True:
        pool += max(0.0, _num(sponsors_total))

    # 1) Explicit $ allocations?
    alloc_map: Dict[str, float] = {}
    if isinstance(cfg.get("impact_allocations"), dict):
        for k, v in cfg["impact_allocations"].items():
            alloc_map[k] = max(0.0, _num(v))

    # 2) Otherwise, weights (or defaults)
    weights: List[float] = []
    if not alloc_map:
        if isinstance(cfg.get("impact_weights"), (list, tuple)):
            weights = [max(0.0, float(w)) for w in cfg["impact_weights"]]
        else:
            weights = [0.40, 0.30, 0.20, 0.10]

    buckets: List[Bucket] = []
    for i, key in enumerate(keys):
        spec = costs.get(key, {}) or {}
        total = _num(spec.get("total_cost"), 0.0)
        if total <= 0:
            continue  # Skip invisible/disabled buckets

        if alloc_map:
            allocated = min(total, alloc_map.get(key, 0.0))
        else:
            weight = weights[i] if i < len(weights) else 0.0
            allocated = _apply_allocation_strategy(pool, total, weight)

        percent = _clamp(_pct(allocated, total), 0.0, 100.0)
        next_gap, next_label = _calc_next_milestone_gap(
            total, allocated, spec.get("milestones") or []
        )
        locked = percent >= 100.0

        buckets.append(
            Bucket(
                key=key,
                label=str(spec.get("label", key)),
                details=str(spec.get("details", "")),
                total=round(total, 2),
                allocated=round(allocated, 2),
                percent=percent,
                next_gap=round(next_gap, 2),
                next_label=next_label,
                milestones=list(spec.get("milestones") or []),
                emoji={
                    "gym_month": "🏀",
                    "tournament_travel": "🚌",
                    "uniforms": "🎽",
                    "unity_day": "🤝",
                }.get(key, "⭐"),
                locked=locked,
            )
        )

    # Maintain intended order (gym → travel → uniforms → unity)
    out: List[Dict[str, Any]] = []
    for k in keys:
        for b in buckets:
            if b.key == k:
                out.append(
                    {
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
                    }
                )
                break

    return out
