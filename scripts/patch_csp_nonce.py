#!/usr/bin/env python3
import re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]  # repo root
TPL_DIR = ROOT / "app" / "templates"

# Patterns that are known-bad or too clever
BROKEN_PATTERNS = [
    r'nonce="\{\{\s*csp_nonce\(\)\s*if\s*csp_nonce\s*is\s*defined\s*else\s*\}\}"',  # else <empty>
    r"nonce='\{\{\s*csp_nonce\(\)\s*if\s*csp_nonce\s*is\s*defined\s*else\s*\}\}'",
    r'nonce="\{\{\s*csp_nonce\(\)\s*if\s*csp_nonce\s*is\s*defined\s*else\s*["\']\s*["\']\s*\}\}"',  # else '' or ""
    r'nonce="\{\{\s*csp_nonce\(\)\s*\}\}"',  # direct calls (we’ll standardize)
]

# Replace with simple, safe NONCE
REPLACEMENT = 'nonce="{{ NONCE }}"'

# Insert NONCE resolver at top if missing (for partials rendered w/o base inheritance)
NONCE_BOOTSTRAP = (
    "{% set NONCE = NONCE if NONCE is defined else "
    "(csp_nonce() if csp_nonce is defined else '') %}\n"
)

def needs_bootstrap(text: str) -> bool:
    if " set NONCE " in text or " set NONCE=" in text or "set NONCE =" in text:
        return False
    # If file uses nonce="{{ NONCE }}", ensure it has a resolver somewhere
    return 'nonce="{{ NONCE }}"' in text

def patch_file(p: pathlib.Path) -> bool:
    text = p.read_text(encoding="utf-8", errors="ignore")
    orig = text

    # Replace broken nonce patterns
    for pat in BROKEN_PATTERNS:
        text = re.sub(pat, REPLACEMENT, text)

    # Normalize any creative inline variants: csp_nonce() ternaries → NONCE
    text = re.sub(
        r'nonce="\{\{\s*csp_nonce\(\)\s*if\s*csp_nonce\s*is\s*defined\s*else\s*[^}]*\}\}"',
        REPLACEMENT,
        text,
    )

    # Optional: also normalize script/style that still call csp_nonce directly
    text = re.sub(
        r'nonce="\{\{\s*csp_nonce\(\)\s*\}\}"',
        REPLACEMENT,
        text,
    )

    # Bootstrap NONCE at the top of partials that might be included standalone
    if needs_bootstrap(text):
        # Put bootstrap after any leading comment block if present
        if text.lstrip().startswith("{#"):
            # Insert after the first end of a Jinja comment
            end = text.find("#}") 
            if end != -1:
                insert_at = end + 2
                text = text[:insert_at] + "\n" + NONCE_BOOTSTRAP + text[insert_at:]
            else:
                text = NONCE_BOOTSTRAP + text
        else:
            text = NONCE_BOOTSTRAP + text

    if text != orig:
        p.write_text(text, encoding="utf-8")
        print(f"patched: {p.relative_to(ROOT)}")
        return True
    return False

def main():
    if not TPL_DIR.exists():
        print(f"templates dir not found: {TPL_DIR}", file=sys.stderr)
        sys.exit(1)

    changed = 0
    for p in TPL_DIR.rglob("*.html"):
        changed += patch_file(p)
    print(f"done. files changed: {changed}")

if __name__ == "__main__":
    main()

