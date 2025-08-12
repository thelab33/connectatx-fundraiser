#!/usr/bin/env python3

import os, re, sys, glob
from collections import Counter, defaultdict
from termcolor import colored

# ========== Forgemaster Report Data ==========
report = []

def print_banner():
    print(colored("⚒️  FundChamps Forgemaster Audit & AutoPatch ⚒️", "yellow", attrs=["bold"]))
    print(colored("Ultra QA/UX mode for pre-launch polish\n", "cyan"))

def add_result(msg, level="info"):
    color = {"info": "cyan", "warn": "yellow", "err": "red", "fix": "green", "success": "green"}[level]
    emoji = {"info": "ℹ️", "warn": "⚠️", "err": "❌", "fix": "🛠️", "success": "✅"}[level]
    print(colored(f"{emoji} {msg}", color))
    report.append((level, msg))

# ========== 1. Duplicate IDs & Attributes ==========
def audit_duplicate_ids():
    files = glob.glob("app/templates/partials/*.html")
    id_counter = defaultdict(list)
    id_pattern = re.compile(r'id="([^"]+)"')
    for fname in files:
        for i, line in enumerate(open(fname), 1):
            for m in id_pattern.finditer(line):
                id_counter[m.group(1)].append((fname, i))
    dups = {k:v for k,v in id_counter.items() if len(v) > 1}
    if dups:
        add_result("Duplicate IDs found:", "warn")
        for idv, occs in dups.items():
            for f, n in occs:
                add_result(f"  {idv} -> {f}:{n}", "err")
    else:
        add_result("No duplicate IDs found!", "success")
    return dups

def fix_duplicate_ids(dups):
    for idv, occs in dups.items():
        for i, (fname, lineno) in enumerate(occs, 1):
            lines = open(fname).readlines()
            lines[lineno-1] = lines[lineno-1].replace(f'id="{idv}"', f'id="{idv}-{i}"')
            open(fname, "w").writelines(lines)
            add_result(f"Auto-fixed: {idv} in {fname}:{lineno}", "fix")

def audit_attrs():
    files = glob.glob("app/templates/partials/*.html")
    attr_pat = re.compile(r'(\w+)="[^"]*"')
    for fname in files:
        for i, line in enumerate(open(fname), 1):
            attrs = [m.group(1) for m in attr_pat.finditer(line)]
            if len(attrs) != len(set(attrs)):
                add_result(f"Duplicate attributes in {fname}:{i}: {line.strip()}", "warn")

# ========== 2. Tailwind CSS Audit ==========
def extract_classes(line):
    # Basic: class="...", ignore {{}} etc
    m = re.search(r'class="([^"]+)"', line)
    return m.group(1).split() if m else []

def audit_tailwind_classes():
    html_files = glob.glob("app/templates/partials/*.html")
    used = set()
    for fname in html_files:
        for line in open(fname):
            used.update([c for c in extract_classes(line) if not c.startswith("{")])
    # Find Tailwind build (assume minified)
    tw_classes = set()
    try:
        css = open("app/static/css/tailwind.min.css").read()
        tw_classes = set(re.findall(r'\.([a-zA-Z0-9:\-\[\]\/]+)\{', css))
    except FileNotFoundError:
        add_result("Tailwind CSS build not found!", "err")
    missing = used - tw_classes
    if missing:
        add_result(f"{len(missing)} Tailwind classes used but missing in CSS!", "warn")
        for cls in sorted(list(missing))[:25]:
            add_result(f"  {cls}", "err")
    else:
        add_result("All Tailwind classes present!", "success")
    # Optional: Auto-safelist logic here
    return missing

def safelist_update(missing):
    # Update tailwind.config.cjs or js with new classes in safelist
    fn = "tailwind.config.cjs"
    safelist_pat = re.compile(r'safelist:\s*\[([^\]]*)\]', re.DOTALL)
    txt = open(fn).read()
    safelist = safelist_pat.search(txt)
    if safelist:
        content = safelist.group(1)
        new = ", ".join([f'"{c}"' for c in missing if c not in content])
        new_txt = safelist_pat.sub(f'safelist: [{content}, {new}]', txt)
        open(fn, "w").write(new_txt)
        add_result("Updated Tailwind safelist!", "fix")

# ========== 3. JS Audit ==========
def js_eslint():
    rc = os.system("npx eslint app/static/js/main.js --max-warnings=0")
    if rc != 0:
        add_result("JS lint errors found! Run 'npx eslint ...' for details.", "warn")
    else:
        add_result("No JS lint errors!", "success")

# ========== 4. Accessibility Audit ==========
def audit_accessibility():
    # Check for missing alt, aria-label, roles
    alt_pat = re.compile(r'<img [^>]*>')
    html_files = glob.glob("app/templates/partials/*.html")
    for fname in html_files:
        for i, line in enumerate(open(fname), 1):
            if "<img" in line and "alt=" not in line:
                add_result(f"Image missing alt in {fname}:{i}", "warn")
            if 'aria-' in line and ('aria-label' not in line and 'aria-labelledby' not in line):
                add_result(f"Element with aria-* missing label in {fname}:{i}", "warn")

# ========== 5. HTML Audit ==========
def htmlhint():
    rc = os.system("npx htmlhint app/templates/partials/*.html")
    if rc != 0:
        add_result("HTMLHint reported issues.", "warn")
    else:
        add_result("No HTMLHint errors!", "success")

# ========== MAIN ==========
if __name__ == "__main__":
    print_banner()
    dups = audit_duplicate_ids()
    if "--fix" in sys.argv and dups:
        fix_duplicate_ids(dups)
    audit_attrs()
    missing = audit_tailwind_classes()
    if "--fix" in sys.argv and missing:
        safelist_update(missing)
    js_eslint()
    audit_accessibility()
    htmlhint()
    add_result("🚀 Forgemaster audit complete!", "success")

