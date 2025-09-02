#!/usr/bin/env python3
"""
fix_duplicate_tiers.py — removes accidental duplicate 'Sponsorship Tiers' sections
and de-duplicates 'id="tiers"' across all templates. It also prunes repeated
includes of the tiers partial within a single file.

Usage:
  python scripts/fix_duplicate_tiers.py [PROJECT_DIR]

- Scans the project for template folders (*/templates).
- For each *.html / *.jinja / *.j2 file:
    * If more than one 'id="tiers"' is found, rename all but the first to
      id="tiers-2", "tiers-3", ... (and similarly for 'tiers-heading').
    * If more than one {% include "...tiers..." %} is found in the same file,
      it comments out the extras with a safe Jinja comment wrapper.
- Produces a JSON report of changes.
"""

import sys, re, json
from pathlib import Path

PROJECT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
if not PROJECT.exists():
    print(f"[!] Project path not found: {PROJECT}", file=sys.stderr)
    sys.exit(1)

tmpl_roots = []
for p in PROJECT.rglob("templates"):
    if p.is_dir():
        tmpl_roots.append(p)

id_pat = re.compile(r'id\s*=\s*["\\\']tiers["\\\']', re.IGNORECASE)
heading_pat = re.compile(r'id\s*=\s*["\\\']tiers-heading["\\\']', re.IGNORECASE)
include_pat = re.compile(r'{%\s*include\s+["\\\'][^"\\\']*tiers[^"\\\']*["\\\']\s*%}')

changed = []
for root in tmpl_roots:
    for ext in ("*.html", "*.jinja", "*.j2"):
        for f in root.rglob(ext):
            try:
                text = f.read_text(encoding="utf-8")
            except Exception:
                continue

            orig = text
            # 1) Rename duplicate ids
            ids = list(id_pat.finditer(text))
            if len(ids) > 1:
                # Keep the first occurrence as 'tiers', rename others
                # We process from second forward; build a new string progressively
                parts = []
                last_idx = 0
                for i, m in enumerate(ids[1:], start=2):
                    parts.append(text[last_idx:m.start()])
                    parts.append('id="tiers-{}"'.format(i))
                    last_idx = m.end()
                parts.append(text[last_idx:])
                text = "".join(parts)

                # Also fix headings in the same order
                heads = list(heading_pat.finditer(text))
                if len(heads) > 1:
                    parts = []
                    last_idx = 0
                    for i, m in enumerate(heads[1:], start=2):
                        parts.append(text[last_idx:m.start()])
                        parts.append('id="tiers-heading-{}"'.format(i))
                        last_idx = m.end()
                    parts.append(text[last_idx:])
                    text = "".join(parts)

            # 2) Comment out duplicate includes of tiers within the same file
            incs = list(include_pat.finditer(text))
            if len(incs) > 1:
                parts = []
                last_idx = 0
                # Keep first include, comment out subsequent ones
                for i, m in enumerate(incs[1:], start=2):
                    parts.append(text[last_idx:m.start()])
                    block = text[m.start():m.end()]
                    parts.append("{# DUPLICATE TIERS INCLUDE REMOVED BY SCRIPT: ")
                    parts.append(block.replace("#", "~"))  # avoid closing comment edge
                    parts.append(" #}")
                    last_idx = m.end()
                parts.append(text[last_idx:])
                text = "".join(parts)

            if text != orig:
                backup = f.with_suffix(f.suffix + ".bak")
                try:
                    f.rename(backup)
                except Exception:
                    pass
                f.write_text(text, encoding="utf-8")
                changed.append(str(f))

report = {
    "project": str(PROJECT.resolve()),
    "template_roots": [str(p) for p in tmpl_roots],
    "files_changed": changed,
    "summary": {
        "num_roots": len(tmpl_roots),
        "num_files_changed": len(changed),
    }
}

out = Path("fix_duplicate_tiers.report.json")
out.write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
