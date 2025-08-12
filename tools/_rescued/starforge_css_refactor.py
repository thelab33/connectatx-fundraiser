#!/usr/bin/env python3
"""
starforge_css_refactor.py
Elite SaaS CSS Audit & Merge Script 🚀

- Merge variables.css into globals.css (:root only, dedupes)
- Move all @keyframes & custom utility classes from elevated.css/variables.css to luxury.css (dedupes)
- Delete all .bak* files
- Prints final, recommended HTML <link> order

Angel, you deserve *founder-grade* CSS workflows.
"""

import os
import re
from shutil import copyfile

# === 1. Setup Paths ===
CSS_DIR = os.path.abspath(os.path.dirname(__file__))
FILES = {
    "globals": "globals.css",
    "luxury": "luxury.css",
    "variables": "variables.css",
    "elevated": "elevated.css",
}
BACKUP_SUFFIX = ".starforgebak"

# === 2. Helper: Backup originals ===
def backup(filename):
    if os.path.exists(filename):
        copyfile(filename, filename + BACKUP_SUFFIX)
        print(f"🔒 Backed up {filename} → {filename + BACKUP_SUFFIX}")

# === 3. Merge variables.css → globals.css :root ===
def merge_variables_into_globals():
    varfile = FILES["variables"]
    globfile = FILES["globals"]
    if not os.path.exists(varfile):
        print("No variables.css found. Skipping merge.")
        return

    with open(varfile) as f:
        vars_css = f.read()
    var_block = re.findall(r":root\s*{([^}]*)}", vars_css, re.DOTALL)
    var_block = var_block[0] if var_block else vars_css

    backup(globfile)
    with open(globfile, encoding="utf-8") as f:
        glob_css = f.read()

    # Find or add :root in globals.css
    if ":root" in glob_css:
        glob_css_new = re.sub(
            r"(:root\s*{)([^}]*)}",
            lambda m: f"{m.group(1)}\n" + _dedupe_vars(
                m.group(2) + "\n" + var_block
            ) + "}", glob_css, flags=re.DOTALL)
    else:
        # Insert at top
        glob_css_new = f":root {{{var_block}}}\n\n{glob_css}"

    with open(globfile, "w", encoding="utf-8") as f:
        f.write(glob_css_new)
    print("✅ Merged variables.css into globals.css :root block.")

def _dedupe_vars(css_vars):
    # Deduplicate CSS variable definitions, keeping last (so user-defined in variables.css wins)
    lines = [l.strip() for l in css_vars.split("\n") if l.strip()]
    var_map = {}
    for line in lines:
        if ":" in line and "--" in line:
            k, v = line.split(":", 1)
            var_map[k.strip()] = v.strip().rstrip(";")
    return "\n  ".join(f"{k}: {v};" for k, v in var_map.items())

# === 4. Merge all @keyframes and utility classes into luxury.css ===
def merge_utilities_and_keyframes():
    luxury_path = FILES["luxury"]
    sources = [FILES["elevated"], FILES["variables"]]
    all_keyframes = set()
    all_util_classes = []

    for src in sources:
        if not os.path.exists(src):
            continue
        with open(src, encoding="utf-8") as f:
            css = f.read()
        keyframes = re.findall(r"@keyframes\s+[^{]+\{[^}]+\}", css, re.DOTALL)
        all_keyframes.update([kf.strip() for kf in keyframes])
        util_classes = re.findall(
            r"\.([a-zA-Z0-9\-\_]+)\s*{[^}]+}", css, re.DOTALL)
        for match in util_classes:
            # Only keep .animate-, .badge-, .shadow- classes, or anything custom (define your patterns here)
            if match.startswith(("animate-", "badge-", "shadow-", "pop", "pulse", "slide", "fade")):
                class_block = re.search(rf"\.{re.escape(match)}\s*{{[^}}]+}}", css)
                if class_block:
                    all_util_classes.append(class_block.group(0).strip())

    # Read luxury.css, append any missing
    backup(luxury_path)
    with open(luxury_path, encoding="utf-8") as f:
        luxury_css = f.read()

    # Add missing keyframes
    for kf in all_keyframes:
        if kf not in luxury_css:
            luxury_css += "\n\n" + kf
    # Add missing classes
    for cls in all_util_classes:
        if cls not in luxury_css:
            luxury_css += "\n\n" + cls

    with open(luxury_path, "w", encoding="utf-8") as f:
        f.write(luxury_css)
    print("✅ Merged keyframes and custom utility classes into luxury.css.")

# === 5. Delete .bak* files and variables.css ===
def cleanup_bak_and_unused():
    deleted = 0
    for fname in os.listdir(CSS_DIR):
        if fname.startswith("globals.css.bak") or fname.endswith(BACKUP_SUFFIX):
            os.remove(os.path.join(CSS_DIR, fname))
            deleted += 1
    if os.path.exists(FILES["variables"]):
        os.remove(FILES["variables"])
        print("🗑️  Deleted variables.css after merge.")
    print(f"🧹 Cleaned up {deleted} old backup files.")

# === 6. Output final <link> order for your base template ===
def print_final_order():
    print("\n🔗 SaaS CSS Import Order (in base.html):\n")
    print("""<link rel="stylesheet" href="{{ url_for('static', filename='css/tailwind.min.css') }}" />
<link rel="stylesheet" href="{{ url_for('static', filename='css/globals.css') }}" />
<link rel="stylesheet" href="{{ url_for('static', filename='css/luxury.css') }}" />""")

# === Main entry ===
if __name__ == "__main__":
    print("🌟 STARFORGE CSS ELITE UPGRADE: START 🌟\n")
    merge_variables_into_globals()
    merge_utilities_and_keyframes()
    cleanup_bak_and_unused()
    print_final_order()
    print("\n🚀 All done! Your SaaS CSS stack is founder-grade and ready for liftoff.\n")
