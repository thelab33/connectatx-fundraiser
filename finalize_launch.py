#!/usr/bin/env python3
import sys, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tpl = ROOT / "app" / "templates"
partials = tpl / "partials"
static = ROOT / "app" / "static"

BASE = tpl / "base.html"
HOME = tpl / "home.html"

REQUIRED_PARTIALS = [
    "header_sponsor_ticker.html",
    "header_and_announcement.html",
    "footer.html",
    "donation_modal.html",
    "newsletter.html",
    "hero_and_fundraiser.html",
    "flash_and_onboarding.html",
    "admin_onboarding_popover.html",
    "about_section.html",
    "mission_section.html",
    "program_stats_and_calendar.html",
    "digital_hub.html",
    "tiers.html",
    "sponsor_spotlight.html",
    "sponsor_wall.html",
    "testimonial_popover.html",
    "back_to_top.html",
]

REQUIRED_JS = [
    "js/alpine.min.js",
    "js/htmx.min.js",
    "js/socket.io.js",
    "js/confetti.js",
    "js/fc-header-hero.js",
]
REQUIRED_CSS = ["css/tailwind.min.css"]
REQUIRED_IMAGES = ["images/logo.webp", "images/og.jpg"]

def backup(p: Path):
    if p.exists():
        shutil.copy2(p, p.with_suffix(p.suffix + ".bak"))

def ensure_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(content, encoding="utf-8")
        print(f"🆕 Created {path.relative_to(ROOT)}")
    else:
        print(f"✅ Found {path.relative_to(ROOT)}")

def main():
    print("🔧 Finalize Launch — sanity checks")
    # Backups
    for f in [BASE, HOME]:
        if f.exists():
            backup(f); print(f"📦 Backed up {f.relative_to(ROOT)}")

    # Partials
    for name in REQUIRED_PARTIALS:
        p = partials / name
        ensure_file(p, f"<!-- {name} placeholder (auto-created). Replace with real content. -->\n<section class=\"py-8\"></section>\n")

    # Static assets
    for rel in REQUIRED_JS:
        ensure_file(static / rel, "// placeholder\n")
    for rel in REQUIRED_CSS:
        ensure_file(static / rel, "/* placeholder */\n")
    for rel in REQUIRED_IMAGES:
        path = static / rel
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            # write a tiny webp/og placeholder text; real image recommended
            path.write_bytes(b"placeholder")
            print(f"🖼️  Placeholder image created: {path.relative_to(ROOT)}")
        else:
            print(f"🖼️  Found {path.relative_to(ROOT)}")

    # Quick warnings
    missing = [str((static / j).relative_to(ROOT)) for j in REQUIRED_JS if not (static / j).exists()]
    if missing:
        print("⚠️ Missing JS (placeholders created):", missing)

    print("✅ Finalize Launch checks done.")
    print("Next: run the smoke tests below.")
if __name__ == "__main__":
    sys.exit(main())
