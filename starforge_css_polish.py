#!/usr/bin/env python3
"""
starforge_css_polish.py
Auto-fix CSS: kebab-case custom props, remove duplicate imports,
and re-run stylelint for confirmation.
"""

import re
from pathlib import Path
import subprocess

CSS_DIR = Path("app/static/css")

# Regex for custom properties: --SomeThingCamelCase
camel_prop = re.compile(r"--([A-Za-z0-9]+)")

def kebabify(name: str) -> str:
    """Convert camel/Pascal case to kebab-case."""
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name).lower()

def process_file(path: Path):
    text = path.read_text()
    fixed = text

    # Fix custom property casing
    fixed = re.sub(r"--([A-Za-z0-9]+)", lambda m: f"--{kebabify(m.group(1))}", fixed)

    # Remove duplicate @imports (keep first only)
    lines = []
    seen = set()
    for line in fixed.splitlines():
        if line.strip().startswith("@import"):
            if line in seen:
                continue
            seen.add(line)
        lines.append(line)
    fixed = "\n".join(lines)

    if fixed != text:
        path.write_text(fixed)
        print(f"✔ Patched {path}")
    else:
        print(f"✓ No changes {path}")

def main():
    for css_file in CSS_DIR.rglob("*.css"):
        process_file(css_file)

    print("✨ CSS polish done. Running stylelint...")
    subprocess.run([
        "npx", "stylelint",
        "app/static/css/**/*.css",
        "--fix",
        "--config", "stylelint.config.cjs",
        "--ignore-path", ".stylelintignore"
    ])

if __name__ == "__main__":
    main()

