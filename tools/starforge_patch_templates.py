#!/usr/bin/env python3
"""
Starforge Template Patcher — CSP + A11Y + Hints
- Adds nonce="{{ NONCE }}" to <script> and <style> without a nonce
- Ensures a NONCE macro is present near the top of each template
- Adds alt="" to any <img> without an alt attribute (a11y)
- Detects duplicate id="…" within each file and inserts a warning comment
- Makes .bak backups before writing
"""

from __future__ import annotations
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TPL_DIR = ROOT / "app" / "templates"

# Jinja nonce helper we want present once per file
NONCE_LINE = (
    '{% set NONCE = NONCE if NONCE is defined else '
    '(csp_nonce() if csp_nonce is defined else \'\') %}'
)

SCRIPT_OPEN_RE = re.compile(r'(?is)<script(?![^>]*\bnonce=)([^>]*)>')
STYLE_OPEN_RE  = re.compile(r'(?is)<style(?![^>]*\bnonce=)([^>]*)>')
IMG_NO_ALT_RE  = re.compile(r'(?is)<img\b((?:(?!>).)*)>')
ID_RE          = re.compile(r'(?i)\bid\s*=\s*["\']([^"\']+)["\']')

def add_nonce_to_tag(match, tag="script"):
    attrs = match.group(1).strip()
    # Keep existing attributes & spacing
    if attrs:
        return f'<{tag} nonce="{{{{ NONCE }}}}" {attrs}>'
    return f'<{tag} nonce="{{{{ NONCE }}}}">'

def ensure_nonces(html: str) -> str:
    html = SCRIPT_OPEN_RE.sub(lambda m: add_nonce_to_tag(m, "script"), html)
    html = STYLE_OPEN_RE.sub(lambda m: add_nonce_to_tag(m, "style"), html)
    return html

def ensure_nonce_helper(html: str) -> str:
    if "set NONCE" in html:
        return html
    # Try to insert right after an {% extends ... %} line
    lines = html.splitlines()
    for i, ln in enumerate(lines[:30]):  # only scan top of file
        if ln.strip().startswith("{% extends"):
            lines.insert(i + 1, NONCE_LINE)
            return "\n".join(lines) + ("\n" if not html.endswith("\n") else "")
    # Otherwise place at top
    return NONCE_LINE + "\n" + html

def add_missing_img_alt(html: str) -> str:
    out = []
    last = 0
    for m in IMG_NO_ALT_RE.finditer(html):
        tag = m.group(0)
        attrs = m.group(1) or ""
        if re.search(r'(?i)\balt\s*=', attrs):
            continue
        # Insert alt="" after <img
        fixed = "<img alt=\"\" " + attrs + ">"
        out.append(html[last:m.start()])
        out.append(fixed)
        last = m.end()
    out.append(html[last:])
    return "".join(out)

def detect_duplicate_ids(html: str):
    ids = ID_RE.findall(html)
    seen = {}
    dups = []
    for idv in ids:
        seen[idv] = seen.get(idv, 0) + 1
    for k, n in seen.items():
        if n > 1:
            dups.append((k, n))
    return dups

def insert_dup_comment(html: str, dups) -> str:
    if not dups:
        return html
    comment_lines = [f"<!-- Starforge: duplicate id(s) detected: "]
    comment_lines += [f'{k} ×{n}' for k, n in dups]
    comment_lines[-1] += " -->"
    comment = " | ".join(comment_lines)
    # Put right after the first <body or <main or at top
    pos = re.search(r'(?is)<body[^>]*>', html) or re.search(r'(?is)<main[^>]*>', html)
    if pos:
        idx = pos.end()
        return html[:idx] + "\n" + comment + "\n" + html[idx:]
    return comment + "\n" + html

def patch_file(p: Path) -> dict:
    orig = p.read_text(encoding="utf-8")
    html = orig

    html = ensure_nonce_helper(html)
    html = ensure_nonces(html)
    html = add_missing_img_alt(html)
    dups = detect_duplicate_ids(html)
    html = insert_dup_comment(html, dups)

    changed = html != orig
    if changed:
        bak = p.with_suffix(p.suffix + ".bak")
        bak.write_text(orig, encoding="utf-8")
        p.write_text(html, encoding="utf-8")
    return {
        "path": str(p),
        "changed": changed,
        "duplicates": dups,
    }

def main():
    if not TPL_DIR.exists():
        print(f"❌ templates dir missing: {TPL_DIR}")
        return
    files = list(TPL_DIR.rglob("*.html"))
    if not files:
        print("⚠️  No templates found.")
        return
    summary = []
    for f in files:
        summary.append(patch_file(f))

    # Report
    changed = sum(1 for s in summary if s["changed"])
    dup_count = sum(len(s["duplicates"]) for s in summary)
    print("✅ Template patch complete")
    print(f"• Files scanned : {len(summary)}")
    print(f"• Files changed : {changed}")
    print(f"• Duplicate id groups reported : {dup_count}")
    if dup_count:
        print("\n🔎 Duplicate id summary:")
        for s in summary:
            if s["duplicates"]:
                items = ", ".join([f'{k}×{n}' for k, n in s["duplicates"]])
                print(f"  - {s['path']}: {items}")

if __name__ == "__main__":
    main()

