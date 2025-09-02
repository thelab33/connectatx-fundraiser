#!/usr/bin/env python3
"""
starforge_add_theme.py
--------------------------------------------------
CLI tool to append theme-specific CSS blocks
into your Tailwind pipeline.

✨ Enhancements:
- Writes into `themes.css` (imported by input.css), so snippets survive rebuilds.
- Idempotent: won’t duplicate snippets if already present.
- Supports listing all themes and bulk-adding them.
- Pretty logging with ✅/⚠️/✨.

Usage:
    python starforge_add_theme.py legacy
    python starforge_add_theme.py neon
    python starforge_add_theme.py campus
    python starforge_add_theme.py pro
    python starforge_add_theme.py all     # add all themes
    python starforge_add_theme.py list    # list available themes
"""

import sys
from pathlib import Path

CSS_FILE = Path("app/static/css/themes.css")

THEME_SNIPPETS = {
    "legacy": """
/* === FundChamps Theme: LEGACY === */
[data-theme="legacy"] #fc-hero .fc-hero-type {
  font-family: var(--font-legacy, "EB Garamond", serif);
  letter-spacing: -0.01em;
  color: #fdf6e3;
}
""",
    "neon": """
/* === FundChamps Theme: NEON === */
[data-theme="neon"] #fc-hero .fc-hero-cta {
  background: linear-gradient(90deg, #0ff, #f0f);
  color: #000;
  text-shadow: 0 0 8px rgba(255,255,255,.75);
}
""",
    "campus": """
/* === FundChamps Theme: CAMPUS === */
[data-theme="campus"] .fc-hero-brand .txt {
  font-family: "Bebas Neue", sans-serif;
  letter-spacing: .05em;
  text-transform: uppercase;
}
""",
    "pro": """
/* === FundChamps Theme: PRO === */
[data-theme="pro"] #fc-hero .fc-hero-type {
  font-family: "Inter", sans-serif;
  font-weight: 600;
  letter-spacing: -0.015em;
  background: linear-gradient(90deg,#d9d9d9,#f3f3f3);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
[data-theme="pro"] #fc-hero .fc-hero-cta {
  background: #111;
  color: #fff;
  border: 1px solid #000;
  box-shadow: 0 4px 18px rgba(0,0,0,.3);
}
[data-theme="pro"] #fc-hero .fc-hero-cta:hover {
  filter: brightness(1.1);
  text-decoration: underline;
}
"""
}

def add_theme(theme: str, snippet: str):
    CSS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CSS_FILE.exists():
        CSS_FILE.write_text("/* FundChamps Theme Overrides */\n")

    css_content = CSS_FILE.read_text()
    if snippet.strip() in css_content:
        print(f"⚠️  Theme '{theme}' already present in {CSS_FILE}")
        return

    with CSS_FILE.open("a") as f:
        f.write("\n" + snippet.strip() + "\n")

    print(f"✨ Added theme '{theme}' to {CSS_FILE}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python starforge_add_theme.py [legacy|neon|campus|pro|all|list]")
        sys.exit(1)

    arg = sys.argv[1].lower()

    if arg == "list":
        print("🎨 Available themes:")
        for k in THEME_SNIPPETS:
            print(" -", k)
        sys.exit(0)

    if arg == "all":
        for k, v in THEME_SNIPPETS.items():
            add_theme(k, v)
        sys.exit(0)

    if arg not in THEME_SNIPPETS:
        print("❌ Unknown theme. Run `python starforge_add_theme.py list` to see options.")
        sys.exit(1)

    add_theme(arg, THEME_SNIPPETS[arg])

if __name__ == "__main__":
    main()

