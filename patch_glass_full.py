
#!/usr/bin/env python3
"""
patch_glass_full.py
--------------------
Makes the hero "glass card" span the *full photo width* (full-bleed)
without moving markup around. It uses a safe, scoped CSS technique
that lets an element inside a centered container bleed to the viewport
width while keeping padding + rounded corners optional.

What it does:
  1) Adds data-glass="full" on <section id="fc-hero"> (toggle)
  2) Injects a scoped CSS block with a clear marker so it's idempotent

Revert:
  --revert : removes the data attribute and the injected CSS block

Usage:
  python patch_glass_full.py path/to/hero_partial.html
  python patch_glass_full.py path/to/hero_partial.html --revert

Notes:
  - Works with Jinja templates; keeps your existing NONCE style block.
  - If no <style nonce="{{ NONCE }}"> is found in the hero section,
    the CSS block is inserted right before </section>.
"""
import sys
import re
from pathlib import Path

MARKER_START = "/* glass-full injected */"
MARKER_END = "/* end glass-full injected */"

CSS_BLOCK = f"""{MARKER_START}
/* Full-bleed glass card inside centered container */
#fc-hero[data-glass="full"] .hero-glass{{
  position: relative;
  left: 50%;
  right: 50%;
  width: 100vw;
  margin-left: calc(-50vw + 50%);
  margin-right: calc(-50vw + 50%);
  border-radius: 0; /* flush to photo edges */
  /* Safe-area + horizontal padding so content isn't edge-to-edge */
  padding-left: max(1rem, env(safe-area-inset-left));
  padding-right: max(1rem, env(safe-area-inset-right));
}}
@media (min-width: 640px){{
  #fc-hero[data-glass="full"] .hero-glass{{ padding-left: 1.25rem; padding-right: 1.25rem; }}
}}
@media (min-width: 1024px){{
  #fc-hero[data-glass="full"] .hero-glass{{ padding-left: 2rem; padding-right: 2rem; }}
}}
/* Optional: keep the parallax image scale looking natural */
#fc-hero[data-glass="full"] #fc-hero-img{{ transform-origin: center top; }}
{MARKER_END}
"""

def inject_attr(text: str) -> str:
  # Add data-glass="full" on the fc-hero section opening tag if missing.
  pattern = re.compile(r'(<section\s+[^>]*id=["\']fc-hero["\'][^>]*)(>)', re.IGNORECASE)
  def repl(m):
    opening = m.group(1)
    if 'data-glass=' not in opening:
      opening = opening.rstrip() + ' data-glass="full"'
    return opening + m.group(2)
  return pattern.sub(repl, text, count=1)

def remove_attr(text: str) -> str:
  # Remove data-glass="..."
  return re.sub(r'(id=["\']fc-hero["\'][^>]*?)\s+data-glass=["\'][^"\']*["\']', r'\1', text, count=1, flags=re.IGNORECASE)

def inject_css(text: str) -> str:
  if MARKER_START in text:
    return text  # already patched
  # Try to insert right after the local scoped style block inside hero
  style_anchor = re.search(r'(<style\s+[^>]*nonce=\{\{\s*NONCE\s*\}\}[^>]*\>)(.*?)</style>', text, flags=re.DOTALL|re.IGNORECASE)
  if style_anchor:
    start = style_anchor.end(1)
    return text[:start] + "\n" + CSS_BLOCK + text[start:]
  # Fallback: insert before </section> of the hero
  return re.sub(r'(</section>\s*)$', "\n<style nonce=\"{{ NONCE }}\">\n" + CSS_BLOCK + "\n</style>\n\\1", text, count=1, flags=re.IGNORECASE)

def remove_css(text: str) -> str:
  # Strip our marked CSS block (whether inside a style or standalone)
  pattern = re.compile(re.escape(MARKER_START) + r'.*?' + re.escape(MARKER_END), re.DOTALL)
  return pattern.sub('', text)

def main():
  if len(sys.argv) < 2:
    print("Usage: python patch_glass_full.py <path-to-hero-partial.html> [--revert]")
    sys.exit(1)
  path = Path(sys.argv[1])
  if not path.exists():
    print(f"ERROR: File not found: {path}")
    sys.exit(2)
  revert = ('--revert' in sys.argv[2:])
  src = path.read_text(encoding='utf-8')

  if revert:
    out = remove_css(remove_attr(src))
    if out != src:
      path.write_text(out, encoding='utf-8')
      print("Reverted: removed data-glass and injected CSS block.")
    else:
      print("No changes found to revert.")
    return

  # Apply patch
  out = inject_css(inject_attr(src))
  if out != src:
    path.write_text(out, encoding='utf-8')
    print('Patched: hero glass will now full-bleed across the photo (data-glass="full").')
  else:
    print('Already patched — nothing to do.')

if __name__ == "__main__":
  main()

