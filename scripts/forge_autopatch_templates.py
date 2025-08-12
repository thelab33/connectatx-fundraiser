#!/usr/bin/env python3
import os, re, shutil, time

TEMPLATES_DIR = os.environ.get("TEMPLATES_DIR", "app/templates")
STAMP = time.strftime("%Y%m%d-%H%M%S")

def backup(path):
    shutil.copy2(path, f"{path}.{STAMP}.bak")

def replace_attrs_block(text):
    # Replace any `{% if attrs %} ... {% endif %}` (inline in an opening tag) with xmlattr
    return re.sub(r"\{\%\s*if\s+attrs\s*\%\}.*?\{\%\s*endif\s*\%\}",
                  "{{ (attrs or {})|xmlattr }}",
                  text, flags=re.DOTALL)

def cond_hx_inline(text):
    # Convert block-in-tag hx-* to a single inline expression Prettier can parse
    # Pattern 1: every 5m (announcement bar)
    text = re.sub(
        r"\{\%\s*if\s+has_endpoint\('([^']+)'\)\s*\%\}\s*"
        r"hx-get=\"\{\{\s*safe_url_for\('\1'\)\s*\}\}\"\s*"
        r"hx-trigger=\"([^\"]*)\"\s*"
        r"hx-swap=\"([^\"]*)\"\s*"
        r"\{\%\s*endif\s*\%\}",
        r"{{ ('hx-get=\"' ~ safe_url_for('\1') ~ '\" hx-trigger=\"\2\" hx-swap=\"\3\"') if has_endpoint('\1') else '' }}",
        text, flags=re.DOTALL
    )
    return text

def fix_svg_noise(text):
    text = re.sub(r"<svg\s+none", '<svg fill="none"', text)
    text = re.sub(r"</svg\s+aria-label=\"\">", "</svg>", text)
    # Fix shapes that were self-closing then polluted with aria-label
    text = re.sub(r"(<(?:rect|path|circle|line|polyline|polygon)\b[^>]*?)\/\s*aria-label=\"\"\s*>", r"\1/>", text)
    # Remove duplicated empty aria-labels on shapes
    text = re.sub(r"\saria-label=\"\"\s*(/?>)", r"\1", text)
    return text

def fix_url_for_mangles(text):
    text = re.sub(r"url_forstatic,\s*filename=", "url_for('static', filename=", text)
    text = text.replace('action="url_formain.sponsor"', 'action="{{ url_for(\'main.sponsor\') }}"')
    return text

def balance_style(text):
    # If there is a stray </style> with no opening <style>, inject one at top
    opens = len(re.findall(r"<style\b", text, flags=re.I))
    closes = len(re.findall(r"</style>", text, flags=re.I))
    if closes > opens:
        return "<style>\n" + text
    return text

def fix_back_to_top(text, path):
    if not path.endswith("back_to_top.html"):
        return text
    opens = len(re.findall(r"<button\b", text, flags=re.I))
    closes = len(re.findall(r"</button>", text, flags=re.I))
    if closes < opens:
        text += "\n</button>\n"
    if not text.endswith("\n"):
        text += "\n"
    return text

def process(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        t = f.read()
    orig = t
    t = replace_attrs_block(t)
    t = cond_hx_inline(t)
    t = fix_svg_noise(t)
    t = fix_url_for_mangles(t)
    t = balance_style(t)
    t = fix_back_to_top(t, path)
    if t != orig:
        backup(path)
        with open(path, "w", encoding="utf-8") as f:
            f.write(t)
        return True
    return False

changed = 0
for root, _, files in os.walk(TEMPLATES_DIR):
    for fn in files:
        if not fn.endswith(".html"): 
            continue
        p = os.path.join(root, fn)
        if process(p):
            changed += 1
            print(f"🔧 Patched: {p}")

print(f"✅ Done. Files changed: {changed}")
