#!/usr/bin/env python3
"""
audit_partials.py — Find broken/missing Jinja partials and debug hero overlay issues.
"""

from pathlib import Path
import re

BASE = Path("app/templates")
INDEX = BASE / "index.html"

# --- Step 1: scan for all includes in index.html ---
include_re = re.compile(r'{%\s*include\s+"partials/([^"]+)"')

partials = set()
for line in INDEX.read_text(encoding="utf-8").splitlines():
    m = include_re.search(line)
    if m:
        partials.add(m.group(1))

print("🔎 Found partial includes in index.html:")
for p in sorted(partials):
    print(f"  - {p}")

# --- Step 2: verify existence and hero overlay markers ---
missing = []
overlay_flags = {}

for p in sorted(partials):
    f = BASE / "partials" / p
    if not f.exists():
        missing.append(p)
        continue
    txt = f.read_text(encoding="utf-8", errors="ignore").lower()
    # Look for hero/overlay related markers
    has_hero = "id=\"hero" in txt or "hero" in f.stem
    has_overlay = "overlay" in txt or "z-" in txt
    overlay_flags[p] = (has_hero, has_overlay)

print("\n📂 Partial health check:")
for p in sorted(partials):
    if p in missing:
        print(f"  ❌ MISSING: {p}")
    else:
        hero, overlay = overlay_flags[p]
        flags = []
        if hero: flags.append("hero")
        if overlay: flags.append("overlay")
        mark = " / ".join(flags) if flags else "no overlay markers"
        print(f"  ✅ {p} → {mark}")

# --- Step 3: final report ---
print("\n=== REPORT ===")
if missing:
    print("⚠️ Missing partials:", ", ".join(missing))
else:
    print("✅ No missing partials.")

overlay_partials = [p for p,(h,o) in overlay_flags.items() if h or o]
if not overlay_partials:
    print("❌ No partial contains overlay markers. Hero likely broken.")
else:
    print("✅ Overlay candidates:", ", ".join(overlay_partials))

