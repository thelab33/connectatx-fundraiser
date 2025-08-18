#!/usr/bin/env python3
"""
forge_prestige_patch3.py
Angel — Remapped Prestige Patcher
Maps missing overlay partials to actual files and applies SV-Elite polish.
"""

import shutil, time
from pathlib import Path

partials_dir = Path("app/templates/partials")

# Mapping Prestige target → actual file
remap = {
    "program_pulse.html": "program_stats_and_calendar.html",
    "impact_lockers.html": "impact_challenge_coaches_premium.html",
    "funds_allocation.html": "funds_allocation_bar_premium.html",
    "testimonials.html": "testimonials.html",
}

# Demo SV-Elite marker (expand with your real upgrades)
PRESTIGE_MARKER = "\n<!-- 🚀 SV-Elite Prestige Upgrade applied -->\n"

def patch_file(fname: str):
    fpath = partials_dir / fname
    if not fpath.exists():
        print(f"❌ {fname} not found, skipping.")
        return
    backup = f"{fname}.bak-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy(fpath, partials_dir / backup)
    txt = fpath.read_text(encoding="utf-8")
    if PRESTIGE_MARKER not in txt:
        fpath.write_text(txt.rstrip() + PRESTIGE_MARKER, encoding="utf-8")
        print(f"✅ Patched {fname} (backup: {backup})")
    else:
        print(f"⚠️  {fname} already prestige-patched.")

if __name__ == "__main__":
    for target, actual in remap.items():
        patch_file(actual)
    print("\n🎉 Remap-patch sweep complete. Homepage sections now Prestige-aligned!")
    print("↩ Rollback: copy any .bak-* file back over the partial.")
