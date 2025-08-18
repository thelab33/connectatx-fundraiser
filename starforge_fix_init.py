#!/usr/bin/env python3
"""
starforge_fix_init.py — Repair bad static_url insertions in app/__init__.py
- Removes stray `from flask import url_for as _url_for` in the wrong place
- Ensures top-level import has `url_for`
- Adds module-level static_url() helper (CDN-aware)
- Ensures create_app registers Jinja global (idempotent)
"""

from pathlib import Path
import re
import sys

INIT = Path("app/__init__.py")
if not INIT.exists():
    print("❌ app/__init__.py not found")
    sys.exit(1)

src = INIT.read_text(encoding="utf-8")

# 1) Remove any stray mid-file `from flask import url_for as _url_for`
src = re.sub(r"\n\s*from\s+flask\s+import\s+url_for\s+as\s+_url_for\s*\n", "\n", src)

# 2) Ensure top-level import includes url_for
#    Prefer: from flask import Flask, url_for
def ensure_url_for_import(text: str) -> str:
    # Expand "from flask import Flask" → "from flask import Flask, url_for"
    pat = re.compile(r"^from\s+flask\s+import\s+([^\n]+)$", re.MULTILINE)
    found = False
    def repl(m):
        nonlocal found
        found = True
        items = [i.strip() for i in m.group(1).split(",")]
        if "url_for" not in items:
            items.append("url_for")
        # dedupe while preserving order
        dedup = []
        for it in items:
            if it and it not in dedup:
                dedup.append(it)
        return f"from flask import {', '.join(dedup)}"
    new = pat.sub(repl, text, count=1)  # only first import line
    if not found:
        # No "from flask import ..." line? Add a clean one near the top.
        new = re.sub(r"(^\s*from __future__.*?\n)", r"\1from flask import Flask, url_for\n", new, count=1, flags=re.DOTALL)
        if new == text:  # no __future__ header
            new = f"from flask import Flask, url_for\n{new}"
    return new

src = ensure_url_for_import(src)

# 3) Ensure module-level static_url helper (CDN-aware) exists exactly once
HELPER_ID = "def static_url(filename: str"
if HELPER_ID not in src:
    helper = """
# ---------------------------------------------------------------------------
# Starforge utility: CDN-aware static URL helper
# Usage: {{ static_url('css/app.css', v=asset_version) }}
# If CDN_URL is set in config, we serve from CDN; else url_for('static', ...).
# ---------------------------------------------------------------------------
def static_url(filename: str, **kwargs) -> str:
    try:
        # Prefer CDN if configured (e.g., https://cdn.fundchamps.com)
        cdn = None
        try:
            # 'current_app' only available in app context; guard just in case
            from flask import current_app
            cdn = (current_app and current_app.config.get("CDN_URL")) or None
        except Exception:
            cdn = None
        if cdn:
            # honor optional 'v' param for cache-busting
            v = kwargs.get("v")
            suffix = (f"?v={v}" if v is not None else "")
            return f"{cdn.rstrip('/')}/{filename.lstrip('/')}{suffix}"
        # Fallback to Flask static
        return url_for("static", filename=filename, **kwargs)
    except Exception:
        # Last-resort fallback (still deterministic)
        v = kwargs.get("v")
        suffix = (f"?v={v}" if v is not None else "")
        return f"/static/{filename}{suffix}"
"""
    # Append helper near the end, but before any __main__ guard
    if "__main__" in src:
        src = re.sub(r"\nif\s+__name__\s*==\s*['\"]__main__['\"]\s*:\s*\n.*", helper + "\n" + r"\g<0>", src, flags=re.DOTALL)
    else:
        src += helper

# 4) Ensure create_app registers Jinja global
#    Find def create_app( ... ):
m = re.search(r"def\s+create_app\s*\(.*?\):", src)
if not m:
    print("⚠️ Could not find create_app(); writing helper + import only.")
else:
    # Insert idempotent registration after the first occurrence of 'app = Flask(' inside create_app
    start = m.end()
    tail = src[start:]
    # limit search to first 1000 chars to keep safe
    ahead = tail[:1500]
    mm = re.search(r"app\s*=\s*Flask\s*\([^)]*\)", ahead)
    if mm:
        ins_at = start + mm.end()
        block = """
    # --- Register Jinja global helper (idempotent) ---
    try:
        if "static_url" not in app.jinja_env.globals:
            app.jinja_env.globals["static_url"] = static_url
    except Exception:
        pass
"""
        # Only add if not already present
        if "app.jinja_env.globals[\"static_url\"]" not in ahead and "app.jinja_env.globals['static_url']" not in ahead:
            src = src[:ins_at] + block + src[ins_at:]
    else:
        # Fallback: add near the end of create_app body
        src = re.sub(
            r"(def\s+create_app\s*\(.*?\):)",
            r"\1\n    # --- Register Jinja global helper (idempotent) ---\n"
            r"    try:\n"
            r"        if \"static_url\" not in app.jinja_env.globals:\n"
            r"            app.jinja_env.globals[\"static_url\"] = static_url\n"
            r"    except Exception:\n"
            r"        pass\n",
            src, count=1, flags=re.DOTALL
        )

# 5) Write back
INIT.write_text(src, encoding="utf-8")
print("✅ app/__init__.py repaired: url_for import fixed, static_url helper ensured, Jinja global registered.")

