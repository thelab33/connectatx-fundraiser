#!/usr/bin/env python3
from __future__ import annotations
import re, sys, glob, pathlib

CSS = r"""
/*[AUTO] Athletic headline theme */
#fc-hero[data-theme="athletic"] .fc-hero-type{
  font-family:"Plus Jakarta Sans","Inter",system-ui,sans-serif;
  text-transform:uppercase; letter-spacing:.02em; line-height:.98;
  font-weight:900;
  font-size:clamp(2rem,1.2rem + 4vw,3.6rem);
  color:transparent;
  background:linear-gradient(180deg,#f8fafc 0%, #fff6bf 55%, #facc15 100%);
  -webkit-background-clip:text; background-clip:text;
  text-shadow:0 2px 0 rgba(0,0,0,.35), 0 22px 40px rgba(0,0,0,.35);
}
#fc-hero[data-theme="athletic"] .fc-hero-copy{
  font-family:"Plus Jakarta Sans","Inter",system-ui,sans-serif;
  font-weight:600; letter-spacing:.005em; color:#eaeaea; opacity:.98; max-width:64ch;
}
#fc-hero[data-theme="athletic"] #hero-heading{ position:relative }
#fc-hero[data-theme="athletic"] #hero-heading::after{
  content:""; position:absolute; left:8%; right:8%; bottom:-.25rem; height:.35rem; border-radius:999px;
  background:linear-gradient(90deg,#fef9c3,#facc15,#f59e0b); opacity:.75;
  filter:drop-shadow(0 6px 12px rgba(250,204,21,.35));
}
""".strip()+"\n"

def find_hero_file() -> pathlib.Path:
    for p in glob.glob("app/templates/**/*.html", recursive=True):
        try:
            t = pathlib.Path(p).read_text(encoding="utf-8")
            if 'id="fc-hero"' in t:
                return pathlib.Path(p)
        except Exception:
            pass
    raise SystemExit("❌ No template with id=\"fc-hero\" found.")

def add_theme_attr(txt: str) -> tuple[str, bool]:
    new = re.sub(r'(<section[^>]*id="fc-hero"(?![^>]*data-theme=))',
                 r'\1 data-theme="athletic"', txt, count=1)
    return new, (new != txt)

def inject_css_in_hero_style(txt: str) -> tuple[str, bool]:
    # Only modify the first <style> block that already targets #fc-hero
    def repl(m):
        head, body, tail = m.group(1), m.group(2), m.group(3)
        return head + body + ("\n" if not body.endswith("\n") else "") + CSS + tail
    new = re.sub(r'(<style[^>]*>)([\s\S]*?#fc-hero[\s\S]*?)(</style>)', repl, txt, count=1, flags=re.I)
    return new, (new != txt)

def main():
    f = find_hero_file()
    txt = f.read_text(encoding="utf-8")

    txt2, themed = add_theme_attr(txt)
    txt3, styled = inject_css_in_hero_style(txt2)

    if not themed and not styled:
        print(f"ℹ️ Already themed: {f}")
        return

    f.write_text(txt3, encoding="utf-8")
    print(f"✨ Enhanced hero in: {f}")
    if themed: print("  • Added data-theme=\"athletic\" on <section id=\"fc-hero\">")
    if styled: print("  • Injected athletic headline CSS inside hero <style>")

if __name__ == "__main__":
    main()

