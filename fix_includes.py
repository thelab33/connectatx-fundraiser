#!/usr/bin/env python3
from pathlib import Path
import re, shutil

ROOTS = [Path("app/templates"), Path("src/templates")]
INCLUDE_RX = re.compile(r'\{\%\s*include\s+([\'"])([^\'"]+)\1([^%]*?)\%\}', re.MULTILINE)
HOTPATCH_RX = re.compile(r'\{\%\s*hotpatch[^\%]*\%\}', re.IGNORECASE)

def normalize_include(m):
    quote, path, tail = m.group(1), m.group(2), m.group(3) or ""
    tail = tail.strip()
    # If the tag already mentions ignore missing, keep it but normalize spacing
    if re.search(r'\bignore\s+missing\b', tail):
        return f'{{% include {quote}{path}{quote} ignore missing %}}'
    # If it has other flags (e.g., with context), keep them and ensure ignore missing exists
    extra = re.sub(r'\bignore\s+missing\b', '', tail).strip()
    if extra:
        # put ignore missing before any extras for consistency
        return f'{{% include {quote}{path}{quote} ignore missing {extra} %}}'
    # Plain include -> add ignore missing
    return f'{{% include {quote}{path}{quote} ignore missing %}}'

def process_file(p: Path):
    text = p.read_text(encoding="utf-8", errors="ignore")
    orig = text

    # Normalize include tags
    text = INCLUDE_RX.sub(normalize_include, text)

    # Remove stray hotpatch blocks
    text = HOTPATCH_RX.sub('', text)

    if text != orig:
        bak = p.with_suffix(p.suffix + ".bak")
        if not bak.exists():
            shutil.copyfile(p, bak)
        p.write_text(text, encoding="utf-8")
        return True
    return False

changed = 0
for root in ROOTS:
    if root.exists():
        for p in root.rglob("*.html"):
            try:
                if process_file(p):
                    changed += 1
            except Exception as e:
                print(f"⚠️  Skip {p}: {e}")

print(f"✅ Done. Files modified: {changed}")
print("ℹ️  Backups written as *.bak next to originals.")
