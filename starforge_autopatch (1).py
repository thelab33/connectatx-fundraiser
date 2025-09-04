#!/usr/bin/env python3
"""
starforge_autopatch.py
----------------------
Auto-fixes common CSS wiring issues in FundChamps projects.

What it does by default:
  1) Keeps only the FIRST occurrence of `@import ...(starforge-additions.css)`.
  2) Removes any `@import ...(.js)` lines (e.g., fc_holo.js accidentally imported as CSS).
  3) (Optional) --disable-hero-css to comment out the fc-hero CSS import if you inline hero styles in templates.

Idempotent: safe to run multiple times.

Usage examples:
  python starforge_autopatch.py -f app/static/css/input.css --dry-run
  python starforge_autopatch.py -f app/static/css/input.css
  python starforge_autopatch.py -f app/static/css/input.css --disable-hero-css

Exit codes:
  0 on success (even if no changes), 1 on error.
"""
from __future__ import annotations
import re, sys, difflib, argparse, datetime
from pathlib import Path

ADDONS_RE = re.compile(r'@import\\s+(?:url\\(|)\\s*[\'"]\\s*\\.\\/?(?:[^"\\)]*/)?starforge-additions\\.css\\s*[\'"]\\s*\\)?\\s*;\\s*', re.IGNORECASE)
JS_IMPORT_RE = re.compile(r'@import\\s+(?:url\\(|)\\s*[\'"][^\'"]+\\.js[\'"]\\s*\\)?\\s*;\\s*', re.IGNORECASE)
HERO_IMPORT_RE = re.compile(r'@import\\s+(?:url\\(|)\\s*[\'"]\\s*\\.\\/?(?:[^"\\)]*/)?fc-hero[^\'"]*\\.css\\s*[\'"]\\s*\\)?\\s*;\\s*', re.IGNORECASE)

def dedupe_starforge_addons(css: str) -> tuple[str, int]:
    """Keep only the first starforge-additions.css import; remove others."""
    matches = list(ADDONS_RE.finditer(css))
    removed = 0
    if len(matches) > 1:
        # Keep first, remove subsequent
        to_remove_spans = [m.span() for m in matches[1:]]
        new_css = []
        last = 0
        for start, end in to_remove_spans:
            new_css.append(css[last:start])
            last = end
            removed += 1
        new_css.append(css[last:])
        return ("".join(new_css), removed)
    return (css, removed)

def strip_js_imports(css: str) -> tuple[str, int]:
    """Remove any @import lines that incorrectly reference .js files."""
    new_css, n = JS_IMPORT_RE.subn("", css)
    return (new_css, n)

def maybe_disable_hero(css: str, disable: bool) -> tuple[str, int]:
    if not disable:
        return (css, 0)
    count = 0
    def repl(m):
        nonlocal count
        count += 1
        line = m.group(0).rstrip()
        return f"/* disabled by starforge_autopatch: {line} */\n"
    css2 = HERO_IMPORT_RE.sub(repl, css)
    return (css2, count)

def patch(css: str, disable_hero: bool) -> tuple[str, str, dict]:
    original = css
    report = {}
    css, rm_addons = dedupe_starforge_addons(css)
    report["dedup_starforge_additions"] = rm_addons
    css, rm_js = strip_js_imports(css)
    report["removed_js_imports"] = rm_js
    css, dis_hero = maybe_disable_hero(css, disable_hero)
    report["disabled_hero_imports"] = dis_hero
    return original, css, report

def main():
    ap = argparse.ArgumentParser(description="Auto-fix FundChamps input.css wiring")
    ap.add_argument("-f", "--file", required=True, help="Path to input.css")
    ap.add_argument("--dry-run", action="store_true", help="Show diff but do not write")
    ap.add_argument("--no-backup", action="store_true", help="Do not create .bak backup")
    ap.add_argument("--disable-hero-css", action="store_true",
                    help="Comment out @import of fc-hero*.css (use if hero styles are inlined in templates)")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        print(f"[ERR] File not found: {p}", file=sys.stderr)
        return 1
    css = p.read_text(encoding="utf-8")

    original, patched, report = patch(css, args.disable_hero_css)

    if original == patched:
        print("[OK] No changes needed.")
        print(f"    stats: {report}")
        return 0

    # Show diff
    diff = difflib.unified_diff(
        original.splitlines(True),
        patched.splitlines(True),
        fromfile=str(p),
        tofile=str(p) + " (patched)",
        lineterm="",
    )
    print("".join(diff))

    if args.dry_run:
        print("\n[DRY-RUN] No files written.")
        print(f"    stats: {report}")
        return 0

    if not args.no_backup:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = p.with_suffix(p.suffix + f".bak.{ts}")
        backup.write_text(original, encoding="utf-8")
        print(f"[OK] Backup written: {backup.name}")

    p.write_text(patched, encoding="utf-8")
    print(f"[OK] Patched: {p}")
    print(f"    stats: {report}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
