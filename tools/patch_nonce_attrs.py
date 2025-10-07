#!/usr/bin/env python3
# tools/patch_nonce_attrs.py
"""
Normalize nonce usage in templates:
- Remove duplicates like: <style {{ nonce_attr() }}nonce="{{ NONCE }}">
- Replace nonce="{{ NONCE }}" with {{ nonce_attr() }} on <script>/<style>
- Ensure every <script>/<style> has {{ nonce_attr() }} exactly once
- Preserve all other attributes
"""
from __future__ import annotations
import re
import sys
from pathlib import Path
from typing import Tuple

SCRIPT_TAG = re.compile(r'<(script|style)\b', re.IGNORECASE)

def patch_text(txt: str) -> Tuple[str, bool]:
    orig = txt

    # 1) Collapse "{{ nonce_attr() }}nonce="{{ NONCE }}" → {{ nonce_attr() }}"
    #    and the reverse order as well.
    txt = re.sub(
        r'{{\s*nonce_attr\(\)\s*}}\s*nonce="\s*{{\s*NONCE\s*}}\s*"',
        '{{ nonce_attr() }}',
        txt, flags=re.IGNORECASE
    )
    txt = re.sub(
        r'nonce="\s*{{\s*NONCE\s*}}\s*"\s*{{\s*nonce_attr\(\)\s*}}',
        '{{ nonce_attr() }}',
        txt, flags=re.IGNORECASE
    )

    # 2) Replace nonce="{{ NONCE }}" inside <script>/<style> with {{ nonce_attr() }}
    #    Keep all other attributes, preserve order.
    def repl_nonce_to_macro(m: re.Match) -> str:
        tag = m.group(1)
        pre = m.group(2) or ''    # attributes before nonce
        post = m.group(3) or ''   # attributes after nonce
        pre = pre.rstrip()
        space = ' ' if (pre and not pre.endswith(' ')) else ' '
        return f'<{tag}{pre}{space}{{{{ nonce_attr() }}}}{post}>'

    txt = re.sub(
        r'<(script|style)\b([^>]*?)\snonce="\s*{{\s*NONCE\s*}}\s*"\s*([^>]*)>',
        repl_nonce_to_macro,
        txt, flags=re.IGNORECASE
    )

    # 3) Ensure every <script>/<style> open tag has {{ nonce_attr() }} if missing.
    #    Skip if tag already contains nonce= or {{ nonce_attr() }}.
    def ensure_nonce_attr(m: re.Match) -> str:
        tag = m.group(1)
        attrs = m.group(2) or ''
        # already has nonce or macro? leave as-is
        if re.search(r'nonce\s*=|{{\s*nonce_attr\(\)\s*}}', attrs, flags=re.IGNORECASE):
            return m.group(0)
        attrs = (' ' + attrs.strip()) if attrs.strip() else ''
        return f'<{tag} {{ {{ nonce_attr() }} }}{attrs}>'.replace('{{ {{', '{{').replace('}} }}','}}')

    txt = re.sub(
        r'<(script|style)\b([^>]*)>',
        ensure_nonce_attr,
        txt, flags=re.IGNORECASE
    )

    # 4) De-duplicate multiple {{ nonce_attr() }} in the same tag.
    #    e.g., "<script {{ nonce_attr() }} {{ nonce_attr() }} …>"
    txt = re.sub(
        r'(\s*\{\{\s*nonce_attr\(\)\s*\}\}\s*){2,}',
        ' {{ nonce_attr() }} ',
        txt
    )

    # 5) Micro-clean: collapse accidental double spaces before ">"
    txt = re.sub(r'\s+>', '>', txt)

    return txt, (txt != orig)

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else Path("app/templates")
    write = ("--write" in sys.argv) or ("-w" in sys.argv)

    files = [p for p in root.rglob("*.html")]
    changed = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        new, did = patch_text(text)
        if did:
            changed += 1
            if write:
                f.write_text(new, encoding="utf-8")
                print(f"✅ fixed: {f}")
            else:
                print(f"would fix: {f}")

    print(f"\n{'Patched' if write else 'Would patch'} {changed} of {len(files)} files in {root}")

if __name__ == "__main__":
    main()

