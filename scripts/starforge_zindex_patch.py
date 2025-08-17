#!/usr/bin/env python3
"""
starforge_zindex_patch.py — SV-Elite Z-Index Harmonizer
- Normalizes z-index chaos (maps Bootstrap/Tailwind oddities to clean scale).
- Auto-injects `z-30` into hero sections (hero_and_fundraiser, hero_overlay, etc.).
- Creates timestamped .bak backups before editing.

Layering guide:
  -1   background hacks
  0-10 base content / legacy
  30   hero section (guaranteed floor)
  40   sticky nav/header
  50   banners/tooltips
  100  modals
  200  full-screen overlays
"""

import re, time
from pathlib import Path

ROOTS = [
    "app/static/css",
    "app/templates/partials"
]

# map extreme values down to sane layers
Z_MAP = {
    1049: 100,
    1050: 100,
    1100: 200,
    55:   50,
    51:   50,
    12:   10,
}

# hero detection (partials)
HERO_PARTIALS = [
    "hero_and_fundraiser.html",
    "hero_overlay_quote.html",
    "hero_overlay.html",
]

def normalize_zindex(text: str) -> str:
    def repl(m):
        val = int(m.group(1))
        return f"z-index: {Z_MAP.get(val,val)};"
    return re.sub(r"z-index:\s*(\d+)\s*;", repl, text)

def enforce_hero_layer(path: Path, text: str) -> str:
    if not any(name in path.name for name in HERO_PARTIALS):
        return text
    # inject z-30 into first <section ...> or wrapper
    new_text, n = re.subn(
        r'(<section\b[^>]*class=")([^"]*)"',
        lambda m: f'{m.group(1)}{m.group(2)} z-30"' if "z-" not in m.group(2) else m.group(0),
        text,
        count=1
    )
    if n:
        print(f"  [hero] ensured z-30 in {path}")
    return new_text

def patch_file(path: Path):
    orig = path.read_text(encoding="utf-8")
    txt = normalize_zindex(orig)
    txt = enforce_hero_layer(path, txt)
    if txt != orig:
        bak = path.with_suffix(path.suffix + f".bak-{time.strftime('%Y%m%d-%H%M%S')}")
        bak.write_text(orig, encoding="utf-8")
        path.write_text(txt, encoding="utf-8")
        print(f"✔ patched {path}")
    else:
        print(f"… no change {path}")

def main():
    for root in ROOTS:
        for p in Path(root).rglob("*.*"):
            if not p.suffix in (".css", ".html"): 
                continue
            try:
                patch_file(p)
            except Exception as e:
                print(f"❌ error {p}: {e}")

if __name__ == "__main__":
    main()
