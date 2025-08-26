#!/usr/bin/env python3
"""
Refactor Partials → SaaS Layout (Production-Grade)
- Moves premium/admin/shared partials into new subfolders
- Updates `{% include %}` paths across templates
- Creates a Git commit so you can easily roll back
"""

import os, re, shutil, subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "app" / "templates"
PARTIALS = BASE / "partials"

# Map old file → new folder
MOVE_MAP = {
    # Premium
    "impact_challenge_coaches_premium.html": "premium",
    "impact_lockers_premium.html": "premium",
    "funds_allocation_bar_premium.html": "premium",
    "flash_and_onboarding_premium.html": "premium",
    # Admin
    "admin_onboarding_popover.html": "admin",
    "ai_concierge.html": "admin",
    # Shared
    "macros.html": "shared",
    "ui_bootstrap.html": "shared",
}

def ensure_dirs():
    for d in {"premium", "admin", "shared"}:
        (BASE / d).mkdir(exist_ok=True)

def move_files():
    for fname, newdir in MOVE_MAP.items():
        src = PARTIALS / fname
        dst = BASE / newdir / fname
        if src.exists():
            print(f"[MOVE] {src} → {dst}")
            shutil.move(str(src), str(dst))

def update_includes():
    regex = re.compile(r'{%\s*include\s+[\'"]partials/([^\'"]+)[\'"]')
    for path in BASE.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        changed = text
        for fname, newdir in MOVE_MAP.items():
            changed = changed.replace(
                f'include "partials/{fname}"',
                f'include "{newdir}/{fname}"'
            )
        if changed != text:
            print(f"[UPDATE] {path}")
            path.write_text(changed, encoding="utf-8")

def git_commit():
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run([
        "git", "commit", "-m",
        "🏗️ Refactor partials: premium/admin/shared separation"
    ], check=True)

if __name__ == "__main__":
    ensure_dirs()
    move_files()
    update_includes()
    git_commit()
    print("\n✨ Refactor complete! Your templates are now SaaS-clean.")

