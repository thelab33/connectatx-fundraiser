#!/usr/bin/env python3
"""
starforge_audit.py — FundChamps SaaS Audit/Auto-Fix Tool
  • Summarizes and patches duplicate IDs, attribute bugs, Tailwind class issues
  • Designed for Flask/Jinja2, Tailwind CSS, and high-quality SaaS codebases
  • Usage: python3 starforge_audit.py [--fix]
"""

import re, os, sys, glob, json
from collections import defaultdict, Counter
from pathlib import Path
from termcolor import colored

# ==== SETTINGS ====
TEMPLATES_DIR = 'app/templates/partials/'
CSS_OUTPUT = 'app/static/css/tailwind.min.css'
TAILWIND_CONFIG = 'tailwind.config.js'

# ==== CLI/ENV ====
FIX_MODE = '--fix' in sys.argv

def print_summary(msg, color="cyan"):
    print(colored(msg, color))

def audit_duplicate_ids():
    print_summary("\n[1] Checking for duplicate IDs in HTML/Jinja2...", "yellow")
    ids = Counter()
    file_refs = defaultdict(list)
    for fname in glob.glob(f"{TEMPLATES_DIR}/*.html"):
        with open(fname, encoding='utf-8') as f:
            for lineno, line in enumerate(f, 1):
                for idval in re.findall(r'id="([^"]+)"', line):
                    ids[idval] += 1
                    file_refs[idval].append((fname, lineno))
    dupes = [idv for idv, n in ids.items() if n > 1]
    if not dupes:
        print_summary("✅ No duplicate IDs found!", "green")
    else:
        print_summary(f"⚠️ Duplicate IDs found: {', '.join(dupes)}", "red")
        for idv in dupes:
            for fname, lineno in file_refs[idv]:
                print(f"  {fname}:{lineno}: id=\"{idv}\"")
        if FIX_MODE:
            fix_duplicate_ids(dupes, file_refs)

def fix_duplicate_ids(dupes, file_refs):
    print_summary("🛠️ Attempting to auto-fix duplicate IDs...", "magenta")
    for idv in dupes:
        locations = file_refs[idv]
        for i, (fname, lineno) in enumerate(locations):
            with open(fname, encoding='utf-8') as f:
                lines = f.readlines()
            new_id = f'{idv}-{i+1}'
            lines[lineno-1] = re.sub(rf'id="{idv}"', f'id="{new_id}"', lines[lineno-1])
            with open(fname, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"  → {fname}:{lineno}: changed to id=\"{new_id}\"")
    print_summary("✅ Duplicate IDs auto-patched. Please re-test UI!", "green")

def audit_duplicate_attrs():
    print_summary("\n[2] Scanning for duplicate or conflicting attributes...", "yellow")
    pattern = re.compile(r'(\w+)="[^"]*"\s+\1="[^"]*"')
    for fname in glob.glob(f"{TEMPLATES_DIR}/*.html"):
        with open(fname, encoding='utf-8') as f:
            content = f.read()
            for match in pattern.finditer(content):
                attr = match.group(1)
                print_summary(f"⚠️  {fname}: Duplicate attribute '{attr}' found.", "red")
                if FIX_MODE:
                    # Naive: remove second occurrence (production fix should be smarter)
                    fixed = re.sub(rf'{attr}="([^"]*)"\s+{attr}="([^"]*)"', f'{attr}="\\1"', content)
                    with open(fname, 'w', encoding='utf-8') as f2:
                        f2.write(fixed)
                    print_summary(f"  → Removed duplicate '{attr}' attribute in {fname}", "green")

def audit_tailwind_classes():
    print_summary("\n[3] Auditing used vs. generated Tailwind CSS classes...", "yellow")
    used_classes = set()
    for fname in glob.glob(f"{TEMPLATES_DIR}/*.html"):
        with open(fname, encoding='utf-8') as f:
            for m in re.findall(r'class="([^"]+)"', f.read()):
                used_classes.update([c.strip() for c in m.split() if c.strip()])
    try:
        with open(CSS_OUTPUT, encoding='utf-8') as f:
            css_content = f.read()
    except Exception:
        print_summary(f"❌ Could not read {CSS_OUTPUT} (did you build Tailwind?)", "red")
        return
    missing = []
    for cls in used_classes:
        if cls not in css_content:
            missing.append(cls)
    if not missing:
        print_summary("✅ All used Tailwind classes exist in output CSS.", "green")
    else:
        print_summary(f"⚠️ {len(missing)} classes used but missing in CSS: {', '.join(missing[:12]) + (' ...' if len(missing) > 12 else '')}", "red")
        if FIX_MODE:
            patch_tailwind_safelist(missing)

def patch_tailwind_safelist(missing):
    print_summary("🛠️ Adding missing classes to Tailwind safelist...", "magenta")
    try:
        with open(TAILWIND_CONFIG, encoding='utf-8') as f:
            config = f.read()
        safelist_match = re.search(r'safelist\s*:\s*\[([^\]]*)\]', config)
        if safelist_match:
            before = safelist_match.group(1)
            for cls in missing:
                if f'"{cls}"' not in before:
                    before += f', "{cls}"'
            new_config = re.sub(r'safelist\s*:\s*\[[^\]]*\]', f'safelist: [{before}]', config)
        else:
            # No safelist found, add one
            new_config = re.sub(r'(module\.exports\s*=\s*\{)', r'\1\n  safelist: [\n' + ',\n'.join([f'"{c}"' for c in missing]) + '],', config)
        with open(TAILWIND_CONFIG, 'w', encoding='utf-8') as f:
            f.write(new_config)
        print_summary("✅ Safelist updated. Rebuild your CSS for changes to take effect.", "green")
    except Exception as e:
        print_summary(f"❌ Could not update safelist: {e}", "red")

def main():
    print(colored("⭐ FundChamps Elite Audit — SaaS Edition ⭐\n", "blue", attrs=["bold"]))
    audit_duplicate_ids()
    audit_duplicate_attrs()
    audit_tailwind_classes()
    print_summary("\n🚀 Audit complete! Ready for Demo Day polish!\n", "blue")

if __name__ == "__main__":
    main()
with open("audit-results.log", "a") as f:
    import datetime
    f.write(f"\n--- {datetime.datetime.now()} ---\n")
    f.write("Last audit:\n")
    # (Add any summary text you want here)

