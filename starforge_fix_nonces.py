#!/usr/bin/env python3
"""
Starforge Nonce Auditor & Auto-Patcher
--------------------------------------
Scans all Jinja templates (*.html) for:
  • <script>/<style> without nonce
  • Typos like <scrip …>
  • Duplicate nonce attributes
  • Old includes of partials/ui_bootstrap.html
And fixes them safely in-place.

Usage:
  python3 starforge_fix_nonces.py --dry-run   # scan only
  python3 starforge_fix_nonces.py --fix       # auto-patch
"""

import re
import argparse
from pathlib import Path

# Regex patterns
STYLE_NO_NONCE = re.compile(r"<style(?![^>]*nonce=)")
SCRIPT_NO_NONCE = re.compile(r"<script(?![^>]*nonce=)")
SCRIPT_TYPO = re.compile(r"<scrip\b")  # missing 't'
DUP_NONCE = re.compile(r'nonce="{{ NONCE }}"[^>]*nonce="{{ NONCE }}"')

def scan_and_fix(file_path: Path, fix: bool = False):
    text = file_path.read_text(encoding="utf-8")
    original = text
    issues = []

    # Detect issues
    if STYLE_NO_NONCE.search(text):
        issues.append("style missing nonce")
        if fix:
            text = STYLE_NO_NONCE.sub('<style nonce="{{ NONCE }}"', text)

    if SCRIPT_NO_NONCE.search(text):
        issues.append("script missing nonce")
        if fix:
            text = SCRIPT_NO_NONCE.sub('<script nonce="{{ NONCE }}"', text)

    if SCRIPT_TYPO.search(text):
        issues.append("script typo <scrip>")
        if fix:
            text = SCRIPT_TYPO.sub("<script", text)

    if DUP_NONCE.search(text):
        issues.append("duplicate nonce attr")
        if fix:
            text = DUP_NONCE.sub('nonce="{{ NONCE }}"', text)

    # Old include path
    if "partials/ui_bootstrap.html" in text:
        issues.append("old include → partials/ui_bootstrap.html")
        if fix:
            text = text.replace("partials/ui_bootstrap.html", "shared/ui_bootstrap.html")

    # Apply fix if changed
    if fix and text != original:
        file_path.write_text(text, encoding="utf-8")

    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues in place")
    parser.add_argument("--dry-run", action="store_true", help="Only scan, no writes")
    args = parser.parse_args()

    root = Path("app/templates")
    files = list(root.rglob("*.html"))
    if not files:
        print("❌ No .html files found under app/templates/")
        return

    print(f"🔎 Scanning {len(files)} templates…")
    total_issues = 0
    for f in files:
        issues = scan_and_fix(f, fix=args.fix)
        if issues:
            total_issues += len(issues)
            print(f"⚠️  {f}: {', '.join(issues)}")

    if total_issues == 0:
        print("✅ All templates clean & CSP-safe!")
    elif args.fix:
        print(f"✨ Fixed {total_issues} issues across {len(files)} files.")
    else:
        print(f"⚠️ Found {total_issues} issues (run with --fix to auto-patch).")


if __name__ == "__main__":
    main()

