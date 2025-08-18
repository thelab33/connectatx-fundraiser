#!/usr/bin/env python3
"""
forge_csp_autowrap.py
────────────────────────────────────────────
Wraps inline <script> tags in all Jinja partials with CSP-safe wrappers:
  {% if script_open is defined %}{{ script_open() }}{% else %}<script nonce="{{ NONCE }}">{% endif %}
  …contents…
  {% if script_close is defined %}{{ script_close() }}{% else %}</script>{% endif %}

- Creates timestamped .bak files before patching.
- Skips already wrapped scripts.
- Idempotent: safe to run multiple times.
"""

import re
from pathlib import Path
from datetime import datetime

PARTIALS_DIR = Path("app/templates/partials")
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

SCRIPT_RE = re.compile(r"(<script\b[^>]*>)([\s\S]*?)(</script>)", re.I)

for f in PARTIALS_DIR.glob("*.html"):
    text = f.read_text(encoding="utf-8")
    if "script_open" in text or "script_close" in text:
        continue  # already patched

    def replacer(m):
        inner = m.group(2).strip("\n")
        return (
            "{% if script_open is defined %}{{ script_open() }}{% else %}"
            "<script nonce=\"{{ NONCE }}\">{% endif %}\n"
            f"{inner}\n"
            "{% if script_close is defined %}{{ script_close() }}{% else %}</script>{% endif %}"
        )

    new_text, count = SCRIPT_RE.subn(replacer, text)
    if count > 0:
        backup = f.with_suffix(f".html.bak-" + STAMP)
        f.rename(backup)
        f.write_text(new_text, encoding="utf-8")
        print(f"✅ Wrapped {count} script(s) in {f.name} (backup: {backup.name})")

print("🎉 CSP AutoWrap complete. Rollback = restore .bak file(s).")
