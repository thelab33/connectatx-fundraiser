#!/usr/bin/env python3
import re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "app" / "templates"
BASE_HTML = TEMPLATES / "base.html"
PARTIALS = list((TEMPLATES / "partials").rglob("*.html"))
CSS_OUT = ROOT / "app" / "static" / "css" / "sv_enhancements.css"

ENHANCE_CSS = """/* SV Enhancements — low-specificity helpers */
:root{
  --sf-ease:cubic-bezier(.2,.8,.2,1);
}
.sf-btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;
  border-radius:9999px;font-weight:800;padding:.7rem 1.05rem;transition:transform .25s var(--sf-ease),box-shadow .25s var(--sf-ease),background .25s}
.sf-btn:focus-visible{outline:2px solid var(--fc-brand);outline-offset:2px}
.sf-btn-primary{background:linear-gradient(90deg,var(--fc-brand),color-mix(in srgb,var(--fc-brand) 65%,#fff));color:#0b0c0f;
  box-shadow:0 12px 32px color-mix(in srgb,var(--fc-brand) 26%,transparent)}
.sf-btn-primary:hover{transform:translateY(-1px);box-shadow:0 18px 44px color-mix(in srgb,var(--fc-brand) 36%,transparent)}
.sf-btn-ghost{background:transparent;border:1px solid var(--fc-brand-100);color:#fff}
.sf-btn-ghost:hover{background:var(--fc-brand-50)}
.sf-chip{display:inline-flex;align-items:center;gap:.4rem;border-radius:9999px;padding:.3rem .65rem;
  border:1px dashed var(--fc-brand-100);color:#fde68a;font-weight:700;background:color-mix(in srgb,var(--fc-brand) 8%,transparent)}
.motion-safe .reveal{opacity:0;transform:translateY(8px);transition:opacity .55s var(--sf-ease),transform .55s var(--sf-ease)}
.motion-safe .reveal.is-in{opacity:1;transform:none}
.card:hover{border-color:var(--fc-brand-100)}
/* modest focus for links */
a:focus-visible{outline:2px solid var(--fc-brand);outline-offset:2px}
"""

LINK_TAG = """
    <link rel="stylesheet" href="{{ url_for('static', filename='css/sv_enhancements.css', v=asset_version) }}" />
"""

STYLE_BLOCK_RE = re.compile(r"(<style[^>]*>)(.*?)(</style>)", re.S|re.I)
CLASS_RE = re.compile(r'class=("|\')(.*?)\1', re.S|re.I)

def write_css(dry=False):
  changes=False
  if not CSS_OUT.exists() or CSS_OUT.read_text(encoding="utf-8").strip()!=ENHANCE_CSS.strip():
    changes=True
    if not dry:
      CSS_OUT.parent.mkdir(parents=True, exist_ok=True)
      CSS_OUT.write_text(ENHANCE_CSS, encoding="utf-8")
  return changes, str(CSS_OUT.relative_to(ROOT))

def ensure_link_in_base(dry=False):
  if not BASE_HTML.exists(): return False, "base.html missing"
  html = BASE_HTML.read_text(encoding="utf-8")
  if "css/sv_enhancements.css" in html: return False, "already linked"
  # insert after the Tailwind link or before </head>
  m = re.search(r'(<link[^>]+tailwind[^>]*>)', html, re.I)
  if m:
    new_html = html[:m.end()] + LINK_TAG + html[m.end():]
  else:
    new_html = re.sub(r"</head>", LINK_TAG + "\n  </head>", html, flags=re.I)
  if not dry:
    backup(BASE_HTML)
    BASE_HTML.write_text(new_html, encoding="utf-8")
  return True, "link inserted"

def backup(path: Path):
  bak = path.with_suffix(path.suffix + ".bak")
  if not bak.exists():
    bak.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

def sanitize_style_blocks(text:str)->str:
  def _fix(m):
    head, body, tail = m.groups()
    body = body.replace("{#", "{ /*#*/").replace("#}", "/*#*/ }")
    return f"{head}{body}{tail}"
  return STYLE_BLOCK_RE.sub(_fix, text)

def add_reveal_to_cards(text:str)->str:
  def _add(m):
    quote, classes = m.groups()
    parts = classes.split()
    if ("card" in parts or "glass" in parts) and "reveal" not in parts:
      parts.append("reveal")
    return f'class={quote}{" ".join(dict.fromkeys(parts))}{quote}'
  return CLASS_RE.sub(_add, text)

def upgrade_imgs_links(text:str)->str:
  # lazy/decoding on images (skip fetchpriority=high or data-no-lazy)
  text = re.sub(
    r'<img(?![^>]*\b(fetchpriority|data-no-lazy)\b)([^>]*?)>',
    lambda m: ('<img'+m.group(2)
               + ('' if re.search(r'\bloading=', m.group(2)) else ' loading="lazy"')
               + ('' if re.search(r'\bdecoding=', m.group(2)) else ' decoding="async"')
               + '>'),
    text, flags=re.I)
  # security rel on external links
  def fix_a(m):
    tag = m.group(0)
    if 'rel=' not in tag:
      tag = tag[:-1] + ' rel="noopener noreferrer">'
    return tag
  text = re.sub(r'<a(?=[^>]*\shref=["\']https?://)([^>]*)>', fix_a, text, flags=re.I)
  return text

def gentle_cta_upgrade(text:str)->str:
  # add sf-btn classes to donate/sponsor buttons/links (non-destructive)
  def add_btn_classes(tag):
    if 'sf-btn' in tag: return tag
    # keep existing classes, just append
    return re.sub(r'class=("|\')(.*?)\1',
                  lambda m: f'class={m.group(1)}{m.group(2)} sf-btn sf-btn-primary{m.group(1)}',
                  tag, count=1) if 'class=' in tag else tag.replace('>', ' class="sf-btn sf-btn-primary">')
  text = re.sub(r'<(button|a)([^>]*?(?:>))(?=[^<]*(Donate|Sponsor)(?![a-z]))',
                lambda m: add_btn_classes(m.group(0)),
                text, flags=re.I|re.S)
  return text

def process_file(path: Path, dry=False):
  original = path.read_text(encoding="utf-8")
  text = original
  text = sanitize_style_blocks(text)
  text = add_reveal_to_cards(text)
  text = upgrade_imgs_links(text)
  text = gentle_cta_upgrade(text)
  changed = (text != original)
  if changed and not dry:
    backup(path)
    path.write_text(text, encoding="utf-8")
  return changed

def revert_all():
  changed=[]
  for p in [BASE_HTML, *PARTIALS]:
    bak = p.with_suffix(p.suffix + ".bak")
    if bak.exists():
      p.write_text(bak.read_text(encoding="utf-8"), encoding="utf-8")
      changed.append(str(p.relative_to(ROOT)))
  if CSS_OUT.exists():
    CSS_OUT.unlink()
  return changed

def main():
  cmd = (sys.argv[1] if len(sys.argv)>1 else "dry-run").lower()
  if cmd not in {"dry-run","patch","revert"}:
    print("Usage: python scripts/starforge_autopatch.py [dry-run|patch|revert]"); sys.exit(2)

  if cmd == "revert":
    files = revert_all()
    print(json.dumps({"reverted": files}, indent=2)); return

  dry = (cmd == "dry-run")
  css_changed, css_path = write_css(dry=dry)
  base_changed, base_note = ensure_link_in_base(dry=dry)

  touched=[]
  for path in [*PARTIALS, BASE_HTML]:
    try:
      if process_file(path, dry=dry):
        touched.append(str(path.relative_to(ROOT)))
    except Exception as e:
      print(f"⚠️  skip {path}: {e}")

  report = {
    "mode": "dry-run" if dry else "patched",
    "css": {"path": css_path, "updated": css_changed},
    "base_link": {"changed": base_changed, "note": base_note},
    "files_updated": touched,
  }
  print(json.dumps(report, indent=2))

if __name__ == "__main__":
  main()
